"""
Testing for Hypernets file writer
"""

import numpy as np
import datetime
from os.path import join as pjoin
from hypernets_processor import HypernetsDSBuilder
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.filename_util import FilenameUtil


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


N_WAVELENGTHS = 271


def create_sample_W_L1B_file(output_directory, n_sequence, site):
    dsb = HypernetsDSBuilder()
    dataset = dsb.create_ds_template({"wavelength": N_WAVELENGTHS, "sequence": n_sequence}, "W_L1B")

    # wavelength data
    # todo - fix issue with wavelength assignment as coordinate
    dataset["wavelength"].data = np.concatenate((np.arange(400, 1000, 3), np.arange(1000, 1700+10, 10)))
    dataset["bandwidth"].data = np.random.normal(1.0, 0.5, N_WAVELENGTHS)

    # geometry data
    dataset["viewing_azimuth_angle"].data = np.linspace(30, 60, n_sequence)
    dataset["viewing_zenith_angle"].data = np.linspace(30, 60, n_sequence)
    dataset["solar_azimuth_angle"].data = np.linspace(30, 60, n_sequence)
    dataset["solar_zenith_angle"].data = np.linspace(30, 60, n_sequence)

    # observation data
    dataset["upwelling_radiance"].data = np.round(np.random.rand(N_WAVELENGTHS, n_sequence), 3)
    # dataset["u_random_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, n_sequence))
    # dataset["u_systematic_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS,n_sequence))
    # dataset["cov_random_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))
    # dataset["cov_systematic_reflectance"].data = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))

    # time data
    dataset["acquisition_time"].data = np.arange(10000, 10000+n_sequence, dtype=int)

    # make file name
    fu = FilenameUtil()
    filename = fu.create_file_name_l1b("w", site, datetime.datetime.today(), "0.00")

    # write file
    hw = HypernetsWriter()
    hw.write(dataset, pjoin(output_directory, filename))


if __name__ == '__main__':
    create_sample_W_L1B_file(".", 26,  "BSBE")
