"""
test_functions module - module with functions to help with testing
"""
from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_db_builder import HypernetsDBBuilder
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.format.variables import VARIABLES_DICT_DEFS
from hypernets_processor.context import Context
from hypernets_processor.cli.common import read_config_file, configure_logging
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

this_directory = os.path.dirname(__file__)
TEMPLATE_PROCESSOR_CONFIG_PATH = relative_path(
    "../etc/processor.config", this_directory
)
TEMPLATE_JOB_CONFIG_PATH = relative_path(
    "../cli/config_templates/job.config", this_directory
)

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


def setup_test_anomoly_db(url):
    """
    Creates anomoly_db for testing, populated with test data

    :type url: str
    :param url: database url
    """

    db = HypernetsDBBuilder.create_db_template(url, "anomoly")

    # todo - add test data to test anomoly db

    db.commit()
    del db


def setup_test_processor_config(archive_directory=None, metadata_db_url=None):
    """
    Creates processor_config for testing

    :type archive_directory: str
    :param archive_directory: (optional) data archive directory, set if provided else default value used

    :type metadata_db_url: str
    :param metadata_db_url: (optional) metadata db url, set if provided else default value used

    :return: test processor configuration information
    :rtype: configparser.RawConfigParser
    """

    processor_config = read_config_file(TEMPLATE_PROCESSOR_CONFIG_PATH)

    processor_config["Processor"]["version"] = "0.0"

    processor_config["Input"]["metadata_db_url"] = (
        metadata_db_url if metadata_db_url is not None else "sqlite:///metadata.db"
    )

    processor_config["Output"]["archive_directory"] = (
        archive_directory if archive_directory is not None else "out"
    )

    processor_config["Processing Options"] = {"write_l1a": "False"}

    return processor_config


def setup_test_job_config(raw_data_directory=None, anomoly_db_url=None):
    """
    Creates processor_config for testing

    :type raw_data_directory: str
    :param raw_data_directory: (optional) raw data directory, set if provided else default value used

    :type anomoly_db_url: str
    :param anomoly_db_url: (opitional) anomoly db url, set if provided

    :return: test job configuration information
    :rtype: configparser.RawConfigParser
    """

    job_config = read_config_file(TEMPLATE_JOB_CONFIG_PATH)

    job_config["Info"]["network"] = "land"
    job_config["Info"]["site"] = "site"

    job_config["Input"]["raw_data_directory"] = (
        raw_data_directory if raw_data_directory is not None else "data"
    )
    job_config["Output"]["anomoly_db_url"] = (
        anomoly_db_url if anomoly_db_url is not None else "sqlite:///anomoly.db"
    )

    job_config["Processing Options"][
        "measurement_function_name"
    ] = "standard_measurement_function"
    job_config["Processing Options"]["reflectance_protocol_name"] = "standard_protocol"
    job_config["Processing Options"]["write_l1a"] = "True"

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
    anomoly_db_url=None,
    metadata_db_url=None,
    create_directories=False,
    create_dbs=False,
):
    """
    Creates context for testing

    :type archive_directory: str
    :param archive_directory: (optional) data archive directory, set if provided else default value used

    :type metadata_db_url: str
    :param metadata_db_url: (optional) metadata db url, set if provided else default value used

    :type raw_data_directory: str
    :param raw_data_directory: (optional) raw data directory, set if provided else default value used

    :type anomoly_db_url: str
    :param anomoly_db_url: (opitional) anomoly db url, set if provided

    :type create_directories: bool
    :param create_directories: option to create test directories at specified paths (default: False)

    :type create_dbs: bool
    :param create_dbs: option to create test databases at specified urls (default: False)

    :return: test context
    :rtype: hypernets_processor.context.Context
    """

    processor_config = setup_test_processor_config(
        archive_directory=archive_directory, metadata_db_url=metadata_db_url
    )
    job_config = setup_test_job_config(
        raw_data_directory=raw_data_directory, anomoly_db_url=anomoly_db_url
    )
    logger = setup_test_logger()

    if create_directories:
        os.makedirs(processor_config["Output"]["archive_directory"])
        os.makedirs(job_config["Input"]["raw_data_directory"])

    if create_dbs:
        setup_test_metadata_db(processor_config["Input"]["metadata_db_url"])
        setup_test_anomoly_db(job_config["Output"]["anomoly_db_url"])

    context = Context(
        processor_config=processor_config, job_config=job_config, logger=logger
    )

    if not create_dbs:
        del context.metadata_db
        context.metadata_db = None

        del context.anomoly_db
        context.anomoly_db = None

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

        anomoly_db_path = context.anomoly_db.engine.url.database
        del context.anomoly_db
        os.remove(anomoly_db_path)

    if remove_directories:
        shutil.rmtree(context.archive_directory)
        shutil.rmtree(context.raw_data_directory)


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
