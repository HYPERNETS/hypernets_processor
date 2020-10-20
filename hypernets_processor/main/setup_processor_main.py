"""
Main function to setup processor on install
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import (
    read_config_file,
    PROCESSOR_CONFIG_PATH,
    PROCESSOR_LAND_DEFAULTS_CONFIG_PATH,
    PROCESSOR_WATER_DEFAULTS_CONFIG_PATH
)
from hypernets_processor.data_io.hypernets_db_builder import open_database
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "24/9/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(settings):
    """
    Main function to run routine to setup hypernets_processor

    :type settings: dict
    :param settings: user defined configuration values
    """

    # Set default config values for chosen network
    config_path = PROCESSOR_CONFIG_PATH
    if settings["network_defaults"]:
        if settings["network"] == "land":
            def_config_path = PROCESSOR_LAND_DEFAULTS_CONFIG_PATH
        elif settings["network"] == "water":
            def_config_path = PROCESSOR_WATER_DEFAULTS_CONFIG_PATH
        else:
            raise KeyError("Invalid network name ("+settings["network"]+")")

        config_path = [PROCESSOR_CONFIG_PATH, def_config_path]

    processor_config = read_config_file(config_path)

    # Create directories (resets with existing if unchanged)
    os.makedirs(settings["working_directory"], exist_ok=True)
    processor_config["Processor"]["processor_working_directory"] = settings["working_directory"]
    os.makedirs(settings["archive_directory"], exist_ok=True)
    processor_config["Output"]["archive_directory"] = settings["archive_directory"]

    # Create databases
    db_fmts = ["metadata", "anomoly"]
    for db_fmt in db_fmts:
        url = settings[db_fmt + "_db_url"]

        if url is not None:
            new_db = open_database(url, create_format=db_fmt)
            new_db.close()
            processor_config["Databases"][db_fmt + "_db_url"] = url

    # Set processor log file
    if not os.path.exists(settings["log_path"]):
        open(settings["log_path"], 'a').close()
    processor_config["Log"]["log_path"] = settings["log_path"]

    # Write updated config file
    with open(PROCESSOR_CONFIG_PATH, 'w') as f:
        processor_config.write(f)

    return None


if __name__ == "__main__":
    pass
