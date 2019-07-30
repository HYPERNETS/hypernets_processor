import numpy as np
from test_scripts.dataset_util import DatasetUtil
import xarray as xr

n_measurements = 800
n_wavelengths = 271

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

wavelength = du.create_vector_variable(n_wavelengths, dim_names=["wavelength"], dtype=np.float32, fill_value=-1)
du.add_encoding(wavelength, data_type=np.uint16, scale_factor=1.0, offset=0.0)
wavelength.data[:] = np.concatenate((np.arange(400, 1000, 3), np.arange(1000, 1700+10, 10)))
dataset["wavelength"] = wavelength

viewing_angle_azimuth = du.create_vector_variable(n_measurements, dim_names=["measurement_number"], dtype=np.float32, fill_value=-1)
du.add_encoding(viewing_angle_azimuth, data_type=np.uint16, scale_factor=0.1, offset=0.0)
viewing_angle_azimuth.data[:] = np.linspace(30, 60, n_measurements)
dataset["viewing_angle_azimuth"] = viewing_angle_azimuth

viewing_angle_zenith = du.create_vector_variable(n_measurements, dim_names=["measurement_number"], dtype=np.float32, fill_value=-1)
du.add_encoding(viewing_angle_zenith, data_type=np.uint16, scale_factor=0.1, offset=0.0)
viewing_angle_zenith.data[:] = np.linspace(30, 60, n_measurements)
dataset["viewing_angle_zenith"] = viewing_angle_zenith

u_r_var = du.create_array_variable(n_measurements, n_wavelengths, dim_names=["wavelength", "measurement_number"], dtype=np.float32, fill_value=-1)
du.add_encoding(u_r_var, data_type=np.uint8, scale_factor=0.1, offset=0.0)
u_r_var.data[:] = np.random.normal(1.0, 0.5, (n_wavelengths, n_measurements))
dataset["u_random_reflectance"] = u_r_var

u_d_var = du.create_array_variable(n_measurements, n_wavelengths, dim_names=["wavelength", "measurement_number"], dtype=np.float32, fill_value=-1)
du.add_encoding(u_d_var, data_type=np.uint8, scale_factor=0.1, offset=0.0)
u_d_var.data[:] = np.random.normal(1.0, 0.5, (n_wavelengths, n_measurements))
dataset["u_deployment_reflectance"] = u_d_var

u_s_var = du.create_array_variable(n_measurements, n_wavelengths, dim_names=["wavelength", "measurement_number"], dtype=np.float32, fill_value=-1)
du.add_encoding(u_s_var, data_type=np.uint8, scale_factor=0.1, offset=0.0)
u_s_var.data[:] = np.random.normal(1.0, 0.5, (n_wavelengths, n_measurements))
dataset["u_systematic_reflectance"] = u_s_var

ref = du.create_array_variable(n_measurements, n_wavelengths, standard_name="surface_bidirectional_reflectance",
                               long_name='The surface called "surface" means the lower boundary of the\
                                          atmosphere. "Bidirectional_reflectance" depends on the angles\
                                          of incident and measured radiation. Reflectance is the ratio of\
                                          the energy of the reflected to the incident radiation. A coordinate\
                                          variable of radiation_wavelength or radiation_frequency can be\
                                          used to specify the wavelength or frequency, respectively, of the radiation.',
                               dim_names=["wavelength", "measurement_number"], dtype=np.float32, fill_value=-1)
du.add_encoding(ref, data_type=np.uint16, scale_factor=0.001, offset=0.0)
ref.data[:] = np.round(np.random.rand(n_wavelengths, n_measurements), 3)
dataset["reflectance"] = ref

dataset.to_netcdf("HYPERNETS_REF_CP_GBNA_20180403_v0.00.nc")
