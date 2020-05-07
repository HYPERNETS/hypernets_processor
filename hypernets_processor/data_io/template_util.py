"""
TemplateUtil class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil
import xarray


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def create_template_dataset(variables_dict, dim_sizes_dict, metadata=None):
    """
    Returns template dataset

    :type variables_dict: dict
    :type variables_dict: dictionary defining variables

    :type dim_sizes_dict: dict
    :param dim_sizes_dict: entry per dataset dimension with value of size as int

    :type metadata: dict
    :param metadata: (optional) dictionary of dataset metadata

    :return ds: template dataset
    :rtype: xarray.Dataset
    """

    # Create dataset
    ds = xarray.Dataset()

    # Add variables
    ds = TemplateUtil.add_variables(ds, variables_dict, dim_sizes_dict)

    # Add metadata
    if metadata is not None:
        ds = TemplateUtil.add_metadata(ds, metadata)

    return ds


class TemplateUtil:
    """
    Class to create template Hypernets datasets by interfacing with the format subpackage
    """

    @staticmethod
    def add_variables(ds, variables_dict, dim_sizes_dict):
        """
        Adds defined variables dataset

        :type ds: xarray.Dataset
        :param ds: dataset

        :type variables_dict: dict
        :type variables_dict: dictionary defining variables

        :type dim_sizes_dict: dict
        :param dim_sizes_dict: entry per dataset dimension with value of size as int

        :return: dataset with defined variables
        :rtype: xarray.Dataset
        """

        du = DatasetUtil()

        for variable_name in variables_dict.keys():

            variable_attrs = variables_dict[variable_name]

            # Check variable definition
            TemplateUtil._check_variable_definition(variable_name, variable_attrs)

            # Unpack variable attributes
            dtype = variable_attrs["dtype"]
            dim_names = variable_attrs["dim"]
            attributes = variable_attrs["attributes"] if "attributes" in variable_attrs else None

            # Determine variable shape from dims
            dim_sizes = TemplateUtil._return_variable_shape(dim_names, dim_sizes_dict)

            # Create variable and add to dataset
            if dtype == "flag":
                flag_meanings = attributes.pop("flag_meanings")
                variable = du.create_flags_variable(dim_sizes, meanings=flag_meanings,
                                                    dim_names=dim_names, attributes=attributes)

            else:
                variable = du.create_variable(dim_sizes, dim_names=dim_names,
                                              dtype=dtype, attributes=attributes)

                if "encoding" in variable_attrs:
                    du.add_encoding(variable, **variable_attrs["encoding"])

            ds[variable_name] = variable

        return ds

    @staticmethod
    def _check_variable_definition(variable_name, variable_attrs):
        """
        Checks validity of variable definition, raising errors as appropriate

        :type variable_name: str
        :param variable_name: variable name

        :type variable_attrs: dict
        :param variable_attrs: variable defining dictionary
        """

        # Variable name must be type str
        if type(variable_name) != str:
            raise TypeError("Invalid variable name: "+str(variable_name)+" (must be string)")

        # todo - add more tests to check validity of variable definition

    @staticmethod
    def _return_variable_shape(dim_names, dim_sizes_dict):
        """
        Returns dimension sizes of specified dimensions

        :type dim_names: list
        :param dim_names: (optional) dimension names as strings, i.e. ["dim1_name", "dim2_name", "dim3_size"]

        :type dim_sizes_dict: dict
        :param dim_sizes_dict: entry per dataset dimension with value of size as int

        :return: dimension sizes as ints, i.e. [dim1_size, dim2_size, dim3_size] (e.g. [2,3,5])
        :rtype: list
        """

        return [dim_sizes_dict[dim_name] for dim_name in dim_names]

    @staticmethod
    def add_metadata(ds, metadata):
        """
        Adds metadata to dataset

        :type ds: xarray.Dataset
        :param ds: dataset

        :type metadata: dict
        :param metadata: dictionary of dataset metadata

        :return: dataset with updated metadata
        :rtype: xarray.Dataset
        """

        ds.attrs.update(metadata)

        return ds


if __name__ == '__main__':
    pass
