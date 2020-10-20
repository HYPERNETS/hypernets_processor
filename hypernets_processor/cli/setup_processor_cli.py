"""
hypernets_processor setup cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.setup_processor_main import main
from hypernets_processor.cli.common import cli_input_yn, PROCESSOR_CONFIG_PATH, read_config_file, determine_set_value
import argparse
import os
from hypernets_processor.context import Context


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "24/9/2020"
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

    description = "Tool for setting up hypernets_processor"

    # Initialise argument parser
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface for hypernets_processor setup
    """

    processor_config = read_config_file(PROCESSOR_CONFIG_PATH)
    context = Context(processor_config)

    settings = dict()

    # Determine network
    settings["network"] = determine_set_value(
        "network",
        context,
        options=["land", "water"],
        return_existing=True
    )
    settings["network_defaults"] = cli_input_yn("set network default config values (overwrites existing)")

    # Determine archive directory to set
    settings["archive_directory"] = os.path.abspath(
        determine_set_value(
            "archive_directory",
            context,
            return_existing=True
        )
    )

    home_directory = os.path.expanduser("~")
    settings["working_directory"] = os.path.abspath(
        determine_set_value(
            "processor_working_directory",
            context,
            default=os.path.join(home_directory, ".hypernets"),
            return_existing=True
        )
    )

    dbs = ["metadata", "anomoly"]
    for db in dbs:
        settings[db + "_db_url"] = determine_set_value(
                db+"_db_url",
                context,
                default="sqlite:///"+os.path.join(settings["working_directory"], db+".db"),
            )

    settings["log_path"] = os.path.join(settings["working_directory"], "processor.log")

    main(settings)


if __name__ == "__main__":
    pass
