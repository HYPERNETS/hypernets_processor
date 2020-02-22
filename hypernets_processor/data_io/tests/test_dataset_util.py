"""
Tests for DatasetUtil class
"""

import unittest
import numpy as np
from xarray import DataArray
from hypernets_processor.data_io.dataset_util import DatasetUtil


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestDatasetUtil(unittest.TestCase):
    def test_create_default_vector_int(self):
        du = DatasetUtil()

        default_array = du.create_default_vector(5, np.int32)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(-1, default_array[2])

    def test_create_default_vector_int_dims(self):
        du = DatasetUtil()

        default_array = du.create_default_vector(5, np.int32, dims_names="dim1")

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(-1, default_array[2])
        self.assertEqual(("dim1",), default_array.dims)

    def test_create_default_vector_int_fill_value(self):
        du = DatasetUtil()

        default_array = du.create_default_vector(5, np.int32, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((5,), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(1, default_array[2])

    def test_create_default_array(self):
        du = DatasetUtil()

        default_array = du.create_default_array(7, 8, np.int32)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((8, 7), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(-1, default_array[2, 4])

    def test_create_default_array_int_dims(self):
        du = DatasetUtil()

        default_array = du.create_default_array(7, 8, np.int32, dims_names=["dim1", "dim2"])

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((8, 7), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(-1, default_array[2, 4])
        self.assertEqual(("dim1", "dim2"), default_array.dims)

    def test_create_default_array_int_fill_value(self):
        du = DatasetUtil()

        default_array = du.create_default_array(7, 8, np.int32, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((8, 7), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(1, default_array[2, 4])

    def test_create_default_array3d_int(self):
        du = DatasetUtil()

        default_array = du.create_default_array3d(7, 8, 3, np.int32)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((3, 8, 7), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(-1, default_array[2, 4, 3])

    def test_create_default_array3d_int_dims(self):
        du = DatasetUtil()

        default_array = du.create_default_array3d(7, 8, 3, np.int32, dims_names=["dim1", "dim2", "dim3"])

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((3, 8, 7), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(-1, default_array[2, 4, 3])
        self.assertEqual(("dim1", "dim2", "dim3"), default_array.dims)

    def test_create_default_array3d_int_fill_value(self):
        du = DatasetUtil()

        default_array = du.create_default_array3d(7, 8, 3, np.int32, fill_value=1)

        self.assertIsNotNone(default_array)
        self.assertEqual(DataArray, type(default_array))
        self.assertEqual((3, 8, 7), default_array.shape)
        self.assertEqual(np.int32, default_array.dtype)
        self.assertEqual(1, default_array[2, 4, 3])


if __name__ == '__main__':
    unittest.main()
