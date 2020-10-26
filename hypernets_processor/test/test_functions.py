"""
test_functions module - module with functions to help with testing
"""
from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_db_builder import HypernetsDBBuilder
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.context import Context
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.utils.logging import configure_logging
from hypernets_processor.utils.config import (
    PROCESSOR_CONFIG_PATH,
    JOB_CONFIG_TEMPLATE_PATH,
)
from hypernets_processor.utils.paths import relative_path
import datetime
import os
import shutil
import numpy as np
from copy import copy


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


TEST_DS_DIM_SIZES_W = {"wavelength": 271, "series": 3, "scan": 10, "sequence": 1}

TEST_DS_DIM_SIZES_L = {"wavelength": 271, "series": 20, "scan": 10, "sequence": 1}


def setup_test_metadata_db(url):
    """
    Creates metadata_db for testing, populated with test data

    :type url: str
    :param url: database url
    """

    db = HypernetsDBBuilder.create_db_template(url, "metadata")

    # todo - add test data to test metadata db

    db.commit()
    del db


def setup_test_anomaly_db(url):
    """
    Creates anomaly_db for testing, populated with test data

    :type url: str
    :param url: database url
    """

    db = HypernetsDBBuilder.create_db_template(url, "anomaly")

    db["anomalies"].insert(
        dict(
            anomaly="anomaly_name",
            raw_product_name="SEQ20200311T112430",
            site="site",
        )
    )

    db.commit()
    del db


def setup_test_archive_db(url):
    """
    Creates archive_db for testing, populated with test data

    :type url: str
    :param url: database url
    """

    db = HypernetsDBBuilder.create_db_template(url, "archive")

    db["products"].insert(
        dict(
            product_name="new_product1",
            raw_product_name="SEQ20200311T112130",
            site="site",
        )
    )
    db["products"].insert(
        dict(
            product_name="new_product2",
            raw_product_name="SEQ20200311T112230",
            site="site",
        )
    )
    db["products"].insert(
        dict(
            product_name="new_product3",
            raw_product_name="SEQ20200311T112430",
            site="site",
        )
    )

    db.commit()
    del db


def setup_test_processor_config(
    archive_directory=None,
    metadata_db_url=None,
    archive_db_url=None,
    anomaly_db_url=None,
):
    """
    Creates processor_config for testing

    :type archive_directory: str
    :param archive_directory: (optional) data archive directory, set if provided else default value used

    :type metadata_db_url: str
    :param metadata_db_url: (optional) metadata db url, set if provided else default value used

    :type archive_db_url: str
    :param archive_db_url: (optional) archive db url, set if provided else default value used

    :type anomaly_db_url: str
    :param anomaly_db_url: (optional) anomaly db url, set if provided else default value used

    :return: test processor configuration information
    :rtype: configparser.RawConfigParser
    """

    processor_config = read_config_file(PROCESSOR_CONFIG_PATH)

    processor_config["Processor"]["version"] = "0.0"

    processor_config["Databases"]["metadata_db_url"] = (
        metadata_db_url if metadata_db_url is not None else "sqlite:///metadata.db"
    )

    processor_config["Databases"]["anomaly_db_url"] = (
        anomaly_db_url if anomaly_db_url is not None else "sqlite:///anomaly.db"
    )

    processor_config["Databases"]["archive_db_url"] = (
        archive_db_url if archive_db_url is not None else "sqlite:///archive.db"
    )

    processor_config["Output"]["archive_directory"] = (
        archive_directory if archive_directory is not None else "out"
    )

    processor_config["Processing Options"] = {"write_l1a": "False"}

    return processor_config


def setup_test_job_config(raw_data_directory=None):
    """
    Creates processor_config for testing

    :type raw_data_directory: str
    :param raw_data_directory: (optional) raw data directory, set if provided else default value used

    :return: test job configuration information
    :rtype: configparser.RawConfigParser
    """
    job_config = read_config_file(JOB_CONFIG_TEMPLATE_PATH)

    job_config["Job"]["network"] = "land"
    job_config["Job"]["site"] = "site"

    job_config["Input"]["raw_data_directory"] = (
        raw_data_directory if raw_data_directory is not None else "data"
    )

    return job_config


def setup_test_logger():
    """
    Creates logger for testing

    :return: test logger
    :rtype: logging.Logger
    """

    return configure_logging()


def setup_test_context(
    raw_data_directory=None,
    archive_directory=None,
    anomaly_db_url=None,
    metadata_db_url=None,
    archive_db_url=None,
    create_directories=False,
    create_dbs=False,
):
    """
    Creates context for testing

    :type raw_data_directory: str
    :param raw_data_directory: (optional) raw data directory, set if provided else default value used

    :type archive_directory: str
    :param archive_directory: (optional) data archive directory, set if provided else default value used

    :type anomaly_db_url: str
    :param anomaly_db_url: (opitional) anomaly db url, set if provided

    :type metadata_db_url: str
    :param metadata_db_url: (optional) metadata db url, set if provided else default value used

    :type archive_db_url: str
    :param archive_db_url: (opitional) archive db url, set if provided

    :type create_directories: bool
    :param create_directories: option to create test directories at specified paths (default: False)

    :type create_dbs: bool
    :param create_dbs: option to create test databases at specified urls (default: False)

    :return: test context
    :rtype: hypernets_processor.context.Context
    """

    processor_config = setup_test_processor_config(
        archive_directory=archive_directory,
        metadata_db_url=metadata_db_url,
        anomaly_db_url=anomaly_db_url,
        archive_db_url=archive_db_url,
    )
    job_config = setup_test_job_config(raw_data_directory=raw_data_directory)

    logger = setup_test_logger()

    if create_directories:
        os.makedirs(processor_config["Output"]["archive_directory"])
        os.makedirs(job_config["Input"]["raw_data_directory"])
        os.makedirs(
            os.path.join(
                job_config["Input"]["raw_data_directory"], "SEQ20200311T112230"
            )
        )
        os.makedirs(
            os.path.join(
                job_config["Input"]["raw_data_directory"], "SEQ20200311T112330"
            )
        )
        os.makedirs(
            os.path.join(
                job_config["Input"]["raw_data_directory"], "SEQ20200311T112430"
            )
        )
        os.makedirs(
            os.path.join(
                job_config["Input"]["raw_data_directory"], "SEQ20200311T112530"
            )
        )

    if create_dbs:
        setup_test_metadata_db(processor_config["Databases"]["metadata_db_url"])
        setup_test_anomaly_db(processor_config["Databases"]["anomaly_db_url"])
        setup_test_archive_db(processor_config["Databases"]["archive_db_url"])

    if not create_dbs:
        processor_config["Databases"]["metadata_db_url"] = None
        processor_config["Databases"]["anomaly_db_url"] = None
        processor_config["Databases"]["archive_db_url"] = None

    context = Context(
        processor_config=processor_config, job_config=job_config, logger=logger
    )

    context.set_config_value("time", datetime.datetime(2021, 4, 3, 11, 21, 15))

    return context


def teardown_test_context(context, remove_directories=False, remove_dbs=False):
    """
    Removes test context and files

    :type context: hypernets_processor.context.Context
    :param context: context to teardown

    :type remove_directories: bool
    :param remove_dbs: option to remove test data directories (default: False)

    :type remove_dbs: bool
    :param remove_dbs: option to remove test database files (default: False)
    """

    if remove_dbs:
        metadata_db_path = context.metadata_db.engine.url.database
        del context.metadata_db
        os.remove(metadata_db_path)

        anomaly_db_path = context.anomaly_db.engine.url.database
        del context.anomaly_db
        os.remove(anomaly_db_path)

        archive_db_path = context.archive_db.engine.url.database
        del context.archive_db
        os.remove(archive_db_path)

    if remove_directories:
        shutil.rmtree(context.get_config_value("archive_directory"))
        shutil.rmtree(context.get_config_value("raw_data_directory"))


def create_test_ds(ds_format):
    """
    Returns sample ds with random data

    :type ds_format: str
    :param ds_format: format string of dataset

    :return: test ds
    :rtype: xarray.Dataset
    """

    context = setup_test_context()
    dsb = HypernetsDSBuilder(context=context)

    dim_sizes_dict = dsb.create_empty_dim_sizes_dict(ds_format)
    variable_names = dsb.return_ds_format_variable_names(ds_format)

    dim_values = TEST_DS_DIM_SIZES_L
    if ds_format[0] == "W":
        dim_values = TEST_DS_DIM_SIZES_W

    for k in dim_sizes_dict.keys():
        dim_sizes_dict[k] = dim_values[k]

    ds = dsb.create_ds_template(dim_sizes_dict, ds_format)

    remaining_variables = copy(variable_names)
    for variable_name in variable_names:
        if variable_name == "wavelength":
            wavelength_data = np.concatenate(
                (np.arange(400, 1000, 3), np.arange(1000, 1700 + 10, 10))
            )
            ds = ds.assign_coords(
                coords={"wavelength": ds.wavelength.copy(data=wavelength_data).variable}
            )

        elif variable_name == "bandwidth":
            ds[variable_name].data = np.random.normal(
                1.0, 0.5, len(ds[variable_name].data)
            )

        elif variable_name == "acquisition_time":
            ds[variable_name].data = np.arange(
                10000, 10000 + len(ds[variable_name].data), dtype=int
            )

        # geometry data
        elif "angle" in variable_name:
            ds[variable_name].data = np.linspace(30, 60, len(ds[variable_name].data))

        # geometry data
        elif "acceleration" in variable_name:
            ds[variable_name].data = np.random.normal(
                1.0, 0.5, ds[variable_name].data.shape
            )

        # observation data
        elif "reflectance" in variable_name:
            if variable_name[0] == "u":
                ds[variable_name].data = np.random.normal(
                    1.0, 0.5, ds[variable_name].data.shape
                )
            if variable_name[:3] == "cov":
                ds[variable_name].data = np.random.normal(
                    1.0, 0.5, ds[variable_name].data.shape
                )
            else:
                ds[variable_name].data = np.round(
                    np.random.rand(*ds[variable_name].data.shape), 3
                )

        elif "radiance" in variable_name:
            if variable_name[0] == "u":
                ds[variable_name].data = np.random.normal(
                    1.0, 0.5, ds[variable_name].data.shape
                )
            if variable_name[:3] == "cov":
                ds[variable_name].data = np.random.normal(
                    1.0, 0.5, ds[variable_name].data.shape
                )
            else:
                ds[variable_name].data = np.round(
                    np.random.rand(*ds[variable_name].data.shape) * 100, 3
                )

        elif "digital_number" in variable_name:
            if variable_name[0] == "u":
                ds[variable_name].data = np.random.normal(
                    1.0, 0.5, ds[variable_name].data.shape
                )
            if variable_name[:3] == "cov":
                ds[variable_name].data = np.random.normal(
                    1.0, 0.5, ds[variable_name].data.shape
                )
            else:
                ds[variable_name].data = (
                    np.random.rand(*ds[variable_name].data.shape) * 200
                ).astype(int)

        else:
            continue

        remaining_variables.remove(variable_name)

    remaining_variables.remove("quality_flag")

    return ds


if __name__ == "__main__":
    create_test_ds("W_L1B")
    pass
