"""
Tests for HypernetsWriter class
"""

import unittest
import datetime
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


COMMON_VARIABLES = ["wavelength", "bandwidth", "viewing_angle_azimuth", "viewing_angle_zenith", "sun_angle_azimuth",
                    "sun_angle_zenith", "acquisition_time"]
L1_VARIABLES = ["u_random_radiance", "u_systematic_radiance", "cov_random_radiance",
                "cov_systematic_radiance", "radiance"]
L2A_VARIABLES = ["u_random_reflectance", "u_systematic_reflectance", "cov_random_reflectance",
                "cov_systematic_reflectance", "reflectance"]
L2B_VARIABLES = ["u_random_reflectance", "u_systematic_reflectance", "cov_random_reflectance",
                "cov_systematic_reflectance", "reflectance"]


class TestHypernetsWriter(unittest.TestCase):
    def test_create_template_dataset_l1_land(self):
        ds = HypernetsWriter.create_template_dataset_l1(271, 10, network="land")

        self.assertEqual(len(COMMON_VARIABLES) + len(L1_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L1_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling radiance",
                         ds.attrs["resource_title"])
        self.assertEqual("Hunt Sam", ds.attrs["creator_name"])

    def test_create_template_dataset_l1_water(self):
        ds = HypernetsWriter.create_template_dataset_l1(271, 10, network="water")

        self.assertEqual(len(COMMON_VARIABLES) + len(L1_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L1_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling radiance",
                         ds.attrs["resource_title"])
        self.assertEqual("Goyens Clémence", ds.attrs["creator_name"])

    def test_create_template_dataset_l2a_land(self):
        ds = HypernetsWriter.create_template_dataset_l2a(271, 10, network="land")

        self.assertEqual(len(COMMON_VARIABLES) + len(L2A_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L2A_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of spectral surface reflectance",
                         ds.attrs["resource_title"])
        self.assertEqual("Hunt Sam", ds.attrs["creator_name"])

    def test_create_template_dataset_l2a_water(self):
        ds = HypernetsWriter.create_template_dataset_l2a(271, 10, network="water")

        self.assertEqual(len(COMMON_VARIABLES) + len(L2A_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L2A_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of spectral surface reflectance",
                         ds.attrs["resource_title"])
        self.assertEqual("Goyens Clémence", ds.attrs["creator_name"])

    def test_create_template_dataset_l2b_land(self):
        ds = HypernetsWriter.create_template_dataset_l2b(271, 10, network="land")

        self.assertEqual(len(COMMON_VARIABLES) + len(L2B_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L2B_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of spectral surface reflectance",
                         ds.attrs["resource_title"])
        self.assertEqual("Hunt Sam", ds.attrs["creator_name"])

    def test_create_template_dataset_l2b_water(self):
        ds = HypernetsWriter.create_template_dataset_l2b(271, 10, network="water")

        self.assertEqual(len(COMMON_VARIABLES) + len(L2B_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L2B_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of spectral surface reflectance",
                         ds.attrs["resource_title"])
        self.assertEqual("Goyens Clémence", ds.attrs["creator_name"])

    def test_create_file_name_l1(self):

        fname = HypernetsWriter.create_file_name_l1("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_RAD_201804031100_v0.00.nc", fname)

    def test_create_file_name_l2a(self):

        fname = HypernetsWriter.create_file_name_l2a("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_REF_201804031100_v0.00.nc", fname)

    def test_create_file_name_l2b(self):

        fname = HypernetsWriter.create_file_name_l2b("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_REFD_20180403_v0.00.nc", fname)


if __name__ == '__main__':
    unittest.main()
