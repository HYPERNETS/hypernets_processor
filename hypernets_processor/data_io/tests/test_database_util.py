"""
Tests for DatasetUtil class
"""

import unittest
import string
import random
from datetime import date, datetime
import os
from copy import deepcopy
from sqlalchemy import UnicodeText, Float, BigInteger, Boolean, Date, \
    DateTime, JSON
from sqlalchemy_utils import drop_database
from hypernets_processor.data_io.database_util import DatabaseUtil
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


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


def test_db_schema(self, db):

    # Test tables
    self.assertCountEqual(db.tables, ["table1", "table2"])

    # Test table1
    table1 = db.get_table("table1")
    self.assertCountEqual(table1.table.columns.keys(), ["1id", "column1"])

    # Test table1, column 1id
    table1_1id = table1.table.columns['1id']
    self.assertTrue(table1_1id.primary_key)

    # todo - check types for creation of db schema in different dialects
    #self.assertEqual(type(table1_1id.type), type(BigInteger()))

    # Test table1, column column1
    table1_column1 = table1.table.columns['column1']
    self.assertFalse(table1_column1.primary_key)
    #elf.assertEqual(type(table1_column1.type), type(UnicodeText()))

    # Test table2
    table2 = db.get_table("table2")
    self.assertCountEqual(table2.table.columns.keys(), ["id", "2id", "column2"])

    # Test table2, column id
    table2_id = table2.table.columns['id']
    self.assertTrue(table2_id.primary_key)
    #self.assertEqual(type(table2_id.type), type(INTEGER()))

    # Test table2, column 2id
    table2_2id = table2.table.columns['2id']
    self.assertFalse(table2_2id.primary_key)
    #self.assertEqual(type(table2_2id.type), type(BIGINT()))

    # Test table2, column column2
    table2_column2 = table2.table.columns['column2']
    self.assertFalse(table2_column2.primary_key)
    #self.assertEqual(type(table2_column2.type), type(FLOAT()))


class TestDatabaseUtil(unittest.TestCase):

    def test_create_db_sqlite(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        self.assertEqual(db.engine.url.__str__(), url)

        # test that you can create
        db.create_table("test")

    def test_create_db_postgresql(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6))
        url = "postgresql://localhost/" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        self.assertEqual(db.engine.url.__str__(), url)

        # test that you can create
        db.create_table("table")

        del db
        drop_database(url)

    def test_create_db_other(self):

        dbu = DatabaseUtil()
        self.assertRaises(NameError, dbu.create_db, "mysql://localhost/test")

    def test_get_db_type(self):
        dbu = DatabaseUtil()

        self.assertEqual(dbu.get_db_type(bool), Boolean)
        self.assertEqual(dbu.get_db_type(int), BigInteger)
        self.assertEqual(dbu.get_db_type(float), Float)
        self.assertEqual(dbu.get_db_type(str), UnicodeText)
        self.assertEqual(dbu.get_db_type(date), Date)
        self.assertEqual(dbu.get_db_type(datetime), DateTime)
        self.assertEqual(dbu.get_db_type(dict), JSON)

    def test_apply_schema_dict_sqlite(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        test_schema = deepcopy(TEST_SCHEMA)
        dbu.apply_schema_dict(db, schema_dict=test_schema)

        test_db_schema(self, db)

        del db
        os.remove(temp_name)

    def test_apply_schema_dict_postgresql(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6))
        url = "postgresql://localhost/" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        test_schema = deepcopy(TEST_SCHEMA)
        dbu.apply_schema_dict(db, schema_dict=test_schema)

        test_db_schema(self, db)

        drop_database(url)

    def test_update_to_foreign_key(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6))
        url = "postgresql://localhost/" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        test_schema = deepcopy(TEST_SCHEMA)
        dbu.apply_schema_dict(db, schema_dict=test_schema)

        table1 = db.get_table("table1")
        table1_column1 = table1.table.columns['column1']
        fk1_before = table1_column1.foreign_keys

        self.assertEqual(len(fk1_before), 0)

        dbu.update_to_foreign_key(db, "table1", "column1", "table2", "id")

        table1 = db.get_table("table1")
        table1_column1 = table1.table.columns['column1']
        fk1_after = table1_column1.foreign_keys

        self.assertEqual(len(fk1_after), 1)

        drop_database(url)

    def test_apply_schema_dict_postgresql_foreign_key(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6))
        url = "postgresql://localhost/" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        test_schema = deepcopy(TEST_SCHEMA)
        test_schema["table1"]["columns"]["column1"]["foreign_key"] = {"reference_table": "table2",
                                                                      "reference_column": "id"}

        dbu.apply_schema_dict(db, schema_dict=test_schema)

        table1 = db.get_table("table1")
        table1_column1 = table1.table.columns['column1']
        fk = table1_column1.foreign_keys

        self.assertEqual(len(fk), 1)

        drop_database(url)

    def test_apply_schema_dict_sqlite_foreign_key(self):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + temp_name

        dbu = DatabaseUtil()
        db = dbu.create_db(url)

        test_schema = deepcopy(TEST_SCHEMA)
        test_schema["table1"]["columns"]["column1"]["foreign_key"] = {"reference_table": "table2",
                                                                      "reference_column": "id"}

        self.assertRaises(TypeError, dbu.apply_schema_dict, db, test_schema)

        del db
        os.remove(temp_name)


if __name__ == '__main__':
    unittest.main()
