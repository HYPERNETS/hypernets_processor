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

    parser.add_argument("-n", "--job-name", action="store", required=True,
                        help="Job name")

    parser.add_argument("-w", "--job-working-directory", action="store", required=True,
                        help="Working directory of job (will write config here)")

    parser.add_argument("-i", "--raw-data-directory", action="store", required=True,
                        help="Directory of input data")

    parser.add_argument("--add-to-scheduler", action="store_true",
                        help="Option to add job to automatically hypernets_scheduler jobs")

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface for job init
    """

    settings = dict()
    settings["job_name"] = parsed_args.job_name
    settings["job_working_directory"] = parsed_args.job_working_directory
    settings["raw_data_directory"] = parsed_args.raw_data_directory
    settings["add_to_scheduler"] = parsed_args.add_to_scheduler

    main(settings)


if __name__ == "__main__":
    pass
