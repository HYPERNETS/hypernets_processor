"""
Common functions for command line interfaces
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.paths import relative_path
from hypernets_processor.utils.config import get_config_value
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

loggers = {}


def configure_logging(fname=None, verbose=None, trace=None, quiet=None, config=None, name=None):
    """
    Configure logger

    :type fname: str
    :param fname:  path to write log to, if None output log as stdout

    :type verbose: bool
    :param verbose: Option for verbose log output (DEBUG level)

    :type quiet: bool
    :param quiet: Option for quiet log output (WARNING level)

    :type config: configparser.RawConfigParser
    :param config: Config file with logging configuration information. This finds fname, verbose and quiet if not
    specifed as arguments

    :type name: str
    :param name: (optional) set name of logger to get

    :return: logger
    :rtype: logging.logger
    """
    global loggers

    if name is not None:
        if loggers.get(name):
            return loggers.get(name)

    if config is not None:
        fname = get_config_value(config, "Log", "log_path", dtype=str)
        verbose = get_config_value(config, "Log", "verbose", dtype=bool)
        trace = get_config_value(config, "Log", "trace", dtype=bool)
        quiet = get_config_value(config, "Log", "quiet", dtype=bool)

    # Configure logger
    if name is None:
        name = __name__

    logger = logging.getLogger(name)

    # Define verboseness levels
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif trace:
        logger.setLevel(logging.TRACE)
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

    loggers[name] = logger

    return logger