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


"""___Authorship___"""
__author__ = "Sam Hunr"
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

    if to_archive:
        processed_products = [
            product["raw_product_name"]
            for product in context.archive_db["products"].find(
                site=context.get_config_value("site")
            )
        ]

        directory = os.path.dirname(raw_paths[0])

        raw_products = [os.path.basename(raw_path) for raw_path in raw_paths]
        raw_products = list(set(raw_products) - set(processed_products))
        raw_paths = [
            os.path.join(directory, raw_product) for raw_product in raw_products
        ]

    return raw_paths


def main(processor_config_path, job_config_path, to_archive):
    """
    Main function to run processing chain for sequence files

    :type processor_config_path: str
    :param processor_config_path: processor configuration file path

    :type job_config_path: str
    :param job_config_path: job configuration file path

    :type to_archive: bool
    :param to_archive: switch for if to add processed data to data archive
    """

    processor_config = read_config_file(processor_config_path)
    job_config = read_config_file(job_config_path)

    # Configure logging
    logger = configure_logging(config=job_config)

    # Define context
    context = Context(
        processor_config=processor_config, job_config=job_config, logger=logger
    )
    context.set_config_value("to_archive", to_archive)

    # Determine target sequences
    target_sequences = get_target_sequences(context, to_archive)

    # Run processor
    sp = SequenceProcessor(context=context)

    for target_sequence in target_sequences:
        sp.process_sequence(target_sequence)

    return None


if __name__ == "__main__":
    pass
