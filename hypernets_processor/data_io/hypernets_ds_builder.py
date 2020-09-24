"""
HypernetsDSBuilder class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.template_util import create_template_dataset
from hypernets_processor.data_io.product_name_util import ProductNameUtil
from hypernets_processor.data_io.format.metadata import METADATA_DEFS
from hypernets_processor.data_io.format.variables import VARIABLES_DICT_DEFS


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "6/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


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

    def create_ds_template(self, dim_sizes_dict, ds_format, propagate_ds=None):
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
            variables_dict = self.variables_dict_defs[ds_format]
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

            metadata_db = self.context.metadata_db
            print(metadata_db)

            # Evaluate queries for metadata_db to populate product metadata
            metadata_db_query = None
            if self.context.metadata_db is not None:
                metadata_db_query = {}

        # Set product_name metadata
        pu = ProductNameUtil(context=self.context)
        metadata["product_name"] = pu.create_product_name(ds_format)

        return create_template_dataset(
            variables_dict,
            dim_sizes_dict,
            metadata=metadata,
            propagate_ds=propagate_ds,
            metadata_db=metadata_db,
            metadata_db_query=metadata_db_query,
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


if __name__ == "__main__":
    pass
