"""
Module of helper functions for configfile operations
"""
import numpy as np
from hypernets_processor.version import __version__
from hypernets_processor.utils.paths import relative_path
import os
import configparser


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "4/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


this_directory = os.path.dirname(__file__)
etc_directory = os.path.join(os.path.dirname(this_directory), "etc")
WORKING_DIRECTORY_FILE_PATH = os.path.join(etc_directory, "working_directory.txt")
if os.path.exists(WORKING_DIRECTORY_FILE_PATH):
    working_directory = os.path.abspath(
        str(np.genfromtxt(WORKING_DIRECTORY_FILE_PATH, dtype=str))
    )

    PROCESSOR_CONFIG_PATH = os.path.join(working_directory, "processor.config")
    SCHEDULER_CONFIG_PATH = os.path.join(working_directory, "scheduler.config")
    JOBS_FILE_PATH = os.path.join(working_directory, "jobs.txt")
else:
    print(
        "working_directory.txt does not exist so some of the paths for automated processing could not be correctly set up."
    )
    PROCESSOR_CONFIG_PATH = None
    SCHEDULER_CONFIG_PATH = None
    JOBS_FILE_PATH = None

PROCESSOR_DEFAULT_CONFIG_PATH = os.path.join(etc_directory, "processor.config")
PROCESSOR_LAND_DEFAULTS_CONFIG_PATH = os.path.join(
    etc_directory, "processor_land_defaults.config"
)
PROCESSOR_WATER_DEFAULTS_CONFIG_PATH = os.path.join(
    etc_directory, "processor_water_defaults.config"
)
SCHEDULER_DEFAULT_CONFIG_PATH = os.path.join(etc_directory, "scheduler_default.config")
JOB_CONFIG_TEMPLATE_PATH = os.path.join(etc_directory, "job_template.config")


def read_config_file(fname):
    """
    Returns information from configuration file

    :type fname: str
    :param fname: path of configuration file

    :return: configuration information
    :rtype: configparser.RawConfigParser
    """

    # Open file
    config = configparser.RawConfigParser()
    config.read(fname)

    return config


def read_jobs_list(fname):
    """
    Return job config paths from jobs list file

    :type fname: str
    :param fname: path of jobs list file

    :return: job config paths
    :rtype: list
    """

    # Read lines for file
    with open(fname, "r") as f:
        # lines = [line.rstrip() for line in f.readlines()]
        jobs = [
            relative_path(line.rstrip(), os.path.dirname(fname))
            for line in f.readlines()
        ]

    return jobs


def get_config_value(config, section, key, dtype=None):
    """
    Return value from config file

    :type config: configparser.RawConfig
    :param config: parsed config file

    :type section: str
    :param section: section to retrieve data from

    :type key: str
    :param key: key in section to retrieve data from

    :type dtype: type
    :param dtype: type of data to return

    :return: config value
    :rtype: str/bool/int/float
    """

    val = config.get(section, key, fallback=None)

    dtype = infer_dtype(val) if dtype is None else dtype

    if (val == "") or (val is None):
        if dtype == bool:
            return False
        return None

    if dtype == str:
        return val

    elif dtype == bool:
        return config.getboolean(section, key)

    elif dtype == int:
        return config.getint(section, key)

    elif dtype == float:
        return config.getfloat(section, key)


def infer_dtype(val):
    """
    Return inferred dtype of val

    :param val: value

    :return: inferred data type
    :rtype: type
    """

    # Check bool
    if (val == "True") or (val == "False"):
        return bool

    # Check int
    is_int = True
    try:
        int(val)
    except:
        is_int = False

    if is_int:
        return int

    # Check float
    is_float = True
    try:
        float(val)
    except:
        is_float = False

    if is_float:
        return float

    return str


if __name__ == "__main__":
    pass
