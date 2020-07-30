"""
DatabaseUtil class
"""

from hypernets_processor.version import __version__
import dataset
from dataset.types import Types
from copy import copy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import drop_database
from datetime import date, datetime

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "28/7/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def create_template_db(url, schema_dict=None, schema_sql=None):
    """
    Create database at defined url and initialise database with defined schema

    :type url: str
    :param url: url of database to create

    :type schema_dict: dict
    :param schema_dict: dictionary defining database schema

    :type schema_sql: str
    :param schema_sql: sql command to create database schema

    :return: Initialised database
    :rtype: dataset.Database
    """

    dbu = DatabaseUtil()

    db = dbu.create_db(url)

    if schema_dict is not None:
        dbu.apply_schema_dict(db, schema_dict)

    elif schema_sql is not None:
        db.begin()
        db.query(schema_sql)
        db.commit()

    return db


class DatabaseUtil:
    """
    Class to provide utilities for generating databases
    """

    @staticmethod
    def create_db(url):
        """
        Create database at defined url (sqlite or postgresql)

        :type url: str
        :param url: url of database to create

        :return: New database
        :rtype: dataset.Database
        """

        url = copy(make_url(url))

        database = url.database

        if url.drivername.startswith('sqlite'):
            pass

        elif url.drivername.startswith('postgres'):

            # Open issue with sqlalchemy.create_database for postgresql running in pycharm debug env
            # https://github.com/kvesteri/sqlalchemy-utils/issues/432

            url.database = 'postgres'
            engine = create_engine(url, isolation_level="AUTOCOMMIT")
            engine.execute("CREATE DATABASE " + database + " ENCODING 'utf8' TEMPLATE template1")
            url.database = database

        else:
            raise NameError("invalid url - engine must be either sqlite or postgresql")

        return dataset.connect(url.__str__())

    @staticmethod
    def delete_db(url):

        drop_database(url)

    @staticmethod
    def apply_schema_dict(db, schema_dict):
        """
        Initialise database with defined schema

        :type db: dataset.Dataset
        :param db: empty database to initialise

        :type schema_dict: dict
        :param schema_dict: dictionary defining database schema
        """

        db.begin()

        table_names = schema_dict.keys()

        for table_name in table_names:

            # Unpack table info
            table_dict = schema_dict[table_name]
            columns_dict = table_dict["columns"]

            # Get primary key info
            primary_key = table_dict["primary_key"] if "primary_key" in table_dict else None

            primary_db_type = None
            if primary_key is not None:
                primary_column_dict = columns_dict.pop(primary_key)
                primary_python_type = primary_column_dict["type"]
                primary_db_type = DatabaseUtil.get_db_type(primary_python_type)

            # Create table
            tbl = db.create_table(table_name, primary_id=primary_key, primary_type=primary_db_type)

            # Add columns
            column_names = columns_dict.keys()
            for column in column_names:
                column_dict = columns_dict[column]
                column_python_type = column_dict.pop("type")
                column_db_type = DatabaseUtil.get_db_type(column_python_type)

                fk = False
                fk_val = None
                if "foreign_key" in column_dict:
                    fk_val = column_dict.pop("foreign_key")
                    fk = True

                tbl.create_column(column, column_db_type, **column_dict)
                if fk:
                    column_dict["foreign_key"] = fk_val
        db.commit()

        # Update with foreign keys
        for table_name in table_names:
            table_dict = schema_dict[table_name]
            columns_dict = table_dict["columns"]
            column_names = columns_dict.keys()

            for column in column_names:
                column_dict = columns_dict[column]

                if "foreign_key" in column_dict:
                    DatabaseUtil.update_to_foreign_key(db, table_name, column,
                                                       column_dict["foreign_key"]["reference_table"],
                                                       column_dict["foreign_key"]["reference_column"])

    @staticmethod
    def update_to_foreign_key(db, table, column, reference_table, reference_column):
        """
        Update database to set column as foreign key to reference table and column

        :type db: dataset.Dataset
        :param db: empty database to initialise

        :type table: str
        :param table: name of table with column to set as foreign key

        :type column: str
        :param column: name of column to set as foreign key

        :type reference_table: str
        :param reference_table: name of table with column to set foreign key to

        :type reference_column: str
        :param reference_column: name of column to set foreign key to
        """

        if db.engine.name == "sqlite":
            raise TypeError("cannot add foreign keys to sqlite database")

        db.begin()

        query_string = "ALTER TABLE " + table + ""\
                       " ADD FOREIGN KEY ("+column+")"\
                       " REFERENCES "+reference_table+"("+reference_column+");"

        db.query(query_string)

        db.commit()

    @staticmethod
    def get_db_type(python_type):
        """
        Returns sqlalchemy type equivalent to given python type

        :type python_type: type
        :param python_type: python type

        :return: equivalent sqlalchemy type
        :rtype: sqlalchemy.sql.visitors.VisitableType
        """

        db_types = Types()

        if python_type == bool:
            return db_types.boolean
        elif python_type == int:
            return db_types.bigint
        elif python_type == float:
            return db_types.float
        elif python_type == datetime:
            return db_types.datetime
        elif python_type == date:
            return db_types.date
        elif python_type == dict:
            return db_types.json
        else:
            return db_types.text


if __name__ == '__main__':
    pass
