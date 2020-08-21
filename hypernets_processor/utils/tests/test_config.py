"""
Tests for config module
"""

import unittest
from hypernets_processor.version import __version__
from hypernets_processor.utils.config import get_config_value
from configparser import RawConfigParser


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestConfig(unittest.TestCase):
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

    def test_get_config_value_str(self):
        config = RawConfigParser()
        config["section"] = {"key": "val"}

        val = get_config_value(config, "section", "key")
        self.assertEqual(val, "val")

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


if __name__ == "__main__":
    unittest.main()
