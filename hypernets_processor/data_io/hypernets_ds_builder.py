"""
HypernetsDSBuilder class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.template_util import create_template_dataset
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
    formats and interfacing with the TemplateUtil tool.
    """

    @staticmethod
    def create_ds_template(dim_sizes_dict, ds_format, variables_dict_defs=VARIABLES_DICT_DEFS,
                           metadata_defs=METADATA_DEFS):
        """
        Returns empty Hypernets dataset

        :type dim_sizes_dict: dict
        :param dim_sizes_dict: entry per dataset dimension with value of size as int

        :type ds_format: str
        :param ds_format: product format string

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

        # Find metadata
        if ds_format in metadata_defs:
            metadata = metadata_defs[ds_format]
        else:
            raise RuntimeWarning("No metadata found for file type " + str(ds_format))

        return create_template_dataset(variables_dict, dim_sizes_dict, metadata)

    # todo - add method to return available ds_formats


if __name__ == '__main__':
    pass