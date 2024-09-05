"""
Module with main to run sequence file processing chain
"""
import datetime

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.utils.logging import configure_logging
from hypernets_processor.utils.paths import parse_sequence_path
from hypernets_processor.context import Context
from hypernets_processor.sequence_processor import SequenceProcessor
import os
import traceback
import cProfile, pstats
from itertools import repeat
import numpy as np
from multiprocessing import Pool
import gc
import glob

"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "21/10/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def get_target_sequences(context, to_archive):
    """
    Returns paths of sequences to process, checking against previous archived data if
    adding to archive

    :type context: hypernets_processor.context.Context
    :param context: processor context

    :type to_archive: bool
    :param to_archive: switch for if to add processed data to data archive
    """

    # Find potential sequence paths to process
    # raw_data_directory may either be a sequence path or directory of sequence paths

    raw_paths = []
    incomplete_downloads = []

    if parse_sequence_path(context.get_config_value("raw_data_directory")) is not None:
        raw_paths.append(context.get_config_value("raw_data_directory"))
    else:
        #first add SEQ paths in raw_data_directory
        paths=os.listdir(context.get_config_value("raw_data_directory"))
        #then add paths in raw_data_directory/YYYY/mm/DD/SEQ*
        paths.extend(glob.glob(
                os.path.join(context.get_config_value("raw_data_directory"), "20*","*","*","SEQ*")
            ))

        for path in paths:
            if parse_sequence_path(path, context) is not None:
                sequence_path = os.path.join(context.get_config_value("raw_data_directory"), path)
                if os.path.exists(os.path.join(sequence_path, "metadata.txt")):
                    raw_paths.append(sequence_path)
                else:
                    incomplete_downloads.append(sequence_path)

    # If adding to archive, remove previously processed paths from list by referencing
    # archive db
    if to_archive is True:
        if context.archive_db is None:
            raise ValueError("archive db has not been set!")

        processed_products = [
            product["sequence_name"]
            for product in context.archive_db["products"].find(
                site_id=context.get_config_value("site_id")
            )
            if "L2A" in product["product_level"]
        ]

        failed_products = [
            anomaly["sequence_name"]
            for anomaly in context.anomaly_db["anomalies"].find(
                site_id=context.get_config_value("site_id")
            )
            if anomaly["anomaly_id"] != "m"
        ]

        complete_products = processed_products + failed_products

        raw_products = [os.path.basename(raw_path) for raw_path in raw_paths]
        raw_products = list(set(raw_products) - set(complete_products))

        paths_to_process = []
        for i in range(len(raw_paths)):
            raw_product = os.path.basename(raw_paths[i])
            raw_product_datetime = parse_sequence_path(raw_product)["datetime"]
            if raw_product in raw_products:
                if context.get_config_value("delay_hours") is not None and np.abs(
                        raw_product_datetime - datetime.datetime.now()) < datetime.timedelta(
                        hours=context.get_config_value("delay_hours")):
                    print("%s is not processed yet due to not having reached required delay (%s hours)" % (
                    raw_product, context.get_config_value("delay_hours")))
                else:
                    paths_to_process.append(raw_paths[i])

        #next, check if incompete downloads have already been added to anomaly db, and if not add them
        incomplete_products = [
            anomaly["sequence_name"]
            for anomaly in context.anomaly_db["anomalies"].find(
                site_id=context.get_config_value("site_id")
            )
            if anomaly["anomaly_id"] == "m"
        ]

        for incomplete_download_path in incomplete_downloads:
            seq_id = os.path.basename(incomplete_download_path)
            if not seq_id in incomplete_products:
                context.set_config_value("time", parse_sequence_path(incomplete_download_path)["datetime"])
                context.set_config_value("sequence_name", seq_id)
                context.set_config_value("sequence_path", incomplete_download_path)
                context.logger.error(
                    "metadata.txt not found in directory %s, will try processing again later" % (incomplete_download_path))
                context.anomaly_handler.anomaly_db.add_anomaly("m")

        return paths_to_process
    else:
        return raw_paths

def run_sequence(inputs):
    target_sequence, context, logger = inputs
    sp = SequenceProcessor(context=context)
    context.logger.info("Processing sequence: " + target_sequence)
    try:
        # profiler = cProfile.Profile()
        # profiler.enable()
        sp.process_sequence(target_sequence)
        # profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats('tottime')
        # stats.print_stats(100)
        if context.anomaly_handler.anomalies_added is not []:
            context.logger.info(
                "Processing Anomalies: " + str(context.anomaly_handler.anomalies_added)
            )

        context.logger.info(target_sequence + " Complete")
        del sp
        gc.collect()
        return 1

    except Exception as e:

        context.anomaly_handler.add_x_anomaly()
        if context.anomaly_handler.anomalies_added is not []:
            context.logger.info(
                "Processing Anomalies: " + str(context.anomaly_handler.anomalies_added)
            )

        logger.error(target_sequence + "Failed: " + repr(e))
        logger.info(traceback.format_exc())
        del sp
        gc.collect()
        return 0


def main(processor_config, job_config, to_archive, parallel=None):
    """
    Main function to run processing chain for sequence files

    :type processor_config: configparser.RawConfigParser
    :param processor_config: processor configuration file path

    :type job_config: configparser.RawConfigParser
    :param job_config: job configuration file path

    :type to_archive: bool
    :param to_archive: switch for if to add processed data to data archive
    """
    # Configure logging
    name = __name__
    if "job_name" in job_config["Job"].keys():
        name = job_config["Job"]["job_name"]

    logger = configure_logging(config=job_config, name=name)

    # Define context
    context = Context(
        processor_config=processor_config, job_config=job_config, logger=logger
    )

    context.set_config_value("to_archive", to_archive)
    # Determine target sequences
    target_sequences = get_target_sequences(context, to_archive)

    # Run processor
    target_sequences_total = len(target_sequences)

    if target_sequences_total == 0:
        msg = "No sequences to process"

    else:
        success = np.zeros_like(target_sequences, dtype=int)

        for i, target_sequence in enumerate(target_sequences):
            success[i] = run_sequence((target_sequence, context, logger))

        msg = (
            str(np.sum(success))
            + "/"
            + str(target_sequences_total)
            + " sequences successfully processed"
        )

    return msg


if __name__ == "__main__":
    pass
