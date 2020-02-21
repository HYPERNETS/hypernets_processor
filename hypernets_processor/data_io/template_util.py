"""
TemplateUtil class
"""

import numpy as np
from hypernets_processor.data_io.dataset_util import DatasetUtil

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


FILL_VALUE = -1


class TemplateUtil:
    """
    Class to create template Hypernets datasets
    """

    @staticmethod
    def add_common_variables(dataset, n_wavelengths, n_series):
        """
        Returns dataset with additional common variables

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        du = DatasetUtil()

        metadata = {"resource_title":"HYPERNETS network dataset of spectral surface reflectance, downwelling irradiance and upwelling\
        and downwelling radiance above the sea surface",
        "resource_abstract": "The HYPERNETS project (Horizon 2020 research and innovation, grant agreement No\
        775983) has the overall aim to provide high quality in situ measurements to support the (visible/SWIR) optical\
        Copernicus products. Therefore a new multi-head hyperspectral spectroradiometer dedicated to land and water\
        surface reflectance validation with instrument pointing capabilities and embedded calibration device has been\
        established. The instrument has been deployed at 24 sites covering a range of water and land types and a range of\
        climatic and logistic conditions (www.hypernets.eu).",
        "metadata_language":"eng",
        "lineage": "Dataset is quality assured (ATBD document link)",
        "unique_resource_code_identifier": "doi.xxxx",
        "spatial_data_theme":"point",
        "topic_category":"oceans, environment, inland waters, geoscientific information",
        "keywords":"reflectance, radiance, irradiance, point dataset, [we did not find any relevant keyword in\
        http://inspire.ec.europa.eu/codelist/] ",
        "data_created":"2019-07-19 10:00:15 UTC",
        "responsible_party":"Royal Belgian Institute for Natural Sciences, Directorate Natural Environment, REMSEM",
        "creator_name":"Goyens Clémence",
        "creator_email":"cgoyens@naturalsciences.be",
        "project":"HYPERNETS",
        "acknowledgement":"HYPERNETS project is funded by Horizon 2020 research and innovation programm, grant\
        agreement No 775983. Consortium of HYPERNETS project, PI of hypernets test sites, ... are acknowledged.",
        "licence":"Attribution-NonCommercial-NoDerivs CC BY-NC-ND",
        "limitations_on_public_access":"no limitations to public access",
        "conditions_applying_to_access_and_use":"no conditions to access and use",
        "degree_of_conformity":"no evaluated",}

        # Add metadata
        dataset.attrs = metadata

        # Create wavelength variable
        wavelength = du.create_vector_variable(n_wavelengths,
                                               dim_names=["wavelength"],
                                               dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(wavelength, data_type=np.uint16, scale_factor=1.0, offset=0.0)
        dataset["wavelength"] = wavelength

        # Create bandwidth variable
        bandwidth = du.create_vector_variable(n_wavelengths,
                                               dim_names=["wavelength"],
                                               dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(wavelength, data_type=np.uint16, scale_factor=1.0, offset=0.0)
        dataset["bandwidth"] = bandwidth

        # Create viewing angle azimuth variable
        viewing_angle_azimuth = du.create_vector_variable(n_series,
                                                          dim_names=["series"],
                                                          dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(viewing_angle_azimuth, data_type=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["viewing_angle_azimuth"] = viewing_angle_azimuth

        # Create viewing angle azimuth variable
        viewing_angle_zenith = du.create_vector_variable(n_series,
                                                         dim_names=["series"],
                                                         dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(viewing_angle_zenith, data_type=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["viewing_angle_zenith"] = viewing_angle_zenith

        # Create sun angle azimuth variable
        sun_angle_azimuth = du.create_vector_variable(n_series,
                                                      dim_names=["series"],
                                                      dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(viewing_angle_azimuth, data_type=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["sun_angle_azimuth"] = sun_angle_azimuth

        # Create sun angle azimuth variable
        sun_angle_zenith = du.create_vector_variable(n_series,
                                                     dim_names=["series"],
                                                     dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(sun_angle_zenith, data_type=np.uint16, scale_factor=0.1, offset=0.0)
        dataset["sun_angle_zenith"] = sun_angle_zenith

        # Create time variable
        time = du.create_vector_variable(n_series,
                                         dim_names=["series"],
                                         dtype=np.int32, fill_value=FILL_VALUE)
        du.add_encoding(time, data_type=np.int32, scale_factor=0.1, offset=0.0)
        dataset["acquisition_time"] = time
        # todo - Does time have to have a precision better than 1 s?

        return dataset

    @staticmethod
    def add_l1_variables(dataset, n_wavelengths, n_series):
        """
        Returns dataset with additional Level 1 variables

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        du = DatasetUtil()

        # Create random radiance uncertainty variable
        u_r_rad = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(u_r_rad, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_radiance"] = u_r_rad

        # Create systematic radiance uncertainty
        u_s_rad = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(u_s_rad, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_radiance"] = u_s_rad

        # Create radiance wavelength-to-wavelength random covariance matrix variable
        cov_r_rad = du.create_array_variable(n_wavelengths, n_wavelengths,
                                             dim_names=["wavelength", "wavelength"],
                                             dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(cov_r_rad, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_radiance"] = cov_r_rad

        # Create radiance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_rad = du.create_array_variable(n_wavelengths, n_wavelengths,
                                             dim_names=["wavelength", "wavelength"],
                                             dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(cov_s_rad, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_systematic_radiance"] = cov_s_rad

        # Create radiance variable
        rad = du.create_array_variable(n_series, n_wavelengths,
                                       dim_names=["wavelength", "series"],
                                       dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(rad, data_type=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["radiance"] = rad

        return dataset

    @staticmethod
    def add_l2a_variables(dataset, n_wavelengths, n_series):
        """
        Returns dataset with additional Level 2a variables

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        du = DatasetUtil()

        # Create random reflectance uncertainty variable
        u_r_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(u_r_ref, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_reflectance"] = u_r_ref

        # Create systematic reflectance uncertainty variable
        u_s_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(u_s_ref, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_reflectance"] = u_s_ref

        # Create reflectance wavelength-to-wavelength random covariance matrix variable
        cov_r_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(cov_r_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_reflectance"] = cov_r_reflectance

        # Create reflectance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(cov_s_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
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
                                       dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(ref, data_type=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["reflectance"] = ref

        return dataset

    @staticmethod
    def add_l2b_variables(dataset, n_wavelengths, n_series):
        """
        Returns dataset with additional Level 2b variables

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        du = DatasetUtil()

        # Create random reflectance uncertainty variable
        u_r_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(u_r_ref, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_random_reflectance"] = u_r_ref

        # Create systematic reflectance uncertainty variable
        u_s_ref = du.create_array_variable(n_series, n_wavelengths,
                                           dim_names=["wavelength", "series"],
                                           dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(u_s_ref, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["u_systematic_reflectance"] = u_s_ref

        # Create reflectance wavelength-to-wavelength random covariance matrix variable
        cov_r_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(cov_r_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
        dataset["cov_random_reflectance"] = cov_r_reflectance

        # Create reflectance wavelength-to-wavelength systematic covariance matrix variable
        cov_s_reflectance = du.create_array_variable(n_wavelengths, n_wavelengths,
                                                     dim_names=["wavelength", "wavelength"],
                                                     dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(cov_s_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
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
                                       dtype=np.float32, fill_value=FILL_VALUE)
        du.add_encoding(ref, data_type=np.uint16, scale_factor=0.001, offset=0.0)
        dataset["reflectance"] = ref

        return dataset


if __name__ == '__main__':
    pass
