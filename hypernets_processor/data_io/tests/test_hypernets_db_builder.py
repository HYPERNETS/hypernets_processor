"""
Tests for HypernetsDBBuilder class
"""

import unittest
from unittest.mock import patch
from hypernets_processor.data_io.hypernets_db_builder import HypernetsDBBuilder
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "31/7/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestHypernetsDBBuilder(unittest.TestCase):

    @patch('hypernets_processor.data_io.hypernets_db_builder.create_template_db')
    def test_create_db_template_schema_dict(self, mock_create_template_dataset):

        url = "test"

        db_format_defs = {"def1": {"empty": "dict"}, "def2": "db2"}

        db = HypernetsDBBuilder.create_db_template(url, "def1", db_format_defs)

        # test calls to create_template_dataset
        mock_create_template_dataset.assert_called_once_with("test",
                                                             schema_dict={"empty": "dict"},
                                                             schema_sql=None)

        self.assertEqual(db, mock_create_template_dataset.return_value)

    @patch('hypernets_processor.data_io.hypernets_db_builder.create_template_db')
    def test_create_db_template_schema_sql(self, mock_create_template_dataset):
        url = "test"

        db_format_defs = {"def1": {"empty": "dict"}, "def2": "db2"}

        db = HypernetsDBBuilder.create_db_template(url, "def2", db_format_defs)

        # test calls to create_template_dataset
        mock_create_template_dataset.assert_called_once_with("test",
                                                             schema_dict=None,
                                                             schema_sql="db2")

        self.assertEqual(db, mock_create_template_dataset.return_value)

    @patch('hypernets_processor.data_io.hypernets_db_builder.create_template_db')
    def test_create_db_template_default_defs(self, mock_create_template_dataset):
        db = HypernetsDBBuilder.create_db_template("test", "metadata")

        # test calls to create_template_dataset
        mock_create_template_dataset.assert_called()

        self.assertEqual(db, mock_create_template_dataset.return_value)


if __name__ == '__main__':
    unittest.main()
