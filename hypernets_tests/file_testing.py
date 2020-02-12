"""
Testing for Hypernets file writer
"""

import numpy as np
from hypernets_tests.hypernets_writer import HypernetsWriter

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


N_WAVELENGTHS = 271


def create_test_file(filename, n_series):
    hw = HypernetsWriter()
    dataset = hw.create_empty_dataset(N_WAVELENGTHS, n_series)

    # wavelength data
    dataset["wavelength"].data = np.concatenate((np.arange(400, 1000, 3), np.arange(1000, 1700+10, 10)))
    dataset["bandwidth"].data = np.random.normal(1.0, 0.5, N_WAVELENGTHS)

    # geometry data
    dataset["viewing_angle_azimuth"].data = np.linspace(30, 60, n_series)
    dataset["viewing_angle_zenith"].data = np.linspace(30, 60, n_series)
    dataset["sun_angle_azimuth"].data = np.linspace(30, 60, n_series)
    dataset["sun_angle_zenith"].data = np.linspace(30, 60, n_series)

    # reflectance data
    dataset["reflectance"].data = np.round(np.random.rand(N_WAVELENGTHS, n_series), 3)
    dataset["u_random_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, n_series))
    dataset["u_systematic_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, n_series))
    dataset["cov_random_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))
    dataset["cov_systematic_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))

    # time data
    dataset["acquisition_time"].data = np.arange(10000, 10000+n_series, dtype=int)

    # write file
    dataset.to_netcdf(filename)


if __name__ == '__main__':
    create_test_file("HYPERNETS_L_GBNA_REF_201804031100_v0.00.nc", n_series=26)
