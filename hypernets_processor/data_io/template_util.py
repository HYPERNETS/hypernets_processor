"""
TemplateUtil class
"""
from hypernets_processor.data_io.format.flags import FLAG_MEANINGS
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


def create_template_dataset(variables_dict, dim_sizes_dict, metadata=None, propagate_ds=None):
    """
    Returns template dataset

    :type variables_dict: dict
    :type variables_dict: dictionary defining variables

    :type dim_sizes_dict: dict
    :param dim_sizes_dict: entry per dataset dimension with value of size as int

    :type metadata: dict
    :param metadata: (optional) dictionary of dataset metadata

    :type propagate_ds: xarray.Dataset
    :param propagate_ds: (optional) template dataset is populated with data from propagate_ds for their variables with
    common names and dimensions. Useful for transferring common data between datasets at different processing levels
    (e.g. times, etc.).

    N.B. propagates data only, not variables as a whole with attributes etc.

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

    # Propagate variable data
    if propagate_ds is not None:
        TemplateUtil.propagate_values(ds, propagate_ds)

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
            print(variable_name)

            variable_attrs = variables_dict[variable_name]

            # Check variable definition
            TemplateUtil._check_variable_definition(variable_name, variable_attrs)

            # Unpack variable attributes
            dtype = variable_attrs["dtype"]
            dim_names = variable_attrs["dim"]
            attributes = variable_attrs["attributes"] if "attributes" in variable_attrs else None

            # Determine variable shape from dims
            try:
                dim_sizes = TemplateUtil._return_variable_shape(dim_names, dim_sizes_dict)
            except KeyError:
                raise KeyError("Dim Name Error - Variable " + variable_name + " defined with dim not in dim_sizes_dict")

            # Create variable and add to dataset
            if dtype == "flag":
                #print(attributes)
                # why does the flag_meanings does not appear in the attributes????
                flag_meanings = FLAG_MEANINGS #attributes.pop("flag_meanings")
                variable = du.create_flags_variable(dim_sizes, meanings=flag_meanings,
                                                    dim_names=dim_names, attributes=attributes)

            else:
                #print(attributes)
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

    @staticmethod
    def propagate_values(target_ds, source_ds, exclude=None):
        """
        Populates target_ds in-place with data from source_ds for their variables with common names and dimensions.
        Useful for transferring common data between datasets at different processing levels (e.g. times, etc.).

        N.B. propagates data only, not variables as a whole with attributes etc.

        :type target_ds: xarray.Dataset
        :param target_ds: ds to populate (perhaps data at new processing level)

        :type source_ds: xarray.Dataset
        :param source_ds: ds to take data from (perhaps data at previous processing level)
        """

        # Find variable names common to target_ds and source_ds, excluding specified exclude variables
        common_variable_names = list(set(target_ds.variables).intersection(source_ds.variables))

        if exclude is not None:
            common_variable_names = [name for name in common_variable_names if name not in exclude]

        # Remove any common variables that have different dimensions in target_ds and source_ds
        common_variable_names = [name for name in common_variable_names if target_ds[name].dims == source_ds[name].dims]

        # Propagate data
        for common_variable_name in common_variable_names:
            target_ds[common_variable_name].values = source_ds[common_variable_name].values

    # todo - add method to propagate common unpopulated metadata


if __name__ == '__main__':
    pass
