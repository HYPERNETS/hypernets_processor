"""
Tests for TemplateUtil class
"""

import unittest
import xarray
from hypernets_processor.data_io.template_util import TemplateUtil
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestTemplateUtil(unittest.TestCase):
    def test_add_common_metadata(self):
        dataset = xarray.Dataset()

        TemplateUtil.add_common_metadata(dataset)

        self.assertEqual("eng", dataset.attrs["metadata_language"])

    def test_add_l1_metadata(self):
        dataset = xarray.Dataset()

        TemplateUtil.add_l1_metadata(dataset)

        self.assertEqual("HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling radiance",
                         dataset.attrs["resource_title"])

    def test_add_l2_metadata(self):
        dataset = xarray.Dataset()

        TemplateUtil.add_l2_metadata(dataset)

        self.assertEqual("HYPERNETS network dataset of spectral surface reflectance",
                         dataset.attrs["resource_title"])

    def test_add_land_network_metadata(self):
        dataset = xarray.Dataset()

        TemplateUtil.add_land_network_metadata(dataset)

        self.assertEqual("Hunt Sam", dataset.attrs["creator_name"])

    def test_add_water_network_metadata(self):
        dataset = xarray.Dataset()

        TemplateUtil.add_water_network_metadata(dataset)

        self.assertEqual("Goyens Clémence", dataset.attrs["creator_name"])


if __name__ == '__main__':
    unittest.main()
