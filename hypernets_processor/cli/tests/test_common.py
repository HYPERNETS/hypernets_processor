"""
Tests for common module
"""

import unittest
from hypernets_processor.version import __version__
from hypernets_processor.cli.common import read_config_file, read_jobs_list
from configparser import RawConfigParser
import os
import shutil


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "31/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


this_directory = os.path.dirname(__file__)


def create_config_file(fname):
    text = "[Section]\nentry: value"

    with open(fname, "w") as f:
        f.write(text)
    return None


def create_jobs_list_file(fname):
    os.mkdir("config_test")
    with open("config_test/job1.config", "w") as f:
        f.write(" ")
    with open("config_test/job2.config", "w") as f:
        f.write(" ")

    text = "job1.config\njob2.config"

    with open(fname, "w") as f:
        f.write(text)
    return None


class TestCommon(unittest.TestCase):
    def test_read_config_file(self):
        fname = "file.config"
        create_config_file(fname)

        config = read_config_file(fname)

        self.assertEqual(type(config), RawConfigParser)
        self.assertEqual(config["Section"]["entry"], "value")

        os.remove(fname)

    def test_read_jobs_list(self):

        fname = "config_test/file.config"
        create_jobs_list_file(fname)

        jobs = read_jobs_list(fname)

        expected_jobs = [os.path.abspath(os.path.join(this_directory, "config_test", "job1.config")),
                         os.path.abspath(os.path.join(this_directory, "config_test", "job2.config"))]

        self.assertCountEqual(jobs, expected_jobs)

        shutil.rmtree("config_test")


if __name__ == "__main__":
    unittest.main()
