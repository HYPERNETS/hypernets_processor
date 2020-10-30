"""
hypernets_processor cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import (
    PROCESSOR_CONFIG_PATH,
    JOB_CONFIG_TEMPLATE_PATH,
    PROCESSOR_WATER_DEFAULTS_CONFIG_PATH,
    PROCESSOR_LAND_DEFAULTS_CONFIG_PATH
)
from hypernets_processor.utils.cli import configure_std_parser
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.main.sequence_processor_main import main
from datetime import datetime as dt
import sys
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
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

    description = "Tool for processing Hypernets Land and Water Network hyperspectral field data"

    # Create standard parser
    parser = configure_std_parser(description=description)

    # Add specific arguments
    parser.add_argument("-i", "--input-directory", action="store",
                        help="Directory of input data")
    parser.add_argument("-o", "--output-directory", action="store",
                        help="Directory to write output data to")
    parser.add_argument("-n", "--network", action="store", choices=["land", "water"],
                        help="Network to process file for")
    # parser.add_argument("--plot", action="store_true",
    #                     help="Generate plots of processed data")
    parser.add_argument("--write-all", action="store_true",
                        help="Write all products at intermediate data processing levels before final product")
    parser.add_argument("-j", "--job-config", action="store",
                        help="Use instead of above arguments to specify job with configuration file")
    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


if parsed_args.job_config and (
        parsed_args.input_directory or parsed_args.output_directory
        or parsed_args.network or parsed_args.write_all
):
    print("-j is mutually exclusive with other input arguments")
    sys.exit(2)


def cli():
    """
    Command line interface to sequence_processor_main for ad-hoc job processing
    """

    # If job config specified use
    if parsed_args.job_config:
        tmp_job = False
        job_config_path = parsed_args.job_config

    # Else build and write temporary job config from command line arguments
    else:
        tmp_job = True

        processor_defaults = PROCESSOR_WATER_DEFAULTS_CONFIG_PATH
        if parsed_args.network == "land":
            processor_defaults = PROCESSOR_LAND_DEFAULTS_CONFIG_PATH

        job_config = read_config_file([JOB_CONFIG_TEMPLATE_PATH, processor_defaults])
        if parsed_args.input_directory is not None:
            job_config["Input"]["raw_data_directory"] = os.path.abspath(parsed_args.input_directory)
        else:
            print("-i required")
            sys.exit(2)

        if parsed_args.output_directory is not None:
            job_config["Output"]["archive_directory"] = os.path.abspath(parsed_args.output_directory)
        else:
            print("-o required")
            sys.exit(2)

        if parsed_args.write_all:
            for key in job_config["Output"].keys():
                if key[:5] == "write":
                    job_config["Output"][key] = "True"

        job_config["Log"]["log_path"] = os.path.abspath(parsed_args.log) if parsed_args.log is not None else ""
        job_config["Log"]["verbose"] = str(parsed_args.verbose) if parsed_args.verbose is not None else ""
        job_config["Log"]["quiet"] = str(parsed_args.quiet) if parsed_args.verbose is not None else ""

        job_config["Job"]["job_name"] = "run_" + dt.now().strftime("%Y%m%dT%H%M%S")
        home_directory = os.path.expanduser("~")
        job_config["Job"]["job_working_directory"] = os.path.join(home_directory, ".hypernets", "tmp")
        job_config_path = os.path.join(
            job_config["Job"]["job_working_directory"],
            job_config["Job"]["job_name"] + ".config"
        )
        os.makedirs(job_config["Job"]["job_working_directory"], exist_ok=True)
        with open(job_config_path, "w") as f:
            job_config.write(f)

    # run main
    main(processor_config_path=PROCESSOR_CONFIG_PATH, job_config_path=job_config_path, to_archive=False)

    if tmp_job:
        os.remove(job_config_path)

    return None


if __name__ == "__main__":
    pass
