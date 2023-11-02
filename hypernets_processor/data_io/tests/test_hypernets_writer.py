"""
Tests for HypernetsWriter class
"""

import unittest
from unittest.mock import patch, MagicMock
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.context import Context
from hypernets_processor.version import __version__

from xarray import Dataset
import numpy as np
import os
from datetime import datetime as dt
import obsarray

"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

# todo - write test for csv writer
# todo - write test for end to end writer use


class TestHypernetsWriter(unittest.TestCase):
    def test_return_fmt_netcdf(self):
        hw = HypernetsWriter()
        self.assertEqual("nc", hw.return_fmt(fmt="netcdf"))

    def test_return_fmt_netcdf4(self):
        hw = HypernetsWriter()
        self.assertEqual("nc", hw.return_fmt(fmt="netcdf4"))

    def test_return_fmt_csv(self):
        hw = HypernetsWriter()
        self.assertEqual("csv", hw.return_fmt(fmt="csv"))

    def test_return_fmt_invalid(self):
        hw = HypernetsWriter()
        self.assertRaises(NameError, hw.return_fmt, "invalid")

    def test_return_fmt_context(self):
        context = Context()
        context.set_config_value("product_format", "netcdf")
        hw = HypernetsWriter(context)
        self.assertEqual("nc", hw.return_fmt())

    def test_return_fmt_noinput(self):
        hw = HypernetsWriter()
        self.assertRaises(ValueError, hw.return_fmt)

    def test_return_directory(self):
        hw = HypernetsWriter()
        self.assertEqual("directory", hw.return_directory(directory="directory"))

    def test_return_directory_context_toarchive(self):
        context = Context()
        context.set_config_value("archive_directory", "directory")
        context.set_config_value("site", "site")
        context.set_config_value("time", dt(2020, 4, 5, 11, 23, 4, 5))
        context.set_config_value("to_archive", True)

        hw = HypernetsWriter(context)
        self.assertEqual(
            os.path.join("directory", "site", "2020", "4", "5"), hw.return_directory()
        )

    def test_return_directory_context_nottoarchive(self):
        context = Context()
        context.set_config_value("archive_directory", "directory")
        context.set_config_value("site", "site")
        context.set_config_value("time", dt(2020, 4, 5, 11, 23, 4, 5))
        context.set_config_value("to_archive", False)

        hw = HypernetsWriter(context)
        self.assertEqual(os.path.join("directory"), hw.return_directory())

    def test_return_directory_noinput(self):
        hw = HypernetsWriter()
        self.assertRaises(ValueError, hw.return_directory)

    @patch(
        "hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter.return_fmt",
        return_value="nc",
    )
    @patch(
        "hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter.return_directory",
        return_value="directory",
    )
    @patch(
        "hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter._write_netcdf"
    )
    def test_write_netcdf(self, mock_write, mock_dir, mock_fmt):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        hw.write(ds)
        mock_write.assert_called_once_with(
            ds, os.path.join("directory", "test.nc"), compression_level=None
        )

    @patch(
        "hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter.return_fmt",
        return_value="csv",
    )
    @patch(
        "hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter.return_directory",
        return_value="directory",
    )
    @patch(
        "hypernets_processor.data_io.tests.test_hypernets_writer.HypernetsWriter._write_csv"
    )
    def test_write_csv(self, mock_write, mock_dir, mock_fmt):
        ds = Dataset()
        ds.attrs["product_name"] = "test"

        hw = HypernetsWriter()

        hw.write(ds)
        mock_write.assert_called_once_with(ds, os.path.join("directory", "test.csv"))

    def test__write_netcdf(self):

        ds = MagicMock()
        path = "test.nc"

        HypernetsWriter._write_netcdf(ds, path)

        ds.to_netcdf.assert_called_once_with(
            path, encoding={}, engine="netcdf4", format="netCDF4"
        )

    def test_fill_ds(self):
        ds = Dataset()
        ds["array_variable1"] = obsarray.create_var([7, 8], np.float32)
        ds["array_variable2"] = obsarray.create_var([7, 8], np.float32)

        ds["array_variable1"][2, 3] = np.nan
        ds["array_variable2"][2, 3] = np.nan

        HypernetsWriter.fill_ds(ds)

        self.assertTrue(np.all(ds["array_variable1"] == 9.96921e36))
        self.assertTrue(np.all(ds["array_variable2"] == 9.96921e36))


if __name__ == "__main__":
    unittest.main()
