"""
Module with main to run sequence file processing chain
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.utils.logging import configure_logging
from hypernets_processor.utils.paths import parse_sequence_path
from hypernets_processor.context import Context
from hypernets_processor.sequence_processor import SequenceProcessor
import os
import traceback
import cProfile,pstats

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

    if parse_sequence_path(context.get_config_value("raw_data_directory")) is not None:
        raw_paths.append(context.get_config_value("raw_data_directory"))
    else:
        for path in os.listdir(context.get_config_value("raw_data_directory")):
            if parse_sequence_path(path) is not None:
                raw_paths.append(
                    os.path.join(context.get_config_value("raw_data_directory"), path)
                )

    # If adding to archive, remove previously processed paths from list by referencing
    # archive db
    print("here")

    if to_archive is True:
        processed_products = [
            product["sequence_name"]
            for product in context.archive_db["products"].find(
                site_id=context.get_config_value("site_id")
            )
        ]

        failed_products = [
            anomaly["sequence_name"]
            for anomaly in context.anomaly_db["anomalies"].find(
                site_id=context.get_config_value("site_id")
            )
        ]
        print("here2")
        complete_products = processed_products + failed_products

        directory = os.path.dirname(raw_paths[0])

        raw_products = [os.path.basename(raw_path) for raw_path in raw_paths]
        raw_products = list(set(raw_products) - set(complete_products))
        raw_paths = [
            os.path.join(directory, raw_product) for raw_product in raw_products
        ]

    return raw_paths


def main(processor_config, job_config, to_archive):
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

    print("here3")

    # Define context
    context = Context(
        processor_config=processor_config, job_config=job_config, logger=logger
    )

    context.set_config_value("to_archive", to_archive)
    # Determine target sequences
    target_sequences = get_target_sequences(context, to_archive)

    print("here3")
    # Run processor
    sp = SequenceProcessor(context=context)
    target_sequences_passed = 0
    target_sequences_total = len(target_sequences)
    print("here4")

    if target_sequences_total == 0:
        msg = "No sequences to process"

    else:
        for target_sequence in target_sequences:
            print("here5")

            context.logger.info("Processing sequence: " + target_sequence)

            try:
                # profiler = cProfile.Profile()
                # profiler.enable()
                sp.process_sequence(target_sequence)
                # profiler.disable()
                # stats = pstats.Stats(profiler).sort_stats('tottime')
                # stats.print_stats(100)
                target_sequences_passed += 1

                if context.anomaly_handler.anomalies_added is not []:
                    context.logger.info("Processing Anomalies: " + str(context.anomaly_handler.anomalies_added))

                context.logger.info("Complete")
            except Exception as e:

                context.anomaly_handler.add_x_anomaly()
                if context.anomaly_handler.anomalies_added is not []:
                    context.logger.info("Processing Anomalies: " + str(context.anomaly_handler.anomalies_added))

                logger.error("Failed: " + repr(e))
                logger.info(traceback.format_exc())

        msg = str(target_sequences_passed) + "/" + str(target_sequences_total) + \
              " sequences successfully processed"

    return msg


if __name__ == "__main__":
    pass
