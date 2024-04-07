"""
Standard metadata for Hypernets L1, L2a and L2b files, for the land a water network
"""

# Sets of metadata are defined in the below dictionaries. Each entry in a dictionary defines one metadata with entry of
# its required value if applicable.
#
# Following the metadata set definitions a dictionary of is built with an entry for each Hypernets product type, with
# entry of its metadata built by combining the metadata from the metadata sets. This is called METADATA_DEFS
#
# Product metadata is defined following the specification defined in:
# Hypernets Team, Product Data Format Specification, v0.5 (2020)


# todo - update metadata so only required values are included


# Contributing metadata sets
# --------------------------

STANDARD_METADATA = {
    "type": "dataset",
    "abstract": "The HYPERNETS project (Horizon 2020 research and innovation, grant agreement "
    "No 775983) has the overall aim to provide high quality in situ measurements to"
    "support the (visible/SWIR) optical Copernicus products. Therefore a new "
    "multi-head hyperspectral spectroradiometer dedicated to land and water surface"
    " reflectance validation with instrument pointing capabilities and embedded "
    "calibration device has been established. The instrument has been deployed at "
    "24 sites covering a range of water and land types and a range of climatic and"
    "logistic conditions (www.hypernets.eu).",
    "conventions": "CFv72, NVS2.0",
    "format_version": "v2.0",
    "netcdf_version": "1.6",
    "processor_name": "hypernets_processor",
    "processor_version": "NaN",
    "processor_atbd": "https://hypernets-processor.readthedocs.io/en/latest/",
    "product_name": "NaN",
    "data_created": "NaN",  # adds on write not working currently
    "references": "https://hypernets-processor.readthedocs.io/en/latest/",
    "source": "surface observation",
    "comment": "Any free-format text is appropriate.",
    "easting": "longitude",
    "northing": "latitude",
    "acknowledgement": "HYPERNETS project is funded by Horizon 2020 research and innovation program, "
    "Grand Agreement No 775993. Consortium of project  of the Hypernets test sites,"
    " .... are greatly acknowledged.",
    "project_name": "H2020 HYPERNETS GN 775993",
    "language": "English",
    "operational_status": "operational",
    "limitations": "no limitations to public access",
    "licence": "Attribution-NonCommercial-NoDerivs CC BY-NC-ND",
    "conformity": "notEvaluated",
    "lineage": "Quality assured following www.hypernets.eu/docs/QC/",
    "instrument_configuration_file": "TBD",
    "history": "TBD",  # "2020-04-01T00:02:00Z :Creation, 2028-03-23T11:56:12Z :Reviewed calibration",
    "processor_configuration_file": "NaN",
    "sequence_id": "NaN",
    "system_id": "NaN",
    "site_id": "NaN",
    "site_latitude": "NaN",
    "site_longitude": "NaN",
    "source_file": "NaN",
    "system_temperature": "NaN",
    "system_pressure": "NaN",
    "illuminance": "NaN",
    "system_relative_humidity": "NaN",
}
COMPONENTS_METADATA = {  # "system_id": system_id,
    "instrument_id": "TBD",  # key metadata
    # "pointing_system_id": "TBD",  # key metadata
    # "calibration_device_id": "TBD",  # key metadata
    # "irr_vis_head_id": "TBD",  # key metadata
    # "rad_vis_head_id": "TBD",  # key metadata
    # "rain_sensor_id": "TBD",  # key metadata
    # "rgb_camera_id": "TBD",  # key metadata
}

CAL_METADATA = {
    "type": "dataset",
    "abstract": "The HYPERNETS project (Horizon 2020 research and innovation, grant agreement "
    "No 775983) has the overall aim to provide high quality in situ measurements to"
    "support the (visible/SWIR) optical Copernicus products. Therefore a new "
    "multi-head hyperspectral spectroradiometer dedicated to land and water surface"
    " reflectance validation with instrument pointing capabilities and embedded "
    "calibration device has been established. The instrument has been deployed at "
    "24 sites covering a range of water and land types and a range of climatic and"
    "logistic conditions (www.hypernets.eu).",
    "conventions": "CFv72, NVS2.0",
    "format_version": "v01.0",
    "netcdf_version": "1.6",
    "product_name": "NaN",
    "data_created": "NaN",
    "references": "https://hypernets-processor.readthedocs.io/en/latest/",
    "source": "surface observation",
    "comment": "Any free-format text is appropriate.",
    "acknowledgement": "HYPERNETS project is funded by Horizon 2020 research and innovation program, "
    "Grand Agreement No 775993. Consortium of project  of the Hypernets test sites,"
    " .... are greatly acknowledged.",
    "project_name": "H2020 HYPERNETS GN 775993",
    "language": "English",
    "operational_status": "operational",
    "limitations": "no limitations to public access",
    "licence": "Attribution-NonCommercial-NoDerivs CC BY-NC-ND",
    "conformity": "notEvaluated",
    "lineage": "Quality assured following [reference to doc]",
    "instrument_id": "NaN",
}

QC_METADATA = {
    "IRR_acceleration_x_mean": "NaN",
    "IRR_acceleration_x_std": "NaN",
}

L1A_RAD_METADATA = {
    "title": "HYPSTAR dataset of radiance",  # example of irradiance file
    "instrument_calibration_file_rad": "NaN",
}

L1A_IRR_METADATA = {
    "title": "HYPSTAR dataset of irradiance",  # example of irradiance file
    "instrument_calibration_file_irr": "NaN",
}

L1B_RAD_METADATA = {
    "title": "HYPSTAR dataset of radiance averaged over scans",  # example of irradiance file
    "instrument_calibration_file_rad": "NaN",
}

L1B_IRR_METADATA = {
    "title": "HYPSTAR dataset of irradiance averaged over scans",  # example of irradiance file
    "instrument_calibration_file_irr": "NaN",
}

W_L1C_WLR_METADATA = {
    "title": "HYPSTAR Water network dataset of downwelling irradiance, upwelling and downwelling"
    " radiance and water leaving radiance",  # example of irradiance file
    "instrument_calibration_file_rad": "NaN",
    "instrument_calibration_file_irr": "NaN",
    "rhof_option": "NaN",
    "rhof_wind_source": "NaN",
    "similarity_waveref": "NaN",
    "similarity_wavethres": "NaN",
    "similarity_wavelen1": "NaN",
    "similarity_wavelen2": "NaN",
    "similarity_alpha": "NaN",
}

L_L1C_METADATA = {
    "title": "HYPSTAR Land network dataset of radiance and irradiance",  # example of irradiance file
    "instrument_calibration_file_rad": "NaN",
    "instrument_calibration_file_irr": "NaN",
}

W_L2A_REF_METADATA = {
    "title": "HYPSTAR Water network dataset of spectral surface reflectance",
    "instrument_calibration_file_rad": "NaN",
    "instrument_calibration_file_irr": "NaN",
    "rhof_option": "NaN",
    "similarity_waveref": "NaN",
    "similarity_wavethres": "NaN",
    "similarity_wavelen1": "NaN",
    "similarity_wavelen2": "NaN",
    "similarity_alpha": "NaN",
}

L_L2A_REF_METADATA = {
    "title": "HYPSTAR Land network dataset of spectral surface reflectance",
    "instrument_calibration_file_rad": "NaN",
    "instrument_calibration_file_irr": "NaN",
}

LAND_NETWORK_METADATA = {
    "topic_category": "land, environment, geoscientific information",
    "keyword": "Environmental monitoring Facilities (INSPIRE Spatial Data Theme), "
    "reflectance (http://aims.fao.org/aos/agrovoc/c_28538), optical properties"
    "(http://aims.fao.org/aos/agrovoc/c_5371), vegetation "
    "(http://www.eionet.europa.eu/gemet/concept/8922)",
    "locator": "https://github.com/HYPERNETS/hypernets_processor/",
    "responsible_party": "National Physical Laboratory (NPL), UK",
    "creator_name": "Pieter De Vis",
    "creator_email": "pieter.de.vis@npl.cp.uk",
}

WATER_NETWORK_METADATA = {
    "topic_category": "oceans, environment, inland waters, geoscientific information",
    "keyword": "Environmental monitoring Facilities (INSPIRE Spatial Data Theme), "
    "reflectance (http://aims.fao.org/aos/agrovoc/c_28538), optical properties"
    "(http://aims.fao.org/aos/agrovoc/c_5371),inland waters "
    "(http://www.eionet.europa.eu/gemet/concept/4333), "
    "sea (http://www.eionet.europa.eu/gemet/concept/7495)",
    "locator": "https://github.com/HYPERNETS/hypernets_processor/",
    "responsible_party": "Royal Belgian Institute for Natural Sciences, "
    "Directorate Natural Environment, REMSEM",
    "creator_name": "Clemence Goyens",
    "creator_email": "remsem@naturalsciences.be",
}

NETWORK_METADATA = {
    "spectral_range_vnir": "400-1000",
    "spectral_resolution_vnir": "0.5",
    "spectral_range_vnir_swir": "400-1700",
    "spectral_resolution_swir": "10",
    "solar_azimuth_angle_min": "TBD",
    "solar_zenith_angle_min": "TBD",
    "solar_azimuth_angle_max": "TBD",
    "solar_zenith_angle_max": "TBD",
    # "system_id": system_id,  # key metadata
    "southermost_latitude": "TBD",
    "northernmost_latitude": "TBD",
    "westernmost_longitude": "TBD",
    "easternmost_longitude": "TBD",
    "time_coverage_start": "TBD",
    "time_coverage_end": "TBD",
    "viewing_zenith_angle_average": "TBD",
    "viewing_zenith_angle_min": "TBD",
    "viewing_zenith_angle_max": "TBD",
    "viewing_azimuth_angle_average": "TBD",
    "viewing_azimuth_angle_min": "TBD0",
    "viewing_azimuth_angle_max": "TBD",
    "relative_azimuth_angle_average": "TBD",
    "relative_azimuth_angle_min": "TBD",
    "relative_azimuth_angle_max": "TBD",
}

SYSTEM_METADATA = {  # "system_id": system_id,
    "system_model": "TBD",
    "system_manufacturer": "Laboratoire d'Océanographie de Villefranche UMR 7093 - CNRS / Sorbonne Univ",
    "system_date_manufacture": "TBD",
    "system_version": "TBD",
    "system_firmaware_version": "TBD",
    "system_documentation_references": "TBD",
    "system_deployment_date": "TBD",
    "system_deployment_height": "TBD",
    "system_comment": "system below bird nest, bad luck",
}

INSTRUMENT_METADATA = {
    "instrument_id": "NaN",
    "instrument_manufacturer": "Tartu University",
    "instrument_model": "HYPSTARv1",
    "instrument_date_manufacture": "TBD",
    "instrument_version": "TBD",
    "instrument_firmware": "TBD",
    "instrument_firmware_version": "TBD",
    "instrument_documentation_references": "TBD",
    "instrument_history": "TBD",
    "instrument_deployment_date": "TBD",
}

PAN_TILT_METADATA = {
    "pointing_system_id": "TBD",
    "pointing_system_manufacturer": "Will Burt",
    "pointing_system_model": "Bowler-RX",
    "pointing_system_date_manufacture": "TBD",
    "pointing_system_version": "RX001",
    "pointing_accuracy": "1",
    "pointing_range_azimuth": "0-359",
    "pointing_range_zenith": "2-180",
    "pointing_system_documentation_directory": "https://www.willburt.com/mad/pan-and-tilt-heads/light-"
    "duty",
    "pointing_system_description": "custom azimuth to 359°",
}

CALIBRATION_DEVICE_METADATA = {
    "calibration_device_id": "TBD",
    "calibration_device_manufacturer": "Tartu University",
    "calibration_device_model": "TBD",
    "calibration_device_date_manufacture": "TBD",
    "calibration_device_version": "TBD",
    "Calibration_device_LED_ID": "TBD",
    "Calibration_device_LED_model": "TBD",
    "Calibration_device_LED_manufacturer": "TBD",
    "calibration_device_documentation_directory": "TBD",
    "calibration_device_description": "TBD",
}

IRR_HEAD_METADATA = {
    "irr_vis_head_id": "TBD",
    "irr_vis_head_manufacturer": "TBD",
    "irr_vis_head_model": "TBD",
    "irr_vis_head_manufacture": "TBD",
    "irr_vis_head_version": "TBD",
    "irr_vis_head_firmware_version": "TBD",
    "irr_vis_head_ documentation_reference": "TBD",
    "irr_vis_head_description": "TBD",
}

RAD_HEAD_METADATA = {
    "rad_vis_head_id": "TBD",
    "rad_vis_head_manufacturer": "Ibsen",
    "rad_vis_head_model": "Freedom FSA-101",
    "rad_vis_head_manufacture": "20190120",
    "rad_vis_head_version": "101",
    "rad_vis_head_firmware_version": "v001",
    "rad_vis_head_ documentation_reference": "TBD",
    "rad_vis_head_description": "custom 25 μm slit width for the VNIR spectral region",
    "rad_vis_head_radiometric_resolution": "16",
    "rad_vis_head_spectral_range": "190-1100",
    "rad_vis_head_spectral_sampling": "1.5",
    "rad_vis_head_spectral_resolution": "3",
    "rad_vis_head_spectral_accuracy": "0.3",
    "rad_vis_head_spectral_fov": "7",
    "rad_vis_head_cosine_documentation_reference": "TBD",
    "rad_vis_head_calibration_documentation_reference": "TBD",
    "rad_vis_head_linearity_documentation_reference": "TBD",
}

RAIN_SENSOR_METADATA = {
    "rain_sensor_id": "TBD",
    "rain_sensor_manufacturer": "KemoElectronic",
    "rain_sensor_date_manufacture": "TBD",
}

RGB_CAMERA_METADATA = {
    "rgb_camera_id": "TBD",
    "rgb_camera_manufacturer": "ABUS",
    "rgb_camera_date_manufacture": "TBD",
}

SITE_METADATA = {
    "site_description": "TBD",
    "site_latitude": "NaN",
    "site_longitude": "NaN",
    "site_owner": "TBD",
    "site_operator": "TBD",
    "site_manager": "TBD",
    "site_contact_details": "TBD",
    "site_documentation reference": "TBD",
}

# File format metadata defs
# -------------------------

L_SYSTEM_METADATA = {
    **STANDARD_METADATA,
    **COMPONENTS_METADATA,
    **SYSTEM_METADATA,
    **INSTRUMENT_METADATA,
    **RAD_HEAD_METADATA,
    **IRR_HEAD_METADATA,
    **CALIBRATION_DEVICE_METADATA,
    **RAIN_SENSOR_METADATA,
    **RGB_CAMERA_METADATA,
    **PAN_TILT_METADATA,
    **SITE_METADATA,
    **LAND_NETWORK_METADATA,
    **NETWORK_METADATA,
}
W_SYSTEM_METADATA = {
    **STANDARD_METADATA,
    **COMPONENTS_METADATA,
    **SYSTEM_METADATA,
    **INSTRUMENT_METADATA,
    **RAD_HEAD_METADATA,
    **IRR_HEAD_METADATA,
    **CALIBRATION_DEVICE_METADATA,
    **RAIN_SENSOR_METADATA,
    **RGB_CAMERA_METADATA,
    **PAN_TILT_METADATA,
    **SITE_METADATA,
    **WATER_NETWORK_METADATA,
    **NETWORK_METADATA,
}

METADATA_DEFS = {
    "L0A_RAD": {**STANDARD_METADATA, **COMPONENTS_METADATA},
    "L0A_IRR": {**STANDARD_METADATA, **COMPONENTS_METADATA},
    "L0A_BLA": {**STANDARD_METADATA, **COMPONENTS_METADATA},
    "L0B_RAD": {**STANDARD_METADATA, **COMPONENTS_METADATA},
    "L0B_IRR": {**STANDARD_METADATA, **COMPONENTS_METADATA},
    "CAL": {
        **CAL_METADATA,
        **SYSTEM_METADATA,
        **INSTRUMENT_METADATA,
        **RAD_HEAD_METADATA,
        **IRR_HEAD_METADATA,
        **CALIBRATION_DEVICE_METADATA,
    },
    "L_L1A_RAD": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **LAND_NETWORK_METADATA,
        **L1A_RAD_METADATA,
    },
    "W_L1A_RAD": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **WATER_NETWORK_METADATA,
        **L1A_RAD_METADATA,
    },
    "L_L1A_IRR": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **LAND_NETWORK_METADATA,
        **L1A_IRR_METADATA,
    },
    "W_L1A_IRR": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **WATER_NETWORK_METADATA,
        **L1A_IRR_METADATA,
    },
    "L_L1B_RAD": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **LAND_NETWORK_METADATA,
        **L1B_RAD_METADATA,
    },
    "W_L1B_RAD": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **WATER_NETWORK_METADATA,
        **L1B_RAD_METADATA,
    },
    "L_L1B_IRR": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **LAND_NETWORK_METADATA,
        **L1B_IRR_METADATA,
    },
    "W_L1B_IRR": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **WATER_NETWORK_METADATA,
        **L1B_IRR_METADATA,
    },
    "L_L1C": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **LAND_NETWORK_METADATA,
        **L_L1C_METADATA,
    },
    "W_L1C": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **WATER_NETWORK_METADATA,
        **W_L1C_WLR_METADATA,
    },
    "L_L2A": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **LAND_NETWORK_METADATA,
        **L_L2A_REF_METADATA,
    },
    "W_L2A": {
        **STANDARD_METADATA,
        **COMPONENTS_METADATA,
        **WATER_NETWORK_METADATA,
        **W_L2A_REF_METADATA,
    },
    "L_L2B": {**STANDARD_METADATA, **COMPONENTS_METADATA, **LAND_NETWORK_METADATA, **L_L2A_REF_METADATA},
    "W_L2B": {**STANDARD_METADATA, **COMPONENTS_METADATA, **WATER_NETWORK_METADATA, **W_L2A_REF_METADATA},
}
