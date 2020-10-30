"""
Tests for HypernetsDBBuilder class
"""

import unittest
from unittest.mock import patch
from hypernets_processor.data_io.database_util import DatabaseUtil
from hypernets_processor.data_io.hypernets_db_builder import HypernetsDBBuilder
from hypernets_processor.data_io.hypernets_db_builder import open_database
from hypernets_processor.version import __version__
import os
import string
import random
from copy import deepcopy


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "31/7/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


this_directory = os.path.dirname(__file__)

TEST_SCHEMA = {"table1": {"columns": {"1id": {"type": int},
                                      "column1": {"type": int}
                                      },
                          "primary_key": "1id"
                          },
               "table2": {"columns": {"2id": {"type": int},
                                      "column2": {"type": float}
                                      }
                          }
               }


class TestHypernetsDBBuilder(unittest.TestCase):

    @patch("hypernets_processor.data_io.hypernets_db_builder.HypernetsDBBuilder")
    @patch("hypernets_processor.data_io.hypernets_db_builder.makedirs")
    @patch("hypernets_processor.data_io.hypernets_db_builder.dataset.connect")
    def test_open_database_create_nodir(self, mock_ds, mock_mk, mock_hdb):
        db = open_database("sqlite:///test/test.db", create_format="metadata")
        mock_mk.assert_called_once_with("test")
        mock_hdb.return_value.create_db_template.assert_called_once_with("sqlite:///test/test.db", "metadata")
        mock_ds.assert_not_called()

    def test_open_database_none(self):
        url = "sqlite:///" + this_directory + "/test.db"
        db = open_database(url)
        self.assertIsNone(db)

    @patch("hypernets_processor.data_io.hypernets_db_builder.HypernetsDBBuilder")
    @patch("hypernets_processor.data_io.hypernets_db_builder.makedirs")
    def test_open_database(self, mock_mk, mock_hdb):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + this_directory + "/" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        test_schema = deepcopy(TEST_SCHEMA)
        dbu.apply_schema_dict(db, schema_dict=test_schema)
        db.close()

        db = open_database(url, create_format="metadata")
        self.assertEqual(db.url, url)

        mock_mk.assert_not_called()
        mock_hdb.assert_not_called()

        del db
        os.remove(temp_name)

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
