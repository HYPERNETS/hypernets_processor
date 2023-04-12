"""
Tests for config module
"""

import unittest
from hypernets_processor.version import __version__
from hypernets_processor.utils.config import (
    get_config_value,
    infer_dtype,
    read_config_file,
    read_jobs_list,
)
from configparser import RawConfigParser
import os
import shutil


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
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


def create_jobs_list_file(directory, fname):

    os.mkdir(directory)
    with open(os.path.join(directory, "job1.config"), "w") as f:
        f.write(" ")
    with open(os.path.join(directory, "job2.config"), "w") as f:
        f.write(" ")

    text = "job1.config\njob2.config"

    with open(os.path.join(directory, fname), "w") as f:
        f.write(text)
    return None


class TestConfig(unittest.TestCase):
    def test_infer_dtype_str(self):
        dtype = infer_dtype("string")
        self.assertEqual(dtype, str)

    def test_infer_dtype_int(self):
        dtype = infer_dtype("11")
        self.assertEqual(dtype, int)

    def test_infer_dtype_float(self):
        dtype = infer_dtype("11.7")
        self.assertEqual(dtype, float)

    def test_infer_dtype_bool_True(self):
        dtype = infer_dtype("False")
        self.assertEqual(dtype, bool)

    def test_infer_dtype_bool_False(self):
        dtype = infer_dtype("False")
        self.assertEqual(dtype, bool)

    def test_get_config_value_empty_string(self):
        config = RawConfigParser()
        config["section"] = {"key": ""}

        val = get_config_value(config, "section", "key")
        self.assertIsNone(val)

    def test_get_config_value_None(self):
        config = RawConfigParser()
        config["section"] = {"key": None}

        val = get_config_value(config, "section", "key")
        self.assertIsNone(val)

    def test_get_config_value_None_bool(self):
        config = RawConfigParser()
        config["section"] = {"key": None}

        val = get_config_value(config, "section", "key", dtype=bool)
        self.assertEqual(val, False)

    def test_get_config_value_dtype_None(self):
        config = RawConfigParser()
        config["section"] = {"key": "val"}

        val = get_config_value(config, "section", "key")
        self.assertEqual(val, "val")

    def test_get_config_value_dtype_bool(self):
        config = RawConfigParser()
        config["section"] = {"key": "False"}

        val = get_config_value(config, "section", "key")
        self.assertEqual(val, False)

    def test_get_config_value_int(self):
        config = RawConfigParser()
        config["section"] = {"key": 3}

        val = get_config_value(config, "section", "key", dtype=int)
        self.assertEqual(type(val), int)
        self.assertEqual(val, 3)

    def test_config_value_bool(self):
        config = RawConfigParser()
        config["section"] = {"key": "True"}

        val = get_config_value(config, "section", "key", dtype=bool)
        self.assertEqual(type(val), bool)
        self.assertEqual(val, True)

    def test_config_value_float(self):
        config = RawConfigParser()
        config["section"] = {"key": 2.0}

        val = get_config_value(config, "section", "key", dtype=float)
        self.assertEqual(type(val), float)
        self.assertEqual(val, 2.0)

    def test_read_config_file(self):
        fname = "file.config"
        create_config_file(fname)

        config = read_config_file(fname)

        self.assertEqual(type(config), RawConfigParser)
        self.assertEqual(config["Section"]["entry"], "value")

        os.remove(fname)

    def test_read_jobs_list(self):
        test_dir = os.path.join(this_directory, "config_test")
        fname = "file.config"
        create_jobs_list_file(test_dir, fname)

        jobs = read_jobs_list(os.path.abspath(os.path.join(test_dir, "file.config")))

        expected_jobs = [
            os.path.abspath(os.path.join(test_dir, "job1.config")),
            os.path.abspath(os.path.join(test_dir, "job2.config")),
        ]

        self.assertCountEqual(jobs, expected_jobs)

        shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()
