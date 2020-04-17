"""
Tests for HypernetsWriter class
"""

import unittest
import datetime
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


COMMON_VARIABLES = ["wavelength", "bandwidth", "viewing_angle_azimuth", "viewing_angle_zenith", "sun_angle_azimuth",
                    "sun_angle_zenith", "acquisition_time"]
L1_RAD_VARIABLES = ["u_random_radiance", "u_systematic_radiance", "cov_random_radiance",
                "cov_systematic_radiance", "radiance"]
L1_IRR_VARIABLES = ["u_random_irradiance", "u_systematic_irradiance", "cov_random_irradiance",
                "cov_systematic_irradiance", "irradiance"]
L2A_VARIABLES = ["u_random_reflectance", "u_systematic_reflectance", "cov_random_reflectance",
                "cov_systematic_reflectance", "reflectance"]
L2B_VARIABLES = ["u_random_reflectance", "u_systematic_reflectance", "cov_random_reflectance",
                "cov_systematic_reflectance", "reflectance"]


class TestHypernetsWriter(unittest.TestCase):
    def test_create_template_dataset_l1_rad_land(self):
        ds = HypernetsWriter.create_template_dataset_l1_rad(271, 10, network="land")

        self.assertEqual(len(COMMON_VARIABLES) + len(L1_RAD_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L1_RAD_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling radiance",
                         ds.attrs["resource_title"])
        self.assertEqual("Hunt Sam", ds.attrs["creator_name"])

    def test_create_template_dataset_l1_rad_water(self):
        ds = HypernetsWriter.create_template_dataset_l1_rad(271, 10, network="water")

        self.assertEqual(len(COMMON_VARIABLES) + len(L1_RAD_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L1_RAD_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling radiance",
                         ds.attrs["resource_title"])
        self.assertEqual("Goyens Clémence", ds.attrs["creator_name"])

    def test_create_template_dataset_l1_irr_land(self):
        ds = HypernetsWriter.create_template_dataset_l1_irr(271, 10, network="land")

        self.assertEqual(len(COMMON_VARIABLES) + len(L1_RAD_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L1_IRR_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        self.assertEqual("eng", ds.attrs["metadata_language"])
        self.assertEqual("HYPERNETS network dataset of downwelling irradiance and upwelling and downwelling radiance",
                         ds.attrs["resource_title"])
        self.assertEqual("Hunt Sam", ds.attrs["creator_name"])

    def test_create_template_dataset_l1_irr_water(self):
        ds = HypernetsWriter.create_template_dataset_l1_rad(271, 10, network="water")

        self.assertEqual(len(COMMON_VARIABLES) + len(L1_RAD_VARIABLES), len(ds.data_vars) + len(ds.coords))

        for var in COMMON_VARIABLES:
            self.assertIsNotNone(ds.variables[var])

        for var in L1_RAD_VARIABLES:
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
