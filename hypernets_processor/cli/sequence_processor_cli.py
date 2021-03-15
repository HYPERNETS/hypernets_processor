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
from hypernets_processor.utils.config import read_config_file, get_config_value
from hypernets_processor.main.sequence_processor_main import main
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
    parser.add_argument("-ml","--max-level",action="store",choices=["L0","L1A","L1B","L1C","L2A"],
                        help="Only process the data to the specified level.")
    # parser.add_argument("--plot", action="store_true",
    #                     help="Generate plots of processed data")
    parser.add_argument("--write-all",action="store_true",
                        help="Write all products at intermediate data processing levels before final product")
    parser.add_argument("--no-unc",action="store_true",
                        help="Do not include uncertainty propagation")
    parser.add_argument("-j", "--job-config", action="store",
                        help="Job configuration file path. May be used to specify job instead of/along with commandline"
                             "arguments (any fields in both job configuration file overwritten by commandline "
                             "arguments)")
    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface to sequence_processor_main for ad-hoc job processing
    """

    network = "land"

    # If job config specified use
    if parsed_args.job_config:
        job_config_path = parsed_args.job_config

        job_config = read_config_file(job_config_path)
        network = get_config_value(job_config, "Job", "network").lower()
        del job_config

    # Else start with template job config
    else:
        job_config_path = JOB_CONFIG_TEMPLATE_PATH

    # Check if network defined in args and overwrite
    if parsed_args.network is not None:
        network = parsed_args.network

    # Select appropriate processor defaults
    if network in ["land", "l"]:
        processor_defaults = PROCESSOR_LAND_DEFAULTS_CONFIG_PATH
    elif network in ["water", "w"]:
        processor_defaults = PROCESSOR_WATER_DEFAULTS_CONFIG_PATH
    else:
        raise ValueError("Invalid network name - " + network)

    # Read config file
    job_config = read_config_file([job_config_path, processor_defaults])

    # Overwrite config values with any args from commandline
    if parsed_args.input_directory is not None:
        job_config["Input"]["raw_data_directory"] = os.path.abspath(parsed_args.input_directory)

    if parsed_args.output_directory is not None:
        job_config["Output"]["archive_directory"] = os.path.abspath(parsed_args.output_directory)

    if parsed_args.max_level is not None:
        job_config["Processor"]["max_level"] = parsed_args.max_level

    if parsed_args.write_all:
        for key in job_config["Output"].keys():
            if key[:5] == "write":
                job_config["Output"][key] = "True"

    if parsed_args.no_unc:
        job_config["Processor"]["mcsteps"] = "0"
        job_config["Output"]["plot_uncertainty"] = "False"
        job_config["Output"]["plot_correlation"] = "False"

    if parsed_args.log is not None:
        job_config["Log"]["log_path"] = os.path.abspath(parsed_args.log)

    if parsed_args.verbose is not None:
        job_config["Log"]["verbose"] = str(parsed_args.verbose)

    if parsed_args.verbose is not None:
        job_config["Log"]["quiet"] = str(parsed_args.quiet)

    # run main
    processor_config = read_config_file(PROCESSOR_CONFIG_PATH)
    main(processor_config=processor_config, job_config=job_config, to_archive=False)

    return None


if __name__ == "__main__":
    pass
