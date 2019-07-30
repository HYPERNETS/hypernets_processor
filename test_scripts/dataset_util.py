from xarray import Variable, DataArray
import numpy as np


class DatasetUtil:
    @staticmethod
    def create_default_vector(len, dtype, dims_names=None, fill_value=None):
        if fill_value is None:
            fill_value = -1

        empty_array = np.full(len, fill_value, dtype)

        if dims_names is not None:
            default_array = DataArray(empty_array, dims=dims_names)
        else:
            default_array = DataArray(empty_array, dims=['y'])

        return default_array

    @staticmethod
    def create_default_array(width, height, dtype, dims_names=None, fill_value=None):
        if fill_value is None:
            fill_value = -1

        empty_array = np.full([height, width], fill_value, dtype)

        if dims_names is not None:
            default_array = DataArray(empty_array, dims=dims_names)
        else:
            default_array = DataArray(empty_array, dims=['y', 'x'])

        return default_array

    @staticmethod
    def create_default_array3d(length, width, height, dtype, dims_names=None, fill_value=None):
        if fill_value is None:
            fill_value = -1

        empty_array = np.full([height, width, length], fill_value, dtype)

        if dims_names is not None:
            default_array = DataArray(empty_array, dims=dims_names)
        else:
            default_array = DataArray(empty_array, dims=['z', 'y', 'x'])

        return default_array

    def create_vector_variable(self, height, dtype, standard_name=None, long_name=None, dim_names=None, fill_value=None):
        if fill_value is None:
            default_vector = self.create_default_vector(height, dtype)
        else:
            default_vector = self.create_default_vector(height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["y"], default_vector)
        else:
            variable = Variable(dim_names, default_vector)

        if fill_value is None:
            variable.attrs["_FillValue"] = -1
        else:
            variable.attrs["_FillValue"] = fill_value

        if standard_name is not None:
            variable.attrs["standard_name"] = standard_name

        if long_name is not None:
            variable.attrs["long_name"] = long_name

        return variable

    def create_array_variable(self, width, height, dtype, standard_name=None, long_name=None, dim_names=None, fill_value=None):
        if fill_value is None:
            default_array = self.create_default_array(width, height, dtype)
        else:
            default_array = self.create_default_array(width, height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["y", "x"], default_array)
        else:
            variable = Variable(dim_names, default_array)

        if fill_value is None:
            variable.attrs["_FillValue"] = -1
        else:
            variable.attrs["_FillValue"] = fill_value

        if standard_name is not None:
            variable.attrs["standard_name"] = standard_name

        if long_name is not None:
            variable.attrs["long_name"] = long_name

        return variable

    def create_array3d_variable(self, length, width, height, dtype, standard_name=None, long_name=None, dim_names=None, fill_value=None):
        if fill_value is None:
            default_array = self.create_default_array3d(length, width, height, dtype)
        else:
            default_array = self.create_default_array3d(length, width, height, dtype, fill_value=fill_value)

        if dim_names is None:
            variable = Variable(["z", "y", "x"], default_array)
        else:
            variable = Variable(dim_names, default_array)

        if fill_value is None:
            variable.attrs["_FillValue"] = -1
        else:
            variable.attrs["_FillValue"] = fill_value

        if standard_name is not None:
            variable.attrs["standard_name"] = standard_name

        if long_name is not None:
            variable.attrs["long_name"] = long_name

        return variable

    @staticmethod
    def add_encoding(variable, data_type, scale_factor=1.0, offset=0.0, fill_value=None, chunksizes=None):
        encoding_dict ={'dtype': data_type, 'scale_factor': scale_factor, 'add_offset': offset}

        if chunksizes is not None:
            encoding_dict.update({'chunksizes': chunksizes})

        if fill_value is not None:
            encoding_dict.update({'_FillValue': fill_value})

        variable.encoding = encoding_dict

    @staticmethod
    def add_units(variable, units):
        variable.attrs["units"] = units


if __name__ == "__main__":
    pass
