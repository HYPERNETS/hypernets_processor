"""
Common functions for command line interfaces
"""

from hypernets_processor.version import __version__
import argparse


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


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


def cli_input_yn(query, default=True):

    str_def = "n"
    if default:
        str_def = "y"

    res = input(query.capitalize() + " (y/n) [" + str_def + "]: ") or str_def

    if res == "y":
        return True
    elif res == "n":
        return False

    raise ValueError("enter y or n")


def cli_input_str_default(query, default=None):

    str_def = ""
    if default is not None:
        str_def = " [" + default + "]"

    res = input(query.capitalize() + str_def + ": ") or default

    return res


def cli_input_str_opts(query, options=None):

    str_def = ""
    if options is not None:
        str_def = "[" + "/".join(options) + "]"

    res = input(query.capitalize() + str_def + ": ")

    if res in options:
        return res

    raise ValueError("must be one of " + str(options))


def determine_if_set(value_name, context):
    value = context.get_config_value(value_name)

    set_value = True
    if value is not None:
        set_value = cli_input_yn(
            "update " + value_name + ", currently '" + value + "'",
            default=False
        )
    return set_value


def determine_set_value(value_name, context, default=None, options=None, return_existing=False):
    value = context.get_config_value(value_name)

    set_value = determine_if_set(value_name, context)

    value_return = None

    if set_value:
        if options is not None:
            value_return = cli_input_str_opts(
                "set "+value_name,
                options=options
            )

        else:
            value_return = cli_input_str_default(
                "set " + value_name,
                default=default
            )

    if (value_return is None) and return_existing:
        return value
    return value_return


if __name__ == "__main__":
    pass
