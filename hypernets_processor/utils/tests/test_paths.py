"""
Tests for paths module
"""

import unittest
from hypernets_processor.version import __version__
from hypernets_processor.utils.paths import relative_path
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestPaths(unittest.TestCase):
    def test_relative_path_in_directory(self):

        cwd = os.getcwd()

        # Use data directory for tests
        data_directory = "../../../data/tests/cli"
        fname = "jobs1.config"

        full_path = relative_path(fname, data_directory)

        self.assertEqual(full_path, os.path.abspath("../../../data/tests/cli/jobs1.config"))
        self.assertEqual(cwd, os.getcwd())


    def test_relative_path_in_subdirectory(self):

        cwd = os.getcwd()

        # Use data directory for tests
        data_directory = "../../../data"
        fname = "tests/cli/jobs1.config"

        full_path = relative_path(fname, data_directory)

        self.assertEqual(full_path, os.path.abspath("../../../data/tests/cli/jobs1.config"))
        self.assertEqual(cwd, os.getcwd())

    def test_relative_path_in_relative_directory(self):

        cwd = os.getcwd()

        # Use data directory for tests
        data_directory = "../../../data/tests/reader"
        fname = "../cli/jobs1.config"

        full_path = relative_path(fname, data_directory)

        self.assertEqual(full_path, os.path.abspath("../../../data/tests/cli/jobs1.config"))
        self.assertEqual(cwd, os.getcwd())


if __name__ == "__main__":
    unittest.main()
