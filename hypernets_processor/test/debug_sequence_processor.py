"""
hypernets_processor cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import (
    PROCESSOR_CONFIG_PATH,
    JOB_CONFIG_TEMPLATE_PATH,
    PROCESSOR_WATER_DEFAULTS_CONFIG_PATH,
    PROCESSOR_LAND_DEFAULTS_CONFIG_PATH,
    PROCESSOR_DEFAULT_CONFIG_PATH,
)
from hypernets_processor.utils.cli import configure_std_parser
from hypernets_processor.utils.config import read_config_file, get_config_value
from hypernets_processor.main.sequence_processor_main import main
import os


"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "29/3/2023"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


def process_sequence():
    """
    Command line interface to sequence_processor_main for ad-hoc job processing
    """

    # network = "water"
    network = "land"

    job_config_path = JOB_CONFIG_TEMPLATE_PATH
    print(job_config_path)

    # Select appropriate processor defaults
    if network in ["land", "l"]:
        processor_defaults = PROCESSOR_LAND_DEFAULTS_CONFIG_PATH
    elif network in ["water", "w"]:
        processor_defaults = PROCESSOR_WATER_DEFAULTS_CONFIG_PATH
        print(processor_defaults)
    else:
        raise ValueError("Invalid network name - " + network)

    # Read config file
    job_config = read_config_file([job_config_path, processor_defaults])

    job_config["Input"][
        "raw_data_directory"
    ] = r"C:\Users\pdv\data\insitu\hypernets\raw_data\GHNA\DATA\SEQ20231008T150035"

    # job_config["Input"][
    #     "raw_data_directory"
    # ] = r"C:\Users\pdv\OneDrive - National Physical Laboratory\Desktop\GONA_data\raw_data\GONA\SEQ20220829T153127"

    job_config["Output"][
        "archive_directory"
    ] = r"C:\Users\pdv\data\insitu\hypernets\archive_test"

    job_config["Processor"]["max_level"] = "L2A"

    no_unc = False

    if no_unc:
        job_config["Processor"]["mcsteps"] = "0"
        job_config["Output"]["plot_uncertainty"] = "False"
        job_config["Output"]["plot_correlation"] = "False"

    # run main
    processor_config = read_config_file(PROCESSOR_DEFAULT_CONFIG_PATH)
    main(processor_config=processor_config, job_config=job_config, to_archive=False)

    return None


if __name__ == "__main__":
    process_sequence()
