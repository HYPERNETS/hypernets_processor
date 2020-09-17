"""
Tests for Context class
"""

import unittest
from unittest.mock import MagicMock, patch, call
from hypernets_processor.version import __version__
from hypernets_processor.test.test_functions import (
    setup_test_job_config,
    setup_test_processor_config,
)
from hypernets_processor.context import Context
from configparser import RawConfigParser


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def setup_test_config():
    config = RawConfigParser()

    config["Default"] = {"entry1": "value1", "entry2": "value2"}
    config["Other"] = {"entry3": "value3", "entry4": "value4"}
    return config


class TestContext(unittest.TestCase):
    def test_unpack_config(self):

        context = Context()

        config = setup_test_config()
        context.unpack_config(config)

        expected_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        self.assertDictEqual(context.config_values, expected_values)

    def test_unpack_config_protected_values(self):

        context = Context()

        config = setup_test_config()
        context.unpack_config(config, protected_values=["entry4"])

        expected_values = {"entry1": "value1", "entry2": "value2", "entry3": "value3"}

        self.assertDictEqual(context.config_values, expected_values)

    def test_unpack_config_twice(self):

        context = Context()

        config = setup_test_config()
        context.unpack_config(config)

        config2 = RawConfigParser()
        config2["Default"] = {"entry1": "overridden_value"}
        context.unpack_config(config2)

        expected_values = {
            "entry1": "overridden_value",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        self.assertDictEqual(context.config_values, expected_values)

    def test_get_config_names(self):
        context = Context()
        context.config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        entry_list = context.get_config_names()

        self.assertCountEqual(entry_list, ["entry1", "entry2", "entry3", "entry4"])

    def test_get_config_value(self):
        context = Context()
        context.config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        value = context.get_config_value("entry2")

        self.assertCountEqual(value, "value2")

    @patch("hypernets_processor.context.dataset")
    def test___init__(self, mock_dataset):
        job_config = setup_test_job_config()
        processor_config = setup_test_processor_config()
        logger = MagicMock()

        context = Context(
            job_config=job_config, processor_config=processor_config, logger=logger
        )

        # Test values
        self.assertEqual(context.get_config_value("network"), "land")
        self.assertEqual(context.get_config_value("site"), "site")
        self.assertEqual(context.get_config_value("raw_data_directory"), "data")
        self.assertEqual(
            context.get_config_value("anomoly_db_url"), "sqlite:///anomoly.db"
        )
        self.assertEqual(
            context.get_config_value("measurement_function_name"),
            "standard_measurement_function",
        )
        self.assertEqual(
            context.get_config_value("reflectance_protocol_name"), "standard_protocol"
        )
        self.assertEqual(context.get_config_value("write_l1a"), True)
        self.assertEqual(context.get_config_value("version"), 0.0)
        self.assertEqual(
            context.get_config_value("metadata_db_url"), "sqlite:///metadata.db"
        )
        self.assertEqual(context.get_config_value("archive_directory"), "out")

        # Test logger
        self.assertEqual(context.logger, logger)

        # Test dbs
        self.assertEqual(context.metadata_db, mock_dataset.connect.return_value)
        self.assertEqual(context.anomoly_db, mock_dataset.connect.return_value)
        self.assertCountEqual(
            [call("sqlite:///anomoly.db"), call("sqlite:///metadata.db")],
            mock_dataset.connect.call_args_list,
        )


if __name__ == "__main__":
    unittest.main()
