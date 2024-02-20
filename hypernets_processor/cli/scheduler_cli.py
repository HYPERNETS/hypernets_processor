"""
cli for job scheduler
"""

from hypernets_processor.version import __version__
from hypernets_processor.main.scheduler_main import main
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.utils.config import (
    SCHEDULER_CONFIG_PATH,
    PROCESSOR_CONFIG_PATH,
)
import argparse


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "31/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def configure_parser():
    """
    Configure parser

    :return: parser
    :rtype: argparse.ArgumentParser
    """

    description = (
        "Tool for scheduling automatic processing of Hypernets "
        "Land and Water Network hyperspectral field data"
    )

    # Initialise argument parser
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface function for scheduler_main
    """

    scheduler_config = read_config_file(SCHEDULER_CONFIG_PATH)
    processor_config = read_config_file(PROCESSOR_CONFIG_PATH)

    # run main
    main(scheduler_config=scheduler_config, processor_config=processor_config)

    return None


if __name__ == "__main__":
    cli()
