"""
Tests for DatasetUtil class
"""

import unittest
import numpy as np
from xarray import DataArray, Variable, Dataset
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
    def test_create_default_array_1D_int(self):

        default_array = DatasetUtil.create_default_array([5], np.int8)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2])

    def test_create_default_array_1D_int_dims(self):

        default_array = DatasetUtil.create_default_array([5], np.int8, dim_names=["dim1"])

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2])
        self.assertEqual(("dim1",), default_array.dims)

    def test_create_default_array_1D_int_fill_value(self):

        default_array = DatasetUtil.create_default_array([5], np.int8, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(1, default_array[2])

    def test_create_default_array_3D_int(self):
        default_array = DatasetUtil.create_default_array([7, 8, 3], np.int8)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((7, 8, 3), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2, 4, 2])

    def test_create_default_array_3D_int_dims(self):
        default_array = DatasetUtil.create_default_array([7, 8, 3], np.int8, dim_names=["dim1", "dim2", "dim3"])

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((7, 8, 3), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(-127, default_array[2, 4, 2])
        self.assertEqual(("dim1", "dim2", "dim3",), default_array.dims)

    def test_create_default_array_3D_int_fill_value(self):
        default_array = DatasetUtil.create_default_array([7, 8, 3], np.int8, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((7, 8, 3), default_array.shape)
        self.assertEqual(np.int8, default_array.dtype)
        self.assertEqual(1, default_array[2, 4, 2])

    def test_create_variable_1D_int(self):
        vector_variable = DatasetUtil.create_variable([5], np.int8)

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])

    def test_create_variable_1D_int_dims(self):
        vector_variable = DatasetUtil.create_variable([5], np.int8, dim_names=["dim1"])

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])
        self.assertEqual(("dim1",), vector_variable.dims)

    def test_create_variable_1D_int_fill_value(self):
        vector_variable = DatasetUtil.create_variable([5], np.int8, fill_value=1)

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(1, vector_variable[2])

    def test_create_variable_1D_int_attributes(self):
        vector_variable = DatasetUtil.create_variable([5], np.int8, attributes={"standard_name": "std"})

        self.assertIsNotNone(vector_variable)
        self.assertEqual(Variable, type(vector_variable))
        self.assertEqual((5,), vector_variable.shape)
        self.assertEqual(np.int8, vector_variable.dtype)
        self.assertEqual(-127, vector_variable[2])
        self.assertEqual("std", vector_variable.attrs["standard_name"])

    def test_create_variable_3D_int(self):
        array_variable = DatasetUtil.create_variable([7, 8, 3], np.int8)

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((7, 8, 3), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(-127, array_variable[2, 4, 2])

    def test_create_variable_3D_int_dims(self):
        array_variable = DatasetUtil.create_variable([7, 8, 3], np.int8, dim_names=["dim1", "dim2", "dim3"])

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((7, 8, 3), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(-127, array_variable[2, 4, 2])
        self.assertEqual(("dim1", "dim2", "dim3",), array_variable.dims)

    def test_create_variable_3D_int_fill_value(self):
        array_variable = DatasetUtil.create_variable([7, 8, 3], np.int8, fill_value=1)

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((7, 8, 3), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(1, array_variable[2, 4, 2])

    def test_create_variable_3D_int_attributes(self):
        array_variable = DatasetUtil.create_variable([7, 8, 3], np.int8, attributes={"standard_name": "std"})

        self.assertIsNotNone(array_variable)
        self.assertEqual(Variable, type(array_variable))
        self.assertEqual((7, 8, 3), array_variable.shape)
        self.assertEqual(np.int8, array_variable.dtype)
        self.assertEqual(-127, array_variable[2, 4, 2])
        self.assertEqual("std", array_variable.attrs["standard_name"])

    def test_create_flags_variable_1D(self):

        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        meanings_txt = "flag1 flag2 flag3 flag4 flag5 flag6 flag7 flag8"
        masks = "1, 2, 4, 8, 16, 32, 64, 128"
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                         attributes={"standard_name": "std"})

        self.assertIsNotNone(flags_vector_variable)
        self.assertEqual(Variable, type(flags_vector_variable))
        self.assertEqual((5,), flags_vector_variable.shape)
        self.assertEqual(np.uint8, flags_vector_variable.dtype)
        self.assertEqual(flags_vector_variable.attrs['flag_masks'], masks)
        self.assertEqual(flags_vector_variable.attrs['flag_meanings'], meanings_txt)
        self.assertEqual(0, flags_vector_variable[2])
        self.assertEqual("std", flags_vector_variable.attrs["standard_name"])
        self.assertEqual(("dim1",), flags_vector_variable.dims)

    def test_create_flags_variable_3D(self):

        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        meanings_txt = "flag1 flag2 flag3 flag4 flag5 flag6 flag7 flag8"
        masks = "1, 2, 4, 8, 16, 32, 64, 128"
        flags_array_variable = DatasetUtil.create_flags_variable([7, 8, 3], meanings,
                                                                 dim_names=["dim1", "dim2", "dim3"],
                                                                 attributes={"standard_name": "std"})

        self.assertIsNotNone(flags_array_variable)
        self.assertEqual(Variable, type(flags_array_variable))
        self.assertEqual((7, 8, 3), flags_array_variable.shape)
        self.assertEqual(np.uint8, flags_array_variable.dtype)
        self.assertEqual(flags_array_variable.attrs['flag_masks'], masks)
        self.assertEqual(flags_array_variable.attrs['flag_meanings'], meanings_txt)
        self.assertEqual(0, flags_array_variable[2, 4, 2])
        self.assertEqual("std", flags_array_variable.attrs["standard_name"])
        self.assertEqual(("dim1", "dim2", "dim3"), flags_array_variable.dims)

    def test_return_flags_dtype_5(self):
        data_type = DatasetUtil.return_flags_dtype(5)
        self.assertEqual(data_type, np.uint8)

    def test_return_flags_dtype_8(self):
        data_type = DatasetUtil.return_flags_dtype(8)
        self.assertEqual(data_type, np.uint8)

    def test_return_flags_dtype_15(self):
        data_type = DatasetUtil.return_flags_dtype(15)
        self.assertEqual(data_type, np.uint16)

    def test_return_flags_dtype_16(self):
        data_type = DatasetUtil.return_flags_dtype(16)
        self.assertEqual(data_type, np.uint16)

    def test_return_flags_dtype_17(self):
        data_type = DatasetUtil.return_flags_dtype(17)
        self.assertEqual(data_type, np.uint32)

    def test_return_flags_dtype_32(self):
        data_type = DatasetUtil.return_flags_dtype(32)
        self.assertEqual(data_type, np.uint32)

    def test_add_encoding(self):
        vector_variable = DatasetUtil.create_variable([5], np.int8)
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
        
    def test_get_default_fill_value(self):

        self.assertEqual(-127, DatasetUtil.get_default_fill_value(np.int8))
        self.assertEqual(-32767, DatasetUtil.get_default_fill_value(np.int16))
        self.assertEqual(np.uint16(-1), DatasetUtil.get_default_fill_value(np.uint16))
        self.assertEqual(-2147483647, DatasetUtil.get_default_fill_value(np.int32))
        self.assertEqual(-9223372036854775806, DatasetUtil.get_default_fill_value(np.int64))
        self.assertEqual(np.float32(9.96921E36), DatasetUtil.get_default_fill_value(np.float32))
        self.assertEqual(9.969209968386869E36, DatasetUtil.get_default_fill_value(np.float64))

    def test__get_flag_encoding(self):

        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        masks = [1, 2, 4, 8, 16, 32, 64, 128]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})

        ds["flags"] = flags_vector_variable

        meanings_out, masks_out = DatasetUtil._get_flag_encoding(ds["flags"])

        self.assertCountEqual(meanings, meanings_out)
        self.assertCountEqual(masks, masks_out)

    def test__get_flag_encoding_not_flag_var(self):
        ds = Dataset()
        ds["array_variable"] = DatasetUtil.create_variable([7, 8, 3], np.int8, attributes={"standard_name": "std"})

        self.assertRaises(KeyError, DatasetUtil._get_flag_encoding, ds["array_variable"])

    def test_unpack_flags(self):

        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        masks = [1, 2, 4, 8, 16, 32, 64, 128]
        flags_vector_variable = DatasetUtil.create_flags_variable([2,3], meanings, dim_names=["dim1", "dim2"],
                                                                  attributes={"standard_name": "std"})

        ds["flags"] = flags_vector_variable
        ds["flags"][0, 0] = ds["flags"][0, 0] | 8

        empty = np.zeros((2, 3), bool)
        flag4 = np.zeros((2, 3), bool)
        flag4[0,0] = True

        flags = DatasetUtil.unpack_flags(ds["flags"])

        self.assertTrue((flags["flag1"].data == empty).all())
        self.assertTrue((flags["flag2"].data == empty).all())
        self.assertTrue((flags["flag3"].data == empty).all())
        self.assertTrue((flags["flag4"].data == flag4).all())
        self.assertTrue((flags["flag5"].data == empty).all())
        self.assertTrue((flags["flag6"].data == empty).all())
        self.assertTrue((flags["flag7"].data == empty).all())
        self.assertTrue((flags["flag8"].data == empty).all())

    def test_get_set_flags(self):

        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable
        ds["flags"][3] = ds["flags"][3] | 8
        ds["flags"][3] = ds["flags"][3] | 32

        set_flags = DatasetUtil.get_set_flags(ds["flags"][3])

        self.assertCountEqual(set_flags, ["flag4", "flag6"])

    def test_get_set_flags_2d(self):

        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable

        self.assertRaises(ValueError, DatasetUtil.get_set_flags, ds["flags"])

    def test_check_flag_set_true(self):
        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable
        ds["flags"][3] = ds["flags"][3] | 8
        ds["flags"][3] = ds["flags"][3] | 32

        flag_set = DatasetUtil.check_flag_set(ds["flags"][3], "flag6")

        self.assertTrue(flag_set)

    def test_check_flag_set_false(self):
        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable
        ds["flags"][3] = ds["flags"][3] | 8

        flag_set = DatasetUtil.check_flag_set(ds["flags"][3], "flag6")

        self.assertFalse(flag_set)

    def test_check_flag_set_2d(self):
        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable

        self.assertRaises(ValueError, DatasetUtil.check_flag_set, ds["flags"], "flag6")

    def test_set_flag(self):

        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5, 4], meanings, dim_names=["dim1", "dim2"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable

        ds["flags"] = DatasetUtil.set_flag(ds["flags"], "flag4")

        flags = np.full(ds["flags"].shape, 0|8)

        self.assertTrue((ds["flags"].data == flags).all())

    def test_set_flag_error_if_set(self):
        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable
        ds["flags"][3] = ds["flags"][3] | 8

        self.assertRaises(ValueError, DatasetUtil.set_flag, ds["flags"], "flag4", error_if_set=True)

    def test_unset_flag(self):

        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable
        ds["flags"][:] = ds["flags"][:] | 8

        ds["flags"] = DatasetUtil.unset_flag(ds["flags"], "flag4")

        flags = np.zeros(ds["flags"].shape)

        self.assertTrue((ds["flags"].data == flags).all())

    def test_set_flag_error_if_unset(self):
        ds = Dataset()
        meanings = ["flag1", "flag2", "flag3", "flag4", "flag5", "flag6", "flag7", "flag8"]
        flags_vector_variable = DatasetUtil.create_flags_variable([5], meanings, dim_names=["dim1"],
                                                                  attributes={"standard_name": "std"})
        ds["flags"] = flags_vector_variable

        self.assertRaises(ValueError, DatasetUtil.unset_flag, ds["flags"], "flag4", error_if_unset=True)


if __name__ == '__main__':
    unittest.main()
