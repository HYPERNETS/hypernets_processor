"""
scheduler for hypernets_processor jobs cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.hypernets_scheduler_main import main
from hypernets_processor.utils.config import SCHEDULER_CONFIG_PATH
import argparse


'''___Authorship___'''
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

    description = "Tool for scheduling automatic processing of Hypernets " \
                  "Land and Water Network hyperspectral field data"

    # Initialise argument parser
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface function for hypernets_scheduler_main
    """

    # run main
    main(scheduler_config_path=SCHEDULER_CONFIG_PATH)

    return None


if __name__ == "__main__":
    pass
