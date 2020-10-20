"""
HypernetsDBBuilder class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.database_util import create_template_db
from hypernets_processor.data_io.format.databases import DB_DICT_DEFS
from sqlalchemy_utils import database_exists
from sqlalchemy.engine.url import make_url
import dataset
from os import makedirs
from os.path import dirname


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "24/7/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def open_database(url, create_format=None):
    """
    Opens database, optionally creates if doesn't exist

    :return: opened database
    :rtype: dataset.Database
    """

    if database_exists(url):
        return dataset.connect(url)
    elif create_format is not None:
        url_ = make_url(url)
        if url_.drivername == "sqlite":
            makedirs(dirname(url_.database), exist_ok=True)

        hdb = HypernetsDBBuilder()
        return hdb.create_db_template(url, create_format)
    return None


class HypernetsDBBuilder:
    """
    Class to generate SQL database in the Hypernets database format specification
    """

    @staticmethod
    def create_db_template(url, db_format, db_format_defs=DB_DICT_DEFS):
        """
        Returns empty Hypernets database

        :type url: str
        :param url: url of database to create

        :type db_format: str
        :param db_format: product format string

        :type db_format_defs: dict
        :param db_format_defs: dictionary of schema_dict/schema_sql for each database format

        :return: Empty database
        :rtype: dataset.Database
        """

        format_def = db_format_defs[db_format]

        schema_dict = format_def if isinstance(format_def, dict) else None
        schema_sql = format_def if isinstance(format_def, str) else None

        return create_template_db(url, schema_dict=schema_dict, schema_sql=schema_sql)


if __name__ == "__main__":
    pass
