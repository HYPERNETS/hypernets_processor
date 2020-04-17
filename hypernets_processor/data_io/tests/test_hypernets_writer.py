"""
Tests for HypernetsWriter class
"""

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import datetime
import xarray
import numpy as np
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.version import __version__


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

    def test_write_netcdf(self):

        ds = MagicMock()
        path = "test.nc"

        HypernetsWriter.write(ds, path)

        ds.to_netcdf.assert_called_once_with(path, encoding={}, engine='netcdf4', format='netCDF4')

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l1_rad_land(self, mock_tu):

        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l1_rad(n_w, n_s, network="land")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l1_rad_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l1_rad_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_land_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l1_rad_water(self, mock_tu):

        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l1_rad(n_w, n_s, network="water")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l1_rad_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l1_rad_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_water_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l1_irr_land(self, mock_tu):
        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l1_irr(n_w, n_s, network="land")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l1_irr_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l1_irr_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_land_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l1_irr_water(self, mock_tu):
        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l1_irr(n_w, n_s, network="water")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l1_irr_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l1_irr_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_water_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l2a_land(self, mock_tu):
        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l2a(n_w, n_s, network="land")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l2a_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l2_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_land_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l2a_water(self, mock_tu):
        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l2a(n_w, n_s, network="water")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l2a_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l2_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_water_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l2b_land(self, mock_tu):
        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l2b(n_w, n_s, network="land")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l2b_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l2_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_land_network_metadata.assert_called_once_with(ds)

    @patch('hypernets_processor.data_io.hypernets_writer.TemplateUtil')
    def test_create_template_dataset_l2b_water(self, mock_tu):
        n_w = 271
        n_s = 10
        ds = HypernetsWriter.create_template_dataset_l2b(n_w, n_s, network="water")

        # test ds
        self.assertEqual(type(ds), xarray.Dataset)

        # test calls to TemplateUtil
        self.assertTrue(mock_tu.called)
        mock_tu.return_value.add_common_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_l2b_variables.assert_called_once_with(ds, n_w, n_s)
        mock_tu.return_value.add_common_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_l2_metadata.assert_called_once_with(ds)
        mock_tu.return_value.add_water_network_metadata.assert_called_once_with(ds)

    def test_create_file_name_l1_irr(self):

        fname = HypernetsWriter.create_file_name_l1_irr("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_IRR_201804031100_v0.00.nc", fname)

    def test_create_file_name_l1_rad(self):

        fname = HypernetsWriter.create_file_name_l1_rad("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_RAD_201804031100_v0.00.nc", fname)

    def test_create_file_name_l2a(self):

        fname = HypernetsWriter.create_file_name_l2a("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_REF_201804031100_v0.00.nc", fname)

    def test_create_file_name_l2b(self):

        fname = HypernetsWriter.create_file_name_l2b("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_REFD_20180403_v0.00.nc", fname)


if __name__ == '__main__':
    unittest.main()
