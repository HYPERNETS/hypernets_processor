"""
scheduler for hypernets_processor jobs cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.hypernets_scheduler_main import main
from hypernets_processor.cli.common import read_jobs_list, read_config_file
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

    # Add specific arguments
    # Configuration files
    parser.add_argument("-s", "--scheduler-config", action="store",
                        help="Path of scheduler configuration file")

    parser.add_argument("-p", "--processor-config", action="store",
                        help="Path of processor configuration file")

    parser.add_argument("-l", "--jobs-list", action="store",
                        help="Path of jobs list")

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface function for hypernets_scheduler_main
    """

    # unpack parsed_args
    jobs_list = read_jobs_list(parsed_args.l)
    processor_config = read_config_file(parsed_args.p)
    scheduler_config = read_config_file(parsed_args.s)

    # run main
    main(jobs_list=jobs_list,
         processor_config=processor_config,
         scheduler_config=scheduler_config)

    return None


if __name__ == "__main__":
    pass
