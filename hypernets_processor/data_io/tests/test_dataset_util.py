"""
Tests for DatasetUtil class
"""

import unittest
import numpy as np
from xarray import DataArray, Variable
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestDatasetUtil(unittest.TestCase):
    def test_create_default_vector_int(self):

        default_array = DatasetUtil.create_default_vector(5, np.int8)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2])

    def test_create_default_vector_int_dims(self):

        default_array = DatasetUtil.create_default_vector(5, np.int8, dim_name="dim1")

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2])
        self.assertEqual(("dim1",), default_array.dims)

    def test_create_default_vector_int_fill_value(self):

        default_array = DatasetUtil.create_default_vector(5, np.int8, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(1, default_array[2])

    def test_create_default_array_int(self):

        default_array = DatasetUtil.create_default_array(7, 8, np.int8)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((8, 7), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2, 4])

    def test_create_default_array_int_dims(self):

        default_array = DatasetUtil.create_default_array(7, 8, np.int8, dim_names=["dim1", "dim2"])

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((8, 7), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2, 4])
        self.assertEqual(("dim1", "dim2"), default_array.dims)

    def test_create_default_array_int_fill_value(self):

        default_array = DatasetUtil.create_default_array(7, 8, np.int8, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((8, 7), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(1, default_array[2, 4])

    def test_create_default_array3d_int(self):

        default_array = DatasetUtil.create_default_array3d(7, 8, 3, np.int8)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((3, 8, 7), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2, 4, 3])

    def test_create_default_array3d_int_dims(self):
        
        default_array = DatasetUtil.create_default_array3d(7, 8, 3, np.int8, dim_names=["dim1", "dim2", "dim3"])

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((3, 8, 7), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2, 4, 3])
        self.assertEqual(("dim1", "dim2", "dim3"), default_array.dims)

    def test_create_default_array3d_int_fill_value(self):

        default_array = DatasetUtil.create_default_array3d(7, 8, 3, np.int8, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((3, 8, 7), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(1, default_array[2, 4, 3])

    def test_create_vector_variable_int(self):
        vector_variable = DatasetUtil.create_vector_variable(5, np.int8)

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])

    def test_create_vector_variable_int_dims(self):
        vector_variable = DatasetUtil.create_vector_variable(5, np.int8, dim_name="dim1")

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])
        self.assertEqual(("dim1",), vector_variable.dims)

    def test_create_vector_variable_int_fill_value(self):
        vector_variable = DatasetUtil.create_vector_variable(5, np.int8, fill_value=1)

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(1, vector_variable[2])

    def test_create_vector_variable_int_names(self):
        vector_variable = DatasetUtil.create_vector_variable(5, np.int8, standard_name="std", long_name="long")

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])
        self.assertEqual("std", vector_variable.attrs["standard_name"])
        self.assertEqual("long", vector_variable.attrs["long_name"])

    def test_create_array_variable_int(self):
        array_variable = DatasetUtil.create_array_variable(7, 8, np.int8)

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((8, 7), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(-127, array_variable[2, 4])

    def test_create_array_variable_int_dims(self):
        array_variable = DatasetUtil.create_array_variable(7, 8, np.int8, dim_names=["dim1", "dim2"])

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((8, 7), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(-127, array_variable[2, 4])
        self.assertEqual(("dim1", "dim2"), array_variable.dims)

    def test_create_array_variable_int_fill_value(self):
        array_variable = DatasetUtil.create_array_variable(7, 8, np.int8, fill_value=1)

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((8, 7), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(1, array_variable[2, 4])

    def test_create_array_variable_int_names(self):
        array_variable = DatasetUtil.create_array_variable(7, 8, np.int8, standard_name="std", long_name="long")

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((8, 7), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(-127, array_variable[2, 4])
        self.assertEqual("std", array_variable.attrs["standard_name"])
        self.assertEqual("long", array_variable.attrs["long_name"])

    def test_create_array3d_variable_int(self):
        array3d_variable = DatasetUtil.create_array3d_variable(7, 8, 3, np.int8)

        self.assertIsNotNone(array3d_variable)
        self.assertEqual(Variable, type(array3d_variable))
        self.assertEqual((3, 8, 7), array3d_variable.shape)
        self.assertEqual(np.int8, array3d_variable.dtype)
        self.assertEqual(-127, array3d_variable[2, 4, 3])

    def test_create_array3d_variable_int_dims(self):
        array3d_variable = DatasetUtil.create_array3d_variable(7, 8, 3, np.int8, dim_names=["dim1", "dim2", "dim3"])

        self.assertIsNotNone(array3d_variable)
        self.assertEqual(Variable, type(array3d_variable))
        self.assertEqual((3, 8, 7), array3d_variable.shape)
        self.assertEqual(np.int8, array3d_variable.dtype)
        self.assertEqual(-127, array3d_variable[2, 4, 3])
        self.assertEqual(("dim1", "dim2", "dim3"), array3d_variable.dims)

    def test_create_array3d_variable_int_fill_value(self):
        array3d_variable = DatasetUtil.create_array3d_variable(7, 8, 3, np.int8, fill_value=1)

        self.assertIsNotNone(array3d_variable)
        self.assertEqual(Variable, type(array3d_variable))
        self.assertEqual((3, 8, 7), array3d_variable.shape)
        self.assertEqual(np.int8, array3d_variable.dtype)
        self.assertEqual(1, array3d_variable[2, 4, 3])

    def test_create_array3d_variable_int_names(self):
        array3d_variable = DatasetUtil.create_array3d_variable(7, 8, 3, np.int8, standard_name="std", long_name="long")

        self.assertIsNotNone(array3d_variable)
        self.assertEqual(Variable, type(array3d_variable))
        self.assertEqual((3, 8, 7), array3d_variable.shape)
        self.assertEqual(np.int8, array3d_variable.dtype)
        self.assertEqual(-127, array3d_variable[2, 4, 3])
        self.assertEqual("std", array3d_variable.attrs["standard_name"])
        self.assertEqual("long", array3d_variable.attrs["long_name"])

    def test_add_encoding(self):
        vector_variable = DatasetUtil.create_vector_variable(5, np.int8)
        DatasetUtil.add_encoding(vector_variable, np.int32, scale_factor=10, offset=23, fill_value=11, chunksizes=12)

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])

        self.assertEqual(np.int32, vector_variable.encoding["dtype"])
        self.assertEqual(10, vector_variable.encoding["scale_factor"])
        self.assertEqual(23, vector_variable.encoding["add_offset"])
        self.assertEqual(11, vector_variable.encoding["_FillValue"])
        self.assertEqual(12, vector_variable.encoding["chunksizes"])

    def test_add_units(self):
        vector_variable = DatasetUtil.create_vector_variable(5, np.int8)
        DatasetUtil.add_units(vector_variable, "m")

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])

        self.assertEqual("m", vector_variable.attrs["units"])
        
    def test_get_default_fill_value(self):

        self.assertEqual(-127, DatasetUtil.get_default_fill_value(np.int8))
        self.assertEqual(-32767, DatasetUtil.get_default_fill_value(np.int16))
        self.assertEqual(np.uint16(-1), DatasetUtil.get_default_fill_value(np.uint16))
        self.assertEqual(-2147483647, DatasetUtil.get_default_fill_value(np.int32))
        self.assertEqual(-9223372036854775806, DatasetUtil.get_default_fill_value(np.int64))
        self.assertEqual(np.float32(9.96921E36), DatasetUtil.get_default_fill_value(np.float32))
        self.assertEqual(9.969209968386869E36, DatasetUtil.get_default_fill_value(np.float64))


if __name__ == '__main__':
    unittest.main()
