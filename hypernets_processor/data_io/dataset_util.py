"""
DatasetUtil class
"""

from hypernets_processor.version import __version__
import string
from xarray import Variable, DataArray, Dataset
import numpy as np


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

DEFAULT_DIM_NAMES = list(string.ascii_lowercase[-3:]) + list(string.ascii_lowercase[:-3])
DEFAULT_DIM_NAMES.reverse()


class DatasetUtil:
    """
    Class to provide utilities for generating standard xarray DataArrays and Variables
    """

    @staticmethod
    def create_default_array(dim_sizes, dtype, dim_names=None, fill_value=None):
        """
        Return default empty xarray DataArray

        :type dim_sizes: list
        :param dim_sizes: dimension sizes as ints, i.e. [dim1_size, dim2_size, dim3_size] (e.g. [2,3,5])

        :type dtype: type
        :param dtype: numpy data type

        :type dim_names: list
        :param dim_names: (optional) dimension names as strings, i.e. ["dim1_name", "dim2_name", "dim3_size"]

        :type fill_value: int/float
        :param fill_value: (optional) fill value (if None CF compliant value used)

        :return: Default empty array
        :rtype: xarray.DataArray
        """

        if fill_value is None:
            fill_value = DatasetUtil.get_default_fill_value(dtype)

        empty_array = np.full(dim_sizes, fill_value, dtype)

        if dim_names is not None:
            default_array = DataArray(empty_array, dims=dim_names)
        elif (dim_names is None) and (dim_sizes == []):
            default_array = DataArray(empty_array)
        else:
            default_array = DataArray(empty_array, dims=DEFAULT_DIM_NAMES[-len(dim_sizes):])

        return default_array

    @staticmethod
    def create_variable(dim_sizes, dtype, dim_names=None, attributes=None, fill_value=None):
        """
        Return default empty xarray Variable

        :type dim_sizes: list
        :param dim_sizes: dimension sizes as ints, i.e. [dim1_size, dim2_size, dim3_size] (e.g. [2,3,5])

        :type dtype: type
        :param dtype: numpy data type

        :type dim_names: list
        :param dim_names: (optional) dimension names as strings, i.e. ["dim1_name", "dim2_name", "dim3_size"]

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type fill_value: int/float
        :param fill_value: (optional) fill value for data array (if None CF compliant _FillValue used)

        :return: Default empty variable
        :rtype: xarray.Variable
        """

        # Get CF Compliant fill value for data type
        _FillValue = DatasetUtil.get_default_fill_value(dtype)

        if fill_value is None:
            fill_value = _FillValue

        default_array = DatasetUtil.create_default_array(dim_sizes, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(DEFAULT_DIM_NAMES[-len(dim_sizes):], default_array)
        else:
            variable = Variable(dim_names, default_array)

        variable.attrs["_FillValue"] = _FillValue

        if attributes is not None:
            variable.attrs = {**variable.attrs, **attributes}

        return variable

    @staticmethod
    def create_flags_variable(dim_sizes, meanings, dim_names=None, attributes=None):
        """
        Return default empty 1d xarray flag Variable

        :type dim_sizes: list
        :param dim_sizes: dimension sizes as ints, i.e. [dim1_size, dim2_size, dim3_size] (e.g. [2,3,5])

        :type attributes: dict
        :param attributes: (optional) dictionary of variable attributes, e.g. standard_name

        :type dim_names: list
        :param dim_names: (optional) dimension names as strings, i.e. ["dim1_name", "dim2_name", "dim3_size"]

        :return: Default empty flag vector variable
        :rtype: xarray.Variable
        """

        n_masks = len(meanings)

        data_type = DatasetUtil.return_flags_dtype(n_masks)

        variable = DatasetUtil.create_variable(dim_sizes, data_type, dim_names=dim_names,
                                               attributes=attributes, fill_value=0)

        # add flag attributes
        variable.attrs["flag_meanings"] = str(meanings)[1:-1].replace("'","").replace(",","")
        variable.attrs["flag_masks"] = str([2**i for i in range(0, n_masks)])[1:-1]

        # todo - make sure flags can't have units

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
            return np.int8
        elif n_masks <= 16:
            return np.int16
        elif n_masks <= 32:
            return np.int32
        else:
            return np.int64

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

        # todo - make sure flags can't have encoding added

        encoding_dict = {'dtype': dtype, 'scale_factor': scale_factor, 'add_offset': offset}

        if chunksizes is not None:
            encoding_dict.update({'chunksizes': chunksizes})

        if fill_value is not None:
            encoding_dict.update({'_FillValue': fill_value})
        else:
            encoding_dict.update({'_FillValue': DatasetUtil.get_default_fill_value(dtype)})

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
            return np.int8(-128)
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

    @staticmethod
    def _get_flag_encoding(da):
        """
        Returns flag encoding for flag type data array
        :type da: xarray.DataArray
        :param da: data array
        :return: flag meanings
        :rtype: list
        :return: flag masks
        :rtype: list
        """

        try:
            flag_meanings = da.attrs["flag_meanings"].split()
            flag_masks = [int(fm) for fm in da.attrs["flag_masks"].split(",")]
        except KeyError:
            raise KeyError(da.name + " not a flag variable")

        return flag_meanings, flag_masks

    @staticmethod
    def unpack_flags(da):
        """
        Breaks down flag data array into dataset of boolean masks for each flag
        :type da: xarray.DataArray
        :param da: dataset
        :return: flag masks
        :rtype: xarray.Dataset
        """

        flag_meanings, flag_masks = DatasetUtil._get_flag_encoding(da)

        ds = Dataset()
        for flag_meaning, flag_mask in zip(flag_meanings, flag_masks):
            ds[flag_meaning] = DatasetUtil.create_variable(list(da.shape), bool, dim_names=list(da.dims))
            ds[flag_meaning] = (da & flag_mask).astype(bool)

        return ds

    @staticmethod
    def get_flags_mask_or(da, flags=None):
        """
        Returns boolean mask for set of flags, defined as logical or of flags

        :type da: xarray.DataArray
        :param da: dataset

        :type flags: list
        :param flags: list of flags (if unset all data flags selected)

        :return: flag masks
        :rtype: numpy.ndarray
        """

        flags_ds = DatasetUtil.unpack_flags(da)

        flags = flags if flags is not None else flags_ds.variables
        mask_flags = [flags_ds[flag].values for flag in flags]

        return np.logical_or.reduce(mask_flags)

    @staticmethod
    def get_flags_mask_and(da, flags=None):
        """
        Returns boolean mask for set of flags, defined as logical and of flags

        :type da: xarray.DataArray
        :param da: dataset

        :type flags: list
        :param flags: list of flags (if unset all data flags selected)

        :return: flag masks
        :rtype: numpy.ndarray
        """

        flags_ds = DatasetUtil.unpack_flags(da)

        flags = flags if flags is not None else flags_ds.variables
        mask_flags = [flags_ds[flag].values for flag in flags]

        return np.logical_and.reduce(mask_flags)

    @staticmethod
    def set_flag(da, flag_name, error_if_set=False):
        """
        Sets named flag for elements in data array
        :type da: xarray.DataArray
        :param da: dataset
        :type flag_name: str
        :param flag_name: name of flag to set
        :type error_if_set: bool
        :param error_if_set: raises error if chosen flag is already set for any element
        """

        set_flags = DatasetUtil.unpack_flags(da)[flag_name]

        if np.any(set_flags == True) and error_if_set:
            raise ValueError("Flag " + flag_name + " already set for variable " + da.name)

        # Find flag mask
        flag_meanings, flag_masks = DatasetUtil._get_flag_encoding(da)
        flag_bit = flag_meanings.index(flag_name)
        flag_mask = flag_masks[flag_bit]

        da.values = da.values | flag_mask

        return da

    @staticmethod
    def unset_flag(da, flag_name, error_if_unset=False):
        """
        Unsets named flag for specified index of dataset variable
        :type da: xarray.DataArray
        :param da: data array
        :type flag_name: str
        :param flag_name: name of flag to unset
        :type error_if_unset: bool
        :param error_if_unset: raises error if chosen flag is already set at specified index
        """

        set_flags = DatasetUtil.unpack_flags(da)[flag_name]

        if np.any(set_flags == False) and error_if_unset:
            raise ValueError("Flag " + flag_name + " already set for variable " + da.name)

        # Find flag mask
        flag_meanings, flag_masks = DatasetUtil._get_flag_encoding(da)
        flag_bit = flag_meanings.index(flag_name)
        flag_mask = flag_masks[flag_bit]

        da.values = da.values & ~flag_mask

        return da

    @staticmethod
    def get_set_flags(da):
        """
        Return list of set flags for single element data array
        :type da: xarray.DataArray
        :param da: single element data array
        :return: set flags
        :rtype: list
        """

        if da.shape != ():
            raise ValueError("Must pass single element data array")

        flag_meanings, flag_masks = DatasetUtil._get_flag_encoding(da)

        set_flags = []
        for flag_meaning, flag_mask in zip(flag_meanings, flag_masks):
            if (da & flag_mask):
                set_flags.append(flag_meaning)

        return set_flags

    @staticmethod
    def check_flag_set(da, flag_name):
        """
        Returns if flag for single element data array
        :type da: xarray.DataArray
        :param da: single element data array
        :type flag_name: str
        :param flag_name: name of flag to set
        :return: set flags
        :rtype: list
        """

        if da.shape != ():
            raise ValueError("Must pass single element data array")

        set_flags = DatasetUtil.get_set_flags(da)

        if flag_name in set_flags:
            return True
        return False




if __name__ == "__main__":
    pass
