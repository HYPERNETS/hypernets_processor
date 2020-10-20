"""
job init cli
"""

from hypernets_processor.version import __version__
import argparse
from hypernets_processor.main.init_job_main import main


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "20/10/2020"
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

    description = "Tool for initialising hypernets_processor jobs"

    # Initialise argument parser
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface for job init
    """

    pass


if __name__ == "__main__":
    pass
