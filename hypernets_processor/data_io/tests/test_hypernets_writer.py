"""
Tests for HypernetsWriter class
"""

import unittest
from unittest.mock import patch, MagicMock
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.test.test_functions import setup_test_context
from hypernets_processor.version import __version__
from xarray import Dataset


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

# todo - write test for csv writer
# todo - write test for end to end writer use


class TestHypernetsWriter(unittest.TestCase):

    @patch('hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter._write_netcdf')
    def test_write_netcdf(self, mock_write):
        context = setup_test_context()

        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter(context=context)

        hw.write(ds, fmt="netcdf")
        mock_write.assert_called_once_with(ds, "out/site/2021/4/3/test.nc", compression_level=None)

    @patch('hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter._write_netcdf')
    def test_write_no_context_netcdf(self, mock_write):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        hw.write(ds, directory="test", fmt="netcdf")
        mock_write.assert_called_once_with(ds, "test/test.nc", compression_level=None)

    @patch('hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter._write_csv')
    def test_write_no_context_csv(self, mock_write):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        hw.write(ds, directory="test", fmt="csv")
        mock_write.assert_called_once_with(ds, "test/test.csv")

    def test_write_no_context_no_directory_netcdf(self):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        self.assertRaises(ValueError, hw.write, ds)

    def test_write_no_context_badfmt(self):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        self.assertRaises(NameError, hw.write, ds, directory="asdfasdf", fmt="dsfdfg")

    def test__write_netcdf(self):

        ds = MagicMock()
        path = "test.nc"

        HypernetsWriter._write_netcdf(ds, path)

        ds.to_netcdf.assert_called_once_with(path, encoding={}, engine='netcdf4', format='netCDF4')


if __name__ == '__main__':
    unittest.main()
