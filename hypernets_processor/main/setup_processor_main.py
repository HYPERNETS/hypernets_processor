"""
Main function to setup processor on install
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import (
    read_config_file,
    PROCESSOR_DEFAULT_CONFIG_PATH,
    PROCESSOR_LAND_DEFAULTS_CONFIG_PATH,
    PROCESSOR_WATER_DEFAULTS_CONFIG_PATH,
    SCHEDULER_DEFAULT_CONFIG_PATH,
    WORKING_DIRECTORY_FILE_PATH,
)
from hypernets_processor.data_io.format.databases import DB_DICT_DEFS
from hypernets_processor.data_io.hypernets_db_builder import open_database
import os


"""___Authorship___"""
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
    config_path = os.path.join(settings["working_directory"], "processor.config")
    if settings["network_defaults"]:
        if settings["network"] == "l":
            def_config_path = PROCESSOR_LAND_DEFAULTS_CONFIG_PATH
        elif settings["network"] == "w":
            def_config_path = PROCESSOR_WATER_DEFAULTS_CONFIG_PATH
        else:
            raise KeyError("Invalid network name (" + settings["network"] + ")")

        config_path = [PROCESSOR_DEFAULT_CONFIG_PATH, def_config_path]

    processor_config = read_config_file(config_path)

    # Create directories (resets with existing if unchanged)
    os.makedirs(settings["working_directory"], exist_ok=True)
    processor_config["Processor"]["processor_working_directory"] = settings[
        "working_directory"
    ]
    os.makedirs(settings["archive_directory"], exist_ok=True)
    processor_config["Output"]["archive_directory"] = settings["archive_directory"]

    with open(WORKING_DIRECTORY_FILE_PATH, "w") as f:
        f.write(settings["working_directory"])

    # Create databases
    for db_fmt in DB_DICT_DEFS.keys():
        url = settings[db_fmt + "_db_url"]

        if url is not None:
            new_db = open_database(url, db_format=db_fmt)
            new_db.close()
            processor_config["Databases"][db_fmt + "_db_url"] = url

    # Write updated config file
    with open(
        os.path.join(settings["working_directory"], "processor.config"), "w"
    ) as f:
        processor_config.write(f)

    # Set scheduler log file
    scheduler_config = read_config_file(SCHEDULER_DEFAULT_CONFIG_PATH)
    if not os.path.exists(settings["log_path"]):
        open(settings["log_path"], "a").close()
    scheduler_config["Log"]["log_path"] = settings["log_path"]

    with open(
        os.path.join(settings["working_directory"], "scheduler.config"), "w"
    ) as f:
        scheduler_config.write(f)

    return None


if __name__ == "__main__":
    pass
