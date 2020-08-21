"""
Module of helper functions for file path operations
"""


from hypernets_processor.version import __version__
import os


'''___Authorship___'''
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


if __name__ == "__main__":
    pass
