"""
HypernetsDSBuilder class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.product_name_util import ProductNameUtil
from hypernets_processor.data_io.format.metadata import METADATA_DEFS
from hypernets_processor.data_io.format.variables import VARIABLES_DICT_DEFS

from datetime import datetime
import obsarray
import copy

"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "6/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

version = __version__


class HypernetsDSBuilder:
    """
    Class to generate xarray Datasets in the Hypernets file format specification, handling the library of defined file
    formats, metadata database and interfacing with the TemplateUtil tool.

    :type context: hypernets_processor.context.Context
    :param context: processor state defining context object

    :type variables_dict_defs: dict
    :param variables_dict_defs: dictionary of variables_dict for each product format (default is Hypernets formats)

    :type metadata_defs: dict
    :param metadata_defs: dictionary of metadata for each product format (default is Hypernets formats)
    """

    def __init__(
        self,
        context=None,
        variables_dict_defs=VARIABLES_DICT_DEFS,
        metadata_defs=METADATA_DEFS,
    ):
        self.context = context
        self.variables_dict_defs = variables_dict_defs
        self.metadata_defs = metadata_defs

    def create_ds_template(
        self,
        dim_sizes_dict: object,
        ds_format: object,
        propagate_ds: object = None,
        swir: object = False,
        angles: object = False,
        ds=None,
    ) -> object:

        """
        Returns empty Hypernets dataset

        :type dim_sizes_dict: dict
        :param dim_sizes_dict: entry per dataset dimension with value of size as int

        :type ds_format: str
        :param ds_format: product format string

        :type propagate_ds: xarray.Dataset
        :param propagate_ds: (optional) template dataset is populated with data from propagate_ds for their variables
        with common names and dimensions. Useful for transferring common data between datasets at different processing
        levels (e.g. times, etc.).

        N.B. propagates data only, not variables as a whole with attributes etc.

        :return: Empty dataset
        :rtype: xarray.Dataset
        """

        # Find variables
        if ds_format in self.return_ds_formats():
            variables_dict = copy.deepcopy(self.variables_dict_defs[ds_format])
        else:
            raise NameError(
                "Invalid format name: "
                + ds_format
                + " - must be one of "
                + str(self.variables_dict_defs.keys())
            )

        # Find metadata def
        metadata = {}
        if ds_format in self.metadata_defs.keys():
            metadata = self.metadata_defs[ds_format]

        else:
            raise RuntimeWarning("No metadata found for file type " + str(ds_format))

        metadata_db = None
        metadata_db_query = None

        if self.context is not None:
            metadata["responsible_party"] = self.context.get_config_value(
                "responsible_party"
            )
            metadata["creator_name"] = self.context.get_config_value("creator_name")
            metadata["creator_email"] = self.context.get_config_value("creator_email")

            metadata_db = self.context.metadata_db

            # Evaluate queries for metadata_db to populate product metadata
            metadata_db_query = None
            if self.context.metadata_db is not None:
                metadata_db_query = None

        # Set product_name metadata
        pu = ProductNameUtil(context=self.context)
        metadata["product_name"] = pu.create_product_name(
            ds_format, swir=swir, angles=angles
        )
        metadata["product_level"] = str(ds_format)
        metadata["data_created"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        if ds_format == "CAL":
            # calibration metadata
            metadata["data_created"] = "TBD"  # should be the calibration data
        else:
            hypstar = "hypstar_" + str(
                self.context.get_config_value("hypstar_cal_number")
            )
            if ds is not None:
                hypstar = "hypstar_" + str(ds.attrs["instrument_id"])
                metadata["site_latitude"] = ds.attrs["site_latitude"]
                metadata["site_longitude"] = ds.attrs["site_longitude"]
                metadata["source_file"] = ds.attrs["source_file"]
                metadata["sequence_id"] = ds.attrs["sequence_id"]
                metadata["instrument_id"] = ds.attrs["instrument_id"]
                metadata["site_id"] = ds.attrs["site_id"]
                metadata["system_temperature"] = ds.attrs["system_temperature"]
                metadata["system_relative_humidity"] = ds.attrs[
                    "system_relative_humidity"
                ]
                metadata["system_pressure"] = ds.attrs["system_pressure"]
                metadata["illuminance"] = ds.attrs["illuminance"]

            metadata["processor_version"] = str(version)
            metadata["processor_configuration_file"] = "TBD"
            metadata["system_id"] = hypstar.upper()
            # take lat and lon from GPS data from the raw data???? of shouldcome from metadata database?

            if ds_format in ["L_L1A_RAD", "W_L1A_RAD", "L_L1B_RAD"]:
                metadata["instrument_calibration_file_rad"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + "_RAD_v" + str(version) + ".nc"
                )
            if ds_format in ["L_L1A_IRR", "W_L1A_IRR", "L_L1B_IRR"]:
                metadata["instrument_calibration_file_irr"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + "_IRR_v" + str(version) + ".nc"
                )
            if ds_format in ["W_L1B", "L_L1C", "L_L2A"]:
                metadata["instrument_calibration_file_irr"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + "_IRR_v" + str(version) + ".nc"
                )
                metadata["instrument_calibration_file_rad"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + "_RAD_v" + str(version) + ".nc"
                )
            if ds_format in ["W_L1C", "W_L2A"]:
                # W_L1C
                metadata["instrument_calibration_file_rad"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + "_RAD_v" + str(version) + ".nc"
                )
                metadata["instrument_calibration_file_irr"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + "_IRR_v" + str(version) + ".nc"
                )
                metadata["rhof_option"] = self.context.get_config_value("rhof_option")

                wa = self.context.get_config_value("wind_ancillary")
                if not wa:
                    metadata["rhof_wind_source"] = "Default - {}".format(
                        self.context.get_config_value("wind_default")
                    )
                elif wa == "GDAS":
                    metadata["rhof_wind_source"] = "GDAS"
                elif wa == "NCEP":
                    metadata["rhof_wind_source"] = (
                        "The National Centers for Environmental Prediction) "
                        "Reanalysis 2 (NCEPR2) dataset used for the SeaDAS Ocean Color Processing; "
                        "https://oceandata.sci.gsfc.nasa.gov/directdataaccess/Ancillary/GLOBAL"
                    )

                metadata["similarity_waveref"] = self.context.get_config_value(
                    "similarity_wr"
                )
                metadata["similarity_wavethres"] = self.context.get_config_value(
                    "similarity_wp"
                )
                metadata["similarity_wavelen1"] = self.context.get_config_value(
                    "similarity_w1"
                )
                metadata["similarity_wavelen2"] = self.context.get_config_value(
                    "similarity_w2"
                )
                metadata["similarity_alpha"] = self.context.get_config_value(
                    "similarity_alpha"
                )

        if (metadata_db is not None) and (metadata_db_query is not None):
            metadata = self.find_metadata(metadata, metadata_db, metadata_db_query)

        return obsarray.create_ds(
            variables_dict, dim_sizes_dict, metadata=metadata, propagate_ds=propagate_ds
        )

    def return_ds_formats(self):
        """
        Returns available ds format names

        :return: ds formats
        :rtype: list
        """

        return list(self.variables_dict_defs.keys())

    def return_ds_format_variable_names(self, ds_format):
        """
        Returns variables for specified ds format

        :type ds_format: str
        :param ds_format: product format string

        :return: ds format variables
        :rtype: list
        """

        return list(self.variables_dict_defs[ds_format].keys())

    def return_ds_format_variable_dict(self, ds_format, variable_name):
        """
        Returns variable definition info for specified ds format

        :type ds_format: str
        :param ds_format: product format string

        :type variable_name: str
        :param variable_name: variable name

        :return: variable definition info
        :rtype: dict
        """

        return self.variables_dict_defs[ds_format][variable_name]

    def return_ds_format_dim_names(self, ds_format):
        """
        Returns dims required for specified ds format

        :type ds_format: str
        :param ds_format: product format string

        :return: ds format dims
        :rtype: list
        """

        ds_format_def = self.variables_dict_defs[ds_format]

        ds_format_dims = set()

        for var_name in ds_format_def.keys():
            ds_format_dims.update(ds_format_def[var_name]["dim"])

        return list(ds_format_dims)

    def create_empty_dim_sizes_dict(self, ds_format):
        """
        Returns empty dim_size_dict for specified ds format

        :type ds_format: str
        :param ds_format: product format string

        :return: empty dim_size_dict
        :rtype: dict
        """

        dim_sizes_dict = dict()
        for dim in self.return_ds_format_dim_names(ds_format):
            dim_sizes_dict[dim] = None

        return dim_sizes_dict

    @staticmethod
    def find_metadata(metadata, db, query):
        """
        Populate metadata dictionary with values from database query

        :type metadata: dict
        :param metadata: dictionary of dataset metadata

        :type db: dataset.Database
        :param db: metadata database

        :type query: dict/list
        :param query: database query, defined as {"table_name": query_dict} where query_dict defines. Can be a list of
        such database queries
        """

        if isinstance(query, dict):
            query = [query]

        for q in query:
            table_name = list(q.keys())[0]

            row = copy.deepcopy(db[table_name].find_one(**q[table_name]))

            if row is None:
                raise LookupError("query does not find unique metadata value")

            not_required_keys = [
                key for key in row.keys() if key not in metadata.keys()
            ]

            for key in not_required_keys:
                row.pop(key)

            metadata.update(row)

        return metadata


if __name__ == "__main__":
    pass
