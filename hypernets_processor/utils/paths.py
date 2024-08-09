"""
Module of helper functions for file path operations
"""
import warnings

from hypernets_processor.version import __version__
from datetime import datetime as dt
import os


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "31/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def relative_path(path, directory):
    """
    Return path relative to given directory

    :type path: str
    :param path: path of file relative to directory

    :type directory: str
    :param directory: path of directory

    :return: full file path
    :rtype: str
    """

    if directory == "":
        directory = "."

    cwd = os.getcwd()
    os.chdir(directory)
    full_path = os.path.abspath(path)
    os.chdir(cwd)

    return full_path


def parse_sequence_path(path, context=None):
    """
    Unpacks info from raw sequence path, e.g. some/directory/SEQ20200312T135926

    :type path: str
    :param path: sequence path

    :return: unpacked path, containing datetime (None if not a sequence path)
    :rtype: dict
    """
    sequence_path = os.path.basename(path)

    if sequence_path[:3] == "SEQ":
        date_str = sequence_path[3:]
        try:
            date = dt.strptime(date_str, "%Y%m%dT%H%M%S")
            return {"datetime": date}
        except:
            if context is not None:
                context.logger.error(
                    "The following path does not match the expected format and will not be processed (%s)"%(path))
            else:
                warnings.warn(
                    "The following path does not match the expected format and will not be processed (%s)" % (path))
    return None


if __name__ == "__main__":
    pass
