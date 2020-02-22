"""
DatasetUtil class
"""

from xarray import Variable, DataArray
import numpy as np


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class DatasetUtil:
    """
    Class to provide utilities for generating standard xarray DataArrays
    """

    @staticmethod
    def create_default_vector(len, dtype, dim_name=None, fill_value=None):
        """
        Return default empty 1d DataArray

        :type len: int
        :param len: array length

        :type dtype: type
        :param dtype: numpy data type

        :type dim_name: str
        :param dim_name: (optional) dimension name

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return:
            default_vector *xarray.DataArray*

            Default empty vector
        """

        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)

        empty_array = np.full(len, fill_value, dtype)

        if dim_name is not None:
            default_array = DataArray(empty_array, dims=dim_name)
        else:
            default_array = DataArray(empty_array, dims=['y'])

        return default_array

    @staticmethod
    def create_default_array(width, height, dtype, dim_names=None, fill_value=None):
        """
        Return default empty 2d DataArray

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type dtype: type
        :param dtype: numpy data type

        :type dim_names: list
        :param dim_names: (optional) dimension name

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return:
            default_array *xarray.DataArray*

            Default empty array
        """

        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)

        empty_array = np.full([height, width], fill_value, dtype)

        if dim_names is not None:
            default_array = DataArray(empty_array, dims=dim_names)
        else:
            default_array = DataArray(empty_array, dims=['y', 'x'])

        return default_array

    @staticmethod
    def create_default_array3d(length, width, height, dtype, dim_names=None, fill_value=None):
        """
        Return default empty 3d DataArray

        :type length: int
        :param length: array length

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type dtype: type
        :param dtype: numpy data type

        :type dim_names: list
        :param dim_names: (optional) dimension name

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return:
            default_array *xarray.DataArray*

            Default empty 3D array
        """

        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)

        empty_array = np.full([height, width, length], fill_value, dtype)

        if dim_names is not None:
            default_array = DataArray(empty_array, dims=dim_names)
        else:
            default_array = DataArray(empty_array, dims=['z', 'y', 'x'])

        return default_array

    @staticmethod
    def create_vector_variable(height, dtype, standard_name=None, long_name=None, dim_name=None, fill_value=None):
        """
        Return default empty 1d xarray Variable

        :type height: int
        :param height: array length

        :type dtype: type
        :param dtype: numpy data type
        
        :type standard_name: str
        :param standard_name: (optional) variable standard name attribute
        
        :type long_name: str
        :param long_name: (optional) variable long name attribute

        :type dim_name: str
        :param dim_name: (optional) dimension name

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return:
            default_vector_variable *xarray.Variable*

            Default empty vector variable
        """
        
        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)
        
        default_vector = DatasetUtil.create_default_vector(height, dtype, fill_value=fill_value)

        if dim_name is None:
            variable = Variable(["y"], default_vector)
        else:
            variable = Variable(dim_name, default_vector)

        variable.attrs["_FillValue"] = fill_value

        if standard_name is not None:
            variable.attrs["standard_name"] = standard_name

        if long_name is not None:
            variable.attrs["long_name"] = long_name

        return variable

    @staticmethod
    def create_array_variable(width, height, dtype, standard_name=None, long_name=None, dim_names=None,
                              fill_value=None):
        """
        Return default empty 2d xarray Variable

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type dtype: type
        :param dtype: numpy data type

        :type standard_name: str
        :param standard_name: (optional) variable standard name attribute

        :type long_name: str
        :param long_name: (optional) variable long name attribute

        :type dim_names: list
        :param dim_names: (optional) dimension names

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return:
            default_array_variable *xarray.Variable*

            Default empty array variable
        """
        
        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)

        default_array = DatasetUtil.create_default_array(width, height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["y", "x"], default_array)
        else:
            variable = Variable(dim_names, default_array)

        variable.attrs["_FillValue"] = fill_value

        if standard_name is not None:
            variable.attrs["standard_name"] = standard_name

        if long_name is not None:
            variable.attrs["long_name"] = long_name

        return variable

    @staticmethod
    def create_array3d_variable(length, width, height, dtype, standard_name=None, long_name=None, dim_names=None,
                                fill_value=None):
        """
        Return default empty 3d xarray Variable

        :type length: int
        :param length: array length

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type dtype: type
        :param dtype: numpy data type

        :type standard_name: str
        :param standard_name: (optional) variable standard name attribute

        :type long_name: str
        :param long_name: (optional) variable long name attribute

        :type dim_names: list
        :param dim_names: (optional) dimension names

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return:
            default_array_variable *xarray.Variable*

            Default empty array variable
        """
        
        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)
        
        default_array = DatasetUtil.create_default_array3d(length, width, height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["z", "y", "x"], default_array)
        else:
            variable = Variable(dim_names, default_array)

        variable.attrs["_FillValue"] = fill_value

        if standard_name is not None:
            variable.attrs["standard_name"] = standard_name

        if long_name is not None:
            variable.attrs["long_name"] = long_name

        return variable

    @staticmethod
    def add_encoding(variable, dtype, scale_factor=1.0, offset=0.0, fill_value=None, chunksizes=None):
        """
        Add encoding to xarray Variable to apply when writing netCDF files

        :type variable: xarray.Variable
        :param variable: data variable

        :type dtype: type
        :param dtype: numpy data type

        :type scale_factor: float
        :param scale_factor: variable scale factor

        :type offset: float
        :param offset: variable offset value

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :type chunksizes: float
        :param chunksizes: (optional) chucksizes
        """

        encoding_dict = {'dtype': dtype, 'scale_factor': scale_factor, 'add_offset': offset}

        if chunksizes is not None:
            encoding_dict.update({'chunksizes': chunksizes})

        if fill_value is not None:
            encoding_dict.update({'_FillValue': fill_value})

        variable.encoding = encoding_dict

    @staticmethod
    def add_units(variable, units):
        """
        Add units attributes to xarray Variable

        :type variable: xarray.Variable
        :param variable: data variable

        :type units: str
        :param units: variable units
        """

        variable.attrs["units"] = units

    @staticmethod
    def get_default_fill_value(dtype):
        """
        Returns default fill_value for given data type

        :type dtype: type
        :param dtype: numpy dtype

        :return:
            fill_value

            CF-conforming fill value
        """

        if dtype == np.int8:
            return np.int8(-127)
        if dtype == np.uint8:
            return np.uint8(-1)
        elif dtype == np.int16:
            return np.int16(-32767)
        elif dtype == np.uint16:
            return np.uint16(-1)
        elif dtype == np.int32:
            return np.int32(-2147483647)
        elif dtype == np.uint32:
            return np.uint32(-1)
        elif dtype == np.int64:
            return np.int64(-9223372036854775806)
        elif dtype == np.float32:
            return np.float32(9.96921E36)
        elif dtype == np.float64:
            return np.float64(9.969209968386869E36)


if __name__ == "__main__":
    pass
