"""
HypernetsDSBuilder class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.template_util import create_template_dataset
from hypernets_processor.data_io.product_name_util import ProductNameUtil
from hypernets_processor.data_io.format.metadata import METADATA_DEFS
from hypernets_processor.data_io.format.variables import VARIABLES_DICT_DEFS


'''___Authorship___'''
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
    """

    @staticmethod
    def create_ds_template(dim_sizes_dict, ds_format, site=None, time=None, propagate_ds=None,
                           metadata_db=None, metadata_db_query=None,
                           variables_dict_defs=VARIABLES_DICT_DEFS, metadata_defs=METADATA_DEFS):
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

        :type variables_dict_defs: dict
        :param variables_dict_defs: dictionary of variables_dict for each product format (default is Hypernets formats)

        :type metadata_defs: dict
        :param metadata_defs: dictionary of metadata for each product format (default is Hypernets formats)

        :return: Empty dataset
        :rtype: xarray.Dataset
        """

        # Find variables
        if ds_format in variables_dict_defs.keys():
            variables_dict = variables_dict_defs[ds_format]
        else:
            raise NameError("Invalid format name: " + ds_format + " - must be one of " +
                            str(variables_dict_defs.keys()))

        # Find metadata def
        if ds_format in metadata_defs.keys():
            metadata = metadata_defs[ds_format]

        else:
            raise RuntimeWarning("No metadata found for file type " + str(ds_format))

        # todo - should get metadata_db and build query from context

        # # Set product_name metadata
        # pu = ProductNameUtil
        # metadata["product_name"] = pu.create_file_name_l1a_rad(network, site, time, version)

        return create_template_dataset(variables_dict, dim_sizes_dict, metadata=metadata, propagate_ds=propagate_ds,
                                       metadata_db=metadata_db, metadata_db_query=metadata_db_query)

    # todo - add method to return available ds_formats


if __name__ == '__main__':
    pass
