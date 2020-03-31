"""
Common functions for command line interfaces
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.paths import relative_path
import logging
import sys
import os
import argparse
import configparser


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def configure_logging(fname=None, verbose=False, quiet=False):
    """
    Configure logger

    :type fname: str
    :param fname:  path to write log to, if None output log as stdout

    :type verbose: bool
    :param verbose: Option for verbose log output (DEBUG level)

    :type quiet: bool
    :param quiet: Option for quiet log output (WARNING level)

    :return: logger
    :rtype: logging.logger
    """

    # Configure logger
    logger = logging.getLogger(__name__)

    # Define verboseness levels
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)

    # Define logging to file if fname provided
    if fname is not None:
        file_formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        file_handler = logging.FileHandler(fname)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Define logging to stdout if no fname provided
    else:
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    return logger


def configure_std_parser(description=None):
    """
    Configure parser with standard arguments

    :param description:  path to write log to, if None output log as stdout

    :return: parser
    :rtype: argparse.ArgumentParser
    """

    # Initialise argument parser
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add logging related arguments
    logging_options = parser.add_mutually_exclusive_group()
    logging_options.add_argument("--verbose", action="store_true",
                                 help="Option for verbose output")

    logging_options.add_argument("--quiet", action="store_true",
                                 help="Option for quiet output")

    parser.add_argument("--log", action="store", type=str, default=None,
                        help="Log file to write to. Leave out for stdout.")

    # Add software version argument
    parser.add_argument("--version", action="version", version='v%s' % __version__)

    return parser


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


def read_std_config(config):
    """
    Returns standard configuration information from configuration file

    :type config: config.RawConfig
    :param config: path of configuration file

    :rtype: dict
    :return: standard configuration information, with entries (defaults occur if entry omitted from config file):

    * log_path (str) - Path to write log to, default None (means log goes to stdout)
    * verbose (bool) - Switch for verbose output, default False
    * quiet (bool) - Switch for quiet output, default False

    """

    config_dict = dict()

    # Logging Configuration
    config_dict["log_path"] = None
    config_dict["verbose"] = False
    config_dict["quiet"] = False
    if "Log" in config.keys():
        config_dict["log_path"] = config["Log"]["path"] if "verbose" in config["Log"].keys() else None
        config_dict["verbose"] = bool(config["Log"]["verbose"]) if "verbose" in config["Log"].keys() else False
        config_dict["quiet"] = bool(config["Log"]["quiet"]) if "quiet" in config["Log"].keys() else False

    return config_dict


def read_scheduler_config_file(fname):
    """
    Returns information from scheduler configuration file

    :type fname: str
    :param fname: path of configuration file

    :rtype: dict
    :return: scheduler configuration information, with entries (defaults occur if entry omitted from config file):

    * seconds (int) - Scheduled job repeat interval in seconds, default None (if not None minutes and hours are None)
    * minutes (int) - Scheduled job repeat interval in minutes, default None (if not None seconds and hours are None)
    * hours (int) - Scheduled job repeat interval in hour, default None (if not None seconds and minutes are None)
    * start_time (datetime.datetime) - Scheduled time to start running tasks, default None (means start now)
    * parallel (bool) - Switch to run scheduled jobs on different threads, default False
    * log_path (str) - Path to write log to, default None (means log goes to stdout)
    * verbose (bool) - Switch for verbose output, default False
    * quiet (bool) - Switch for quiet output, default False

    """

    scheduler_config = read_config_file(fname)

    scheduler_config_dict = read_std_config(scheduler_config)

    # Schedule Configuration
    scheduler_config_dict["seconds"] = scheduler_config["Schedule"]["seconds"] if "seconds" in \
                                           scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["minutes"] = scheduler_config["Schedule"]["minutes"] if "minutes" in \
                                           scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["hours"] = scheduler_config["Schedule"]["hours"] if "hours" in \
                                         scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["start_time"] = scheduler_config["Schedule"]["start_time"] if "start_time" in \
                                             scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["parallel"] = scheduler_config["Schedule"]["parallel"] if "parallel" in \
                                            scheduler_config["Schedule"].keys() else False

    # Checks
    # Check only have hours, minutes or seconds
    intervals = [scheduler_config_dict["seconds"], scheduler_config_dict["minutes"], scheduler_config_dict["hours"]]
    if intervals.count(None) != 2:
        raise ValueError("Scheduled job repeat interval must be defined as 1 of seconds, minutes or hours")

    return scheduler_config_dict


def read_processor_config_file(fname):
    """
    Returns information from processor configuration file

    :type fname: str
    :param fname: path of configuration file

    :rtype: dict
    :return: processor configuration information, with entries (defaults occur if entry omitted from config file):

    * ...

    """

    processor_config = read_config_file(fname)
    processor_config_dict = dict()

    # todo - read processor config information

    return processor_config_dict


def read_job_config_file(fname):
    """
    Returns information from job configuration file

    :type fname: str
    :param fname: path of configuration file

    :rtype: dict
    :return: job configuration information, with entries (defaults occur if entry omitted from config file):

    * log_path (str) - Path to write log to, default None (means log goes to stdout)
    * verbose (bool) - Switch for verbose output, default False
    * quiet (bool) - Switch for quiet output, default False

    """

    job_config = read_config_file(fname)
    job_config_dict = read_std_config(job_config)

    # todo - read job config information

    return job_config_dict


def read_jobs_list(fname):
    """
    Return job config paths from jobs list file

    :type fname: str
    :param fname: path of jobs list file

    :return: job config paths
    :rtype: list
    """

    # Read lines for file
    with open(fname) as f:
        jobs = [relative_path(line.rstrip(), os.path.dirname(fname)) for line in f]

    return jobs


if __name__ == "__main__":
    pass
