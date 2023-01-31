"""
HypernetsDBBuilder class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.database_util import create_template_db
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.format.databases import DB_DICT_DEFS
from hypernets_processor.data_io.format.anomalies import ANOMALIES_DICT

from sqlalchemy_utils import database_exists
from sqlalchemy.engine.url import make_url
import dataset
from os import makedirs
from os.path import dirname
import numpy as np

"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "24/7/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def open_database(url, db_format=None, context=None):
    """
    Opens database, creates if doesn't exist

    :type url: str
    :param url: url of database to create

    :type db_format: str
    :param db_format: product format string

    :type context: hypernets_processor.context.Context
    :param context: processor context

    :return: opened database
    :rtype: dataset.Database
    """
    if database_exists(url):

        if db_format == "archive":
            return ArchiveDB(url, context)
        elif db_format == "anomaly":
            return AnomalyDB(url, context)
        elif db_format == "metadata":
            return MetadataDB(url, context)
        return dataset.connect(url)

    elif db_format is not None:
        url_ = make_url(url)
        if url_.drivername == "sqlite":
            makedirs(dirname(url_.database), exist_ok=True)

        hdb = HypernetsDBBuilder(context)
        return hdb.create_db_template(url, db_format)

    return None


class HypernetsDBBuilder:
    """
    Class to generate SQL database in the Hypernets database format specification

    :type context: hypernets_processor.context.Context
    :param context: processor context
    """

    def __init__(self, context=None):
        self.context = context

    def create_db_template(self, url, db_format, db_format_defs=DB_DICT_DEFS):
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

        db = create_template_db(url, schema_dict=schema_dict, schema_sql=schema_sql)

        if db_format == "archive":
            db.__class__ = ArchiveDB
            db.context = self.context
            db.writer = HypernetsWriter(self.context)

        elif db_format == "anomaly":
            db.__class__ = AnomalyDB
            db.context = self.context
            db.anomalies_dict = ANOMALIES_DICT

        elif db_format == "metadata":
            db.__class__ = MetadataDB
            db.context = self.context

        return db


class ArchiveDB(dataset.Database):
    """
    Class for handling Archive Database in memory, inherits from dataset.Databases

    :type url: str
    :param url: database url

    :type context: hypernets_processor.context.Context
    :param context: processor context
    """

    def __init__(self, url, context):
        self.context = context
        self.writer = HypernetsWriter(context)
        super().__init__(url)

    def archive_product(self, ds, path):
        """
        Adds product to archive database

        :type ds: xarray.dataset
        :param ds: product to archive

        :type path: str
        :param path: path product is being written to
        """

        tbl = self.get_table("products")
        tbl.insert(
            dict(
                product_name=ds.attrs["product_name"],
                product_path=path,
                product_level=ds.attrs["product_level"],
                datetime=self.context.get_config_value("time"),
                sequence_name=self.context.get_config_value("sequence_name"),
                sequence_path=self.context.get_config_value("sequence_path"),
                site_id=ds.attrs["site_id"],
                system_id=ds.attrs["system_id"],
                plot_path=self.writer.return_plot_directory(),
                image_path=self.writer.return_image_directory(),
                solar_zenith_angle_min=np.min(ds["solar_zenith_angle"].values),
                solar_zenith_angle_max=np.max(ds["solar_zenith_angle"].values),
                solar_azimuth_angle_min=np.min(ds["solar_azimuth_angle"].values),
                solar_azimuth_angle_max=np.max(ds["solar_azimuth_angle"].values),
                viewing_zenith_angle_min=np.min(ds["viewing_zenith_angle"].values),
                viewing_zenith_angle_max=np.max(ds["viewing_zenith_angle"].values),
                viewing_azimuth_angle_min=np.min(ds["viewing_azimuth_angle"].values),
                viewing_azimuth_angle_max=np.max(ds["viewing_azimuth_angle"].values),
            )
        )


class AnomalyDB(dataset.Database):
    """
    Class for handling Anomaly Database in memory, inherits from dataset.Databases

    :type url: str
    :param url: database url

    :type context: hypernets_processor.context.Context
    :param context: processor context
    """

    def __init__(self, url, context):
        self.context = context
        super().__init__(url)

    def add_anomaly(self, anomaly_id):
        """
        Adds anomaly to anomaly database

        :type anomaly_id: str
        :param anomaly_id: anomaly id, must match name of entry in self.anomalies dict
        """

        # Add anomaly to db
        tbl = self.get_table("anomalies")
        tbl.insert(
            dict(
                anomaly_id=anomaly_id,
                sequence_name=self.context.get_config_value("sequence_name"),
                sequence_path=self.context.get_config_value("sequence_path"),
                site_id=self.context.get_config_value("site_id"),
                system_id=self.context.get_config_value("system_id"),
                datetime=self.context.get_config_value("time"),
            )
        )

    def get_sequence_anomalies(self, sequence_name=None, site_id=None):
        """
        Returns anomaly ids of anomalies currently registered for the processed sequence if context attribute is not
        None, else define of interest

        :type sequence_name: str
        :param sequence_name: (optional) name of sequence to lookup anomaly ids for, if omitted gets sequence id from
        context, if avaiable

        :type site_id: str
        :param site_id: (optional) name of site to lookup anomaly ids for, if omitted gets site id from
        context, if avaiable

        :rtype: list
        :return: sequence anomaly ids
        """

        if self.context is not None:
            sequence_name = self.context.get_config_value("sequence_name")
            site_id = self.context.get_config_value("site_id")

        anomalies = [
            product["anomaly_id"]
            for product in self.__getitem__("anomalies").find(
                site_id=site_id,
                sequence_name=sequence_name,
            )
        ]

        return anomalies


class MetadataDB(dataset.Database):
    """
    Class for handling Metadata Database in memory, inherits from dataset.Databases

    :type url: str
    :param url: database url

    :type context: hypernets_processor.context.Context
    :param context: processor context
    """

    def __init__(self, url, context):
        self.context = context
        super().__init__(url)


if __name__ == "__main__":
    pass
