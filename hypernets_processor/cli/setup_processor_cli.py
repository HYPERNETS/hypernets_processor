"""
scheduler for hypernets_processor jobs cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.setup_processor_main import main
from hypernets_processor.cli.common import cli_input_yn, cli_input_str_default, PROCESSOR_CONFIG_PATH, read_config_file, determine_set_value, determine_if_set
import argparse
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
    Command line interface function for hypernets_scheduler_main
    """

    processor_config = read_config_file(PROCESSOR_CONFIG_PATH)
    context = Context(processor_config)

    # Determine archive directory to set
    archive_directory = determine_set_value("archive_directory", context, return_existing=True)

    working_directory = determine_set_value(
        "processor_working_directory",
        context,
        default="./.hypernets",
        return_existing=True
    )

    set_mdb = determine_if_set("metadata_db_url", context)
    mdb_path = None
    if set_mdb:
        old_mdb = cli_input_yn("use existing metadata database", default=False)
        if old_mdb:
            mdb_path = cli_input_str_default("enter metadata database url")

    set_adb = determine_if_set("anomoly_db_url", context)
    adb_path = None
    if set_adb:
        old_adb = cli_input_yn("use existing anomoly database", default=False)
        if old_adb:
            adb_path = cli_input_str_default("enter anomoly database url")

    main(
        working_directory=working_directory,
        mdb_path=mdb_path,
        set_mdb=set_mdb,
        adb_path=adb_path,
        set_adb=set_adb,
        archive_directory=archive_directory
    )

    return None


if __name__ == "__main__":
    cli()
