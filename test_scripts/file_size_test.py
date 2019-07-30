import numpy as np
from test_scripts.dataset_util import DatasetUtil
import xarray as xr


N_WAVELENGTHS = 271


def create_test_file(filename, n_sequences, n_viewings):
    du = DatasetUtil()

    dataset = xr.Dataset()

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

    dataset.attrs = metadata

    wavelength = du.create_vector_variable(N_WAVELENGTHS,
                                           dim_names=["wavelength"],
                                           dtype=np.float32, fill_value=-1)
    du.add_encoding(wavelength, data_type=np.uint16, scale_factor=1.0, offset=0.0)
    wavelength.data[:] = np.concatenate((np.arange(400, 1000, 3), np.arange(1000, 1700+10, 10)))
    dataset["wavelength"] = wavelength

    viewing_angle_azimuth = du.create_vector_variable(n_viewings,
                                                      dim_names=["viewing_num"],
                                                      dtype=np.float32, fill_value=-1)
    du.add_encoding(viewing_angle_azimuth, data_type=np.uint16, scale_factor=0.1, offset=0.0)
    viewing_angle_azimuth.data[:] = np.linspace(30, 60, n_viewings)
    dataset["viewing_angle_azimuth"] = viewing_angle_azimuth

    viewing_angle_zenith = du.create_vector_variable(n_viewings,
                                                     dim_names=["viewing_num"],
                                                     dtype=np.float32, fill_value=-1)
    du.add_encoding(viewing_angle_zenith, data_type=np.uint16, scale_factor=0.1, offset=0.0)
    viewing_angle_zenith.data[:] = np.linspace(30, 60, n_viewings)
    dataset["viewing_angle_zenith"] = viewing_angle_zenith

    u_r_var = du.create_array3d_variable(n_sequences, n_viewings, N_WAVELENGTHS,
                                         dim_names=["wavelength", "viewing_num", "sequence_num"],
                                         dtype=np.float32, fill_value=-1)
    du.add_encoding(u_r_var, data_type=np.uint8, scale_factor=0.1, offset=0.0)
    u_r_var.data[:] = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, n_viewings, n_sequences))
    dataset["u_random_reflectance"] = u_r_var

    u_d_var = du.create_array3d_variable(n_sequences, n_viewings, N_WAVELENGTHS,
                                         dim_names=["wavelength", "viewing_num", "sequence_num"],
                                         dtype=np.float32, fill_value=-1)
    du.add_encoding(u_d_var, data_type=np.uint8, scale_factor=0.1, offset=0.0)
    u_d_var.data[:] = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, n_viewings, n_sequences))
    dataset["u_deployment_reflectance"] = u_d_var

    u_s_var = du.create_array3d_variable(n_sequences, n_viewings, N_WAVELENGTHS,
                                         dim_names=["wavelength", "viewing_num", "sequence_num"],
                                         dtype=np.float32, fill_value=-1)
    du.add_encoding(u_s_var, data_type=np.uint8, scale_factor=0.1, offset=0.0)
    u_s_var.data[:] = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, n_viewings, n_sequences))
    dataset["u_systematic_reflectance"] = u_s_var

    cov_r_reflectance = du.create_array_variable(N_WAVELENGTHS, N_WAVELENGTHS, dim_names=["wavelength", "wavelength"],
                                                 dtype=np.float32, fill_value=-1)
    du.add_encoding(cov_r_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
    cov_r_reflectance.data[:] = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))
    dataset["cov_random_reflectance"] = cov_r_reflectance

    cov_d_reflectance = du.create_array_variable(N_WAVELENGTHS, N_WAVELENGTHS, dim_names=["wavelength", "wavelength"],
                                                 dtype=np.float32, fill_value=-1)
    du.add_encoding(cov_d_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
    cov_d_reflectance.data[:] = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))
    dataset["cov_deployment_reflectance"] = cov_d_reflectance

    cov_s_reflectance = du.create_array_variable(N_WAVELENGTHS, N_WAVELENGTHS, dim_names=["wavelength", "wavelength"],
                                                 dtype=np.float32, fill_value=-1)
    du.add_encoding(cov_s_reflectance, data_type=np.uint8, scale_factor=0.1, offset=0.0)
    cov_s_reflectance.data[:] = np.random.normal(1.0, 0.5, (N_WAVELENGTHS, N_WAVELENGTHS))
    dataset["cov_systematic_reflectance"] = cov_s_reflectance

    ref = du.create_array3d_variable(n_sequences, n_viewings, N_WAVELENGTHS,
                                     dim_names=["wavelength", "viewing_num", "sequence_num"],
                                     standard_name="surface_bidirectional_reflectance",
                                     long_name='The surface called "surface" means the lower boundary of the'
                                               'atmosphere. "Bidirectional_reflectance" depends on the angles'
                                               'of incident and measured radiation. Reflectance is the ratio of'
                                               'the energy of the reflected to the incident radiation. A coordinate'
                                               'variable of radiation_wavelength or radiation_frequency can be'
                                               'used to specify the wavelength or frequency, respectively, of the radia'
                                               'tion.',
                                     dtype=np.float32, fill_value=-1)
    du.add_encoding(ref, data_type=np.uint16, scale_factor=0.001, offset=0.0)
    ref.data[:] = np.round(np.random.rand(N_WAVELENGTHS, n_viewings, n_sequences), 3)
    dataset["reflectance"] = ref

    # Does time have to have a precision better than 1 s?
    time = du.create_array_variable(n_sequences, n_viewings,
                                    dim_names=["viewing_num", "sequence_num"],
                                    dtype=np.int32, fill_value=-1)
    du.add_encoding(time, data_type=np.int32, scale_factor=0.1, offset=0.0)
    time.data[:] = (np.random.normal(1.0, 0.5, (n_viewings, n_sequences))*100000).astype(int)
    dataset["acquisition_time"] = time

    dataset.to_netcdf(filename)


if __name__ == '__main__':
    create_test_file("HYPERNETS_REF_SP_GBNA_20180403_v0.00.nc", n_viewings=26, n_sequences=14)
    create_test_file("HYPERNETS_REF_CP_GBNA_20180403_v0.00.nc", n_viewings=800, n_sequences=1)
