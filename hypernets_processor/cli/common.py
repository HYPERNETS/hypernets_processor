"""
Common functions for command line interfaces
"""

from hypernets_processor.version import __version__
import logging
import sys
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


def read_config(fname):
    """
    Returns information from hypernets_processor configuration file

    :type fname: str
    :param fname: path of configuration file

    :return: configuration information
    :rtype: configparser.RawConfigParser
    """

    # Open file
    config = configparser.RawConfigParser()
    config.read(fname)

    return config


if __name__ == "__main__":
    pass
