"""
Tests for HypernetsWriter class
"""

import unittest
from unittest.mock import patch, MagicMock
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.test.test_functions import setup_test_context
from hypernets_processor.version import __version__
from xarray import Dataset
import numpy as np
import os
import string
import random
import shutil


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
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        context = setup_test_context(
            raw_data_directory=os.path.join(tmpdir, "data"),
            archive_directory=os.path.join(tmpdir, "out"),
            metadata_db_url="sqlite:///" + tmpdir + "/metadata.db",
            anomoly_db_url="sqlite:///" + tmpdir + "/anomoly.db",
            archive_db_url="sqlite:///" + tmpdir + "/archive.db",
            create_directories=True,
            create_dbs=True
        )

        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter(context=context)

        hw.write(ds)
        mock_write.assert_called_once_with(
            ds,
            os.path.join(tmpdir, "out", "site", "2021", "4", "3", "test.nc"),
            compression_level=None
        )

        shutil.rmtree(tmpdir)

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

    def test_write_no_context_nofmt_netcdf(self):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        self.assertRaises(ValueError, hw.write, ds)

    def test_write_no_context_nodirectory_netcdf(self):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        self.assertRaises(ValueError, hw.write, ds, fmt="netCDF4")

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

    def test_fill_ds(self):
        ds = Dataset()
        ds["array_variable1"] = DatasetUtil.create_variable([7, 8], np.float32)
        ds["array_variable2"] = DatasetUtil.create_variable([7, 8], np.float32)

        ds["array_variable1"][2, 3] = np.nan
        ds["array_variable2"][2, 3] = np.nan

        HypernetsWriter.fill_ds(ds)

        self.assertTrue(np.all(ds["array_variable1"] == 9.96921E36))
        self.assertTrue(np.all(ds["array_variable2"] == 9.96921E36))


if __name__ == '__main__':
    unittest.main()
