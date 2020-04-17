"""
TemplateUtil class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.data_io.metadata import COMMON_METADATA, L1_METADATA, L2_METADATA, \
    LAND_NETWORK_METADATA, WATER_NETWORK_METADATA
import numpy as np

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


# todo - add flags


class TemplateUtil:
    """
    Class to create template Hypernets datasets
    """

    @staticmethod
    def add_common_variables(dataset, n_wavelengths, n_series):
        """
        Adds common variables to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series
        """

        du = DatasetUtil()

        # Create wavelength variable
        wavelength = du.create_vector_variable(n_wavelengths, dim_name="wavelength", dtype=np.float32)
        du.add_encoding(wavelength, dtype=np.uint16, scale_factor=1.0, offset=0.0)
        dataset["wavelength"] = wavelength

        # Create bandwidth variable
        bandwidth = du.create_vector_variable(n_wavelengths, dim_name="wavelength", dtype=np.float32)
        du.add_encoding(wavelength, dtype=np.uint16, scale_factor=1.0, offset=0.0)
        dataset["bandwidth"] = bandwidth

        # Create viewing angle azimuth variable
        viewing_angle_azimuth = du.create_vector_variable(n_series, dim_name="series", dtype=np.float32)
        du.add_encoding(viewing_angle_azimuth, dtype=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["viewing_angle_azimuth"] = viewing_angle_azimuth

        # Create viewing angle azimuth variable
        viewing_angle_zenith = du.create_vector_variable(n_series, dim_name="series", dtype=np.float32)
        du.add_encoding(viewing_angle_zenith, dtype=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["viewing_angle_zenith"] = viewing_angle_zenith

        # Create sun angle azimuth variable
        sun_angle_azimuth = du.create_vector_variable(n_series, dim_name="series", dtype=np.float32)
        du.add_encoding(viewing_angle_azimuth, dtype=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["sun_angle_azimuth"] = sun_angle_azimuth

        # Create sun angle azimuth variable
        sun_angle_zenith = du.create_vector_variable(n_series, dim_name="series", dtype=np.float32)
        du.add_encoding(sun_angle_zenith, dtype=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["sun_angle_zenith"] = sun_angle_zenith

        # Create time variable
        time = du.create_vector_variable(n_series, dim_name="series", dtype=np.int32)
        du.add_encoding(time, dtype=np.int32, scale_factor=0.1, offset=0.0)
        dataset["acquisition_time"] = time
        # todo - Does time have to have a precision better than 1 s?

    @staticmethod
    def add_l1_rad_variables(dataset, n_wavelengths, n_series):
        """
        Adds additional Level 1 radiance variables to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series
        """

        du = DatasetUtil()

        # Create random radiance uncertainty variable
        u_r_rad = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_r_rad, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_radiance"] = u_r_rad

        # Create systematic radiance uncertainty
        u_s_rad = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_s_rad, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_radiance"] = u_s_rad

        # Create radiance wavelength-to-wavelength random covariance matrix variable
        cov_r_rad = du.create_array_variable(n_wavelengths, n_wavelengths,
                                             dim_names=["wavelength", "wavelength"],
                                             dtype=np.float32)
        du.add_encoding(cov_r_rad, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_radiance"] = cov_r_rad

        # Create radiance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_rad = du.create_array_variable(n_wavelengths, n_wavelengths,
                                             dim_names=["wavelength", "wavelength"],
                                             dtype=np.float32)
        du.add_encoding(cov_s_rad, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_systematic_radiance"] = cov_s_rad

        # Create radiance variable
        rad = du.create_array_variable(n_series, n_wavelengths,
                                       dim_names=["wavelength", "series"],
                                       dtype=np.float32)
        du.add_encoding(rad, dtype=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["radiance"] = rad

    @staticmethod
    def add_l1_irr_variables(dataset, n_wavelengths, n_series):
        """
        Adds additional Level 1 irradiance variables to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series
        """

        du = DatasetUtil()

        # Create random irradiance uncertainty variable
        u_r_irr = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_r_irr, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_irradiance"] = u_r_irr

        # Create systematic irradiance uncertainty
        u_s_irr = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_s_irr, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_irradiance"] = u_s_irr

        # Create irradiance wavelength-to-wavelength random covariance matrix variable
        cov_r_irr = du.create_array_variable(n_wavelengths, n_wavelengths,
                                             dim_names=["wavelength", "wavelength"],
                                             dtype=np.float32)
        du.add_encoding(cov_r_irr, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_irradiance"] = cov_r_irr

        # Create radiance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_irr = du.create_array_variable(n_wavelengths, n_wavelengths,
                                             dim_names=["wavelength", "wavelength"],
                                             dtype=np.float32)
        du.add_encoding(cov_s_irr, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_systematic_irradiance"] = cov_s_irr

        # Create radiance variable
        irr = du.create_array_variable(n_series, n_wavelengths,
                                       dim_names=["wavelength", "series"],
                                       dtype=np.float32)
        du.add_encoding(irr, dtype=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["irradiance"] = irr

    @staticmethod
    def add_l2a_variables(dataset, n_wavelengths, n_series):
        """
        Adds additional Level 2a variables to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series
        """

        du = DatasetUtil()

        # Create random reflectance uncertainty variable
        u_r_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_r_ref, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_reflectance"] = u_r_ref

        # Create systematic reflectance uncertainty variable
        u_s_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_s_ref, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_reflectance"] = u_s_ref

        # Create reflectance wavelength-to-wavelength random covariance matrix variable
        cov_r_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32)
        du.add_encoding(cov_r_reflectance, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_reflectance"] = cov_r_reflectance

        # Create reflectance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32)
        du.add_encoding(cov_s_reflectance, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_systematic_reflectance"] = cov_s_reflectance

        # Create reflectance variable
        ref = du.create_array_variable(n_series, n_wavelengths,
                                       dim_names=["wavelength", "series"],
                                       standard_name="surface_bidirectional_reflectance",
                                       long_name='The surface called "surface" means the lower boundary of the'
                                                 'atmosphere. "Bidirectional_reflectance" depends on the angles'
                                                 'of incident and measured radiation. Reflectance is the ratio of'
                                                 'the energy of the reflected to the incident radiation. A coordinate'
                                                 'variable of radiation_wavelength or radiation_frequency can be'
                                                 'used to specify the wavelength or frequency, respectively, of the radia'
                                                 'tion.',
                                       dtype=np.float32)
        du.add_encoding(ref, dtype=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["reflectance"] = ref

    @staticmethod
    def add_l2b_variables(dataset, n_wavelengths, n_series):
        """
        Adds additional Level 2b variables to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series
        """

        du = DatasetUtil()

        # Create random reflectance uncertainty variable
        u_r_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_r_ref, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_reflectance"] = u_r_ref

        # Create systematic reflectance uncertainty variable
        u_s_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32)
        du.add_encoding(u_s_ref, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_reflectance"] = u_s_ref

        # Create reflectance wavelength-to-wavelength random covariance matrix variable
        cov_r_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32)
        du.add_encoding(cov_r_reflectance, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_reflectance"] = cov_r_reflectance

        # Create reflectance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32)
        du.add_encoding(cov_s_reflectance, dtype=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_systematic_reflectance"] = cov_s_reflectance

        # Create reflectance variable
        ref = du.create_array_variable(n_series, n_wavelengths,
                                       dim_names=["wavelength", "series"],
                                       standard_name="surface_bidirectional_reflectance",
                                       long_name='The surface called "surface" means the lower boundary of the'
                                                 'atmosphere. "Bidirectional_reflectance" depends on the angles'
                                                 'of incident and measured radiation. Reflectance is the ratio of'
                                                 'the energy of the reflected to the incident radiation. A coordinate'
                                                 'variable of radiation_wavelength or radiation_frequency can be'
                                                 'used to specify the wavelength or frequency, respectively, of the radia'
                                                 'tion.',
                                       dtype=np.float32)
        du.add_encoding(ref, dtype=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["reflectance"] = ref

    @staticmethod
    def add_common_metadata(dataset):
        """
        Adds common metadata to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset
        """

        dataset.attrs.update(COMMON_METADATA)

    @staticmethod
    def add_land_network_metadata(dataset):
        """
        Adds land network metadata to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset
        """

        dataset.attrs.update(LAND_NETWORK_METADATA)

    @staticmethod
    def add_water_network_metadata(dataset):
        """
        Adds water network metadata to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset
        """

        dataset.attrs.update(WATER_NETWORK_METADATA)

    @staticmethod
    def add_l1_rad_metadata(dataset):
        """
        Adds Level 1 radiance metadata to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset
        """

        dataset.attrs.update(L1_METADATA)

    @staticmethod
    def add_l1_irr_metadata(dataset):
        """
        Adds Level 1 irradiance metadata to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset
        """

        dataset.attrs.update(L1_METADATA)

    @staticmethod
    def add_l2_metadata(dataset):
        """
        Adds Level 2 metadata to dataset

        :type dataset: xarray.Dataset
        :param dataset: dataset
        """

        dataset.attrs.update(L2_METADATA)


if __name__ == '__main__':
    pass
