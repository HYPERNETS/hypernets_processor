"""
Testing for Hypernets file writer
"""

import numpy as np
import datetime
from os.path import join as pjoin
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


N_WAVELENGTHS = 271


def create_sample_file(output_directory, n_series, network, site):
    hw = HypernetsWriter()
    dataset = hw.create_template_dataset_l2a(N_WAVELENGTHS, n_series, network=network)

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
    filename = hw.create_file_name_l2a(network, site, datetime.datetime.today(), "0.00")
    hw.write(dataset, pjoin(output_directory, filename))


if __name__ == '__main__':
    create_sample_file(".", 26, "land", "gbna")
