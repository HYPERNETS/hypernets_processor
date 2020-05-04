"""
DatasetUtil class
"""

from hypernets_processor.version import __version__
from xarray import Variable, DataArray
import numpy as np


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = __version__
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

        :return: Default empty vector
        :rtype: xarray.DataArray
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

        :return: Default empty array
        :rtype: xarray.DataArray
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

        :return: Default empty 3D array
        :rtype: xarray.DataArray
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
    def create_vector_variable(height, dtype, dim_name=None, fill_value=None, attributes=None):
        """
        Return default empty 1d xarray Variable

        :type height: int
        :param height: array length

        :type dtype: type
        :param dtype: numpy data type
        
        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_name: str
        :param dim_name: (optional) dimension name

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return: Default empty vector variable
        :rtype: xarray.Variable
        """
        
        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)
        
        default_vector = DatasetUtil.create_default_vector(height, dtype, fill_value=fill_value)

        if dim_name is None:
            variable = Variable(["y"], default_vector)
        else:
            variable = Variable(dim_name, default_vector)

        variable.attrs["_FillValue"] = fill_value

        if attributes is not None:
            variable.attrs = {**variable.attrs, **attributes}

        return variable

    @staticmethod
    def create_array_variable(width, height, dtype, dim_names=None, fill_value=None, attributes=None):
        """
        Return default empty 2d xarray Variable

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type dtype: type
        :param dtype: numpy data type

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_names: list
        :param dim_names: (optional) dimension names

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return: Default empty array variable
        :rtype: xarray.Variable
        """
        
        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)

        default_array = DatasetUtil.create_default_array(width, height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["y", "x"], default_array)
        else:
            variable = Variable(dim_names, default_array)

        variable.attrs["_FillValue"] = fill_value

        if attributes is not None:
            variable.attrs = {**variable.attrs, **attributes}

        return variable

    @staticmethod
    def create_array3d_variable(length, width, height, dtype, dim_names=None, fill_value=None, attributes=None):
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

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_names: list
        :param dim_names: (optional) dimension names

        :type fill_value: int/float
        :param fill_value: (optional) fill value

        :return: Default empty 3D array variable
        :rtype: xarray.Variable
        """
        
        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)
        
        default_array = DatasetUtil.create_default_array3d(length, width, height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["z", "y", "x"], default_array)
        else:
            variable = Variable(dim_names, default_array)

        variable.attrs["_FillValue"] = fill_value

        if attributes is not None:
            variable.attrs = {**variable.attrs, **attributes}

        return variable

    @staticmethod
    def create_flags_vector_variable(height, meanings, dim_name=None, attributes=None):
        """
        Return default empty 1d xarray flag Variable

        :type height: int
        :param height: array length

        :type meanings: list
        :param meanings: flag meanings

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_name: str
        :param dim_name: (optional) dimension name

        :return: Default empty flag vector variable
        :rtype: xarray.Variable
        """

        n_masks = len(meanings)

        data_type = DatasetUtil.return_flags_dtype(n_masks)

        variable = DatasetUtil.create_vector_variable(height, data_type, dim_name=dim_name, fill_value=0,
                                                      attributes=attributes)

        # add flag attributes
        variable.attrs["flag_meanings"] = str(meanings)[1:-1].replace("'","").replace(",","")
        variable.attrs["flag_masks"] = str([2**i for i in range(0, n_masks)])[1:-1]

        return variable

    @staticmethod
    def create_flags_array_variable(width, height, meanings, dim_names=None, attributes=None):
        """
        Return default empty 2d xarray flag Variable

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type meanings: list
        :param meanings: flag meanings

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_names: list
        :param dim_names: (optional) dimension name

        :return: Default empty flag vector variable
        :rtype: xarray.Variable
        """

        n_masks = len(meanings)

        data_type = DatasetUtil.return_flags_dtype(n_masks)

        variable = DatasetUtil.create_array_variable(width, height, data_type, dim_names=dim_names, fill_value=0,
                                                     attributes=attributes)

        # add flag attributes
        variable.attrs["flag_meanings"] = str(meanings)[1:-1].replace("'", "").replace(",", "")
        variable.attrs["flag_masks"] = str([2 ** i for i in range(0, n_masks)])[1:-1]

        return variable

    @staticmethod
    def create_flags_array3d_variable(length, width, height, meanings, dim_names=None, attributes=None):
        """
        Return default empty 3d xarray flag Variable

        :type length: int
        :param length: array length

        :type width: int
        :param width: array width

        :type height: int
        :param height: array height

        :type meanings: list
        :param meanings: flag meanings

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_names: list
        :param dim_names: (optional) dimension name

        :return: Default empty flag vector variable
        :rtype: xarray.Variable
        """

        n_masks = len(meanings)

        data_type = DatasetUtil.return_flags_dtype(n_masks)

        variable = DatasetUtil.create_array3d_variable(length, width, height, data_type, dim_names=dim_names,
                                                       fill_value=0, attributes=attributes)

        # add flag attributes
        variable.attrs["flag_meanings"] = str(meanings)[1:-1].replace("'", "").replace(",", "")
        variable.attrs["flag_masks"] = str([2 ** i for i in range(0, n_masks)])[1:-1]

        return variable

    @staticmethod
    def return_flags_dtype(n_masks):
        """
        Return required flags array data type

        :type n_masks: int
        :param n_masks: number of masks required in flag array

        :return: data type
        :rtype: dtype
        """

        if n_masks <= 8:
            return np.uint8
        elif n_masks <= 16:
            return np.uint16
        elif n_masks <= 32:
            return np.uint32
        else:
            return np.uint64

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
    def get_default_fill_value(dtype):
        """
        Returns default fill_value for given data type

        :type dtype: type
        :param dtype: numpy dtype

        :return: CF-conforming fill value
        :rtype: fill_value
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
