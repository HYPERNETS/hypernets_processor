"""
Standard metadata for Hypernets L1, L2a and L2b files, for the land a water network
20200420 CG : Updated metadata according to Hyperents_Data_format_v0.5.docx" 
"""

COMMON_METADATA={"type":"dataset",
                 "abstract":: "The HYPERNETS project (Horizon 2020 research and innovation, grant agreement "
                                        "No 775983) has the overall aim to provide high quality in situ measurements to"
                                        "support the (visible/SWIR) optical Copernicus products. Therefore a new "
                                        "multi-head hyperspectral spectroradiometer dedicated to land and water surface"
                                        " reflectance validation with instrument pointing capabilities and embedded "
                                        "calibration device has been established. The instrument has been deployed at "
                                        "24 sites covering a range of water and land types and a range of climatic and"
                                        "logistic conditions (www.hypernets.eu).",
		 "conventions":"CFv72, NVS2.0",
		 "format_version":"v01.0",
		 "netcdf_version":"1.6",
                 "data_created": "29302838",  # adds on write
		 "references":"https://hypernets-processor.readthedocs.io/en/latest/",
		 "source":"surface observation",
		 "comment":"Any free-format text is appropriate.",
		 "locator":"www.hypernets.eu, www.waterhypernet.org",
		 "area":"Global",
		 "easting":"longitude",
		 "northing":"latitude",
		 "southermost_latitude	:"-90.00",
		 "northernmost_latitude	:"90.00",
		 "westernmost_longitude	:"-180.00",
		 "easternmost_longitude	:"180.00",
		 "time_coverage_start":"2020-04-01T00:02:00Z",
		 "time_coverage_end":"2020-04-01T00:02:00Z",
		 "acknowledgement":"HYPERNETS project is funded by Horizon 2020 research and innovation program, "
					"Grand Agreement No 775993. Consortium of project  of the Hypernets test sites, .... are greatly acknowledged.",
		 "project_name":"H2020 HYPERNETS GN 775993",
		 "language":"English",
		 "operational_status":"operational",
		 "limitations":"no limitations to public access",
		 "licence":"Attribution-NonCommercial-NoDerivs CC BY-NC-ND",
		 "conformity":"notEvaluated",
		 "lineage":"Quality assured following www.hypernets.eu/docs/QC/"
}
LAND_NETWORK_METADATA = {"responsible_party": "National Physical Laboratory, UK",
                         "creator_name": "Hunt Sam",
                         "creator_email": "sam.hunt@npl.co.uk",
                         "topic_category": "land, environment, geoscientific information"
			 "keyword":"Environmental monitoring Facilities (INSPIRE Spatial Data Theme)," 
			 "reflectance (http://aims.fao.org/aos/agrovoc/c_28538), optical properties"
			 "(http://aims.fao.org/aos/agrovoc/c_5371), vegetation (http://www.eionet.europa.eu/gemet/concept/8922)"
}

WATER_NETWORK_METADATA = {"responsible_party": "Royal Belgian Institute for Natural Sciences, "
                                               "Directorate Natural Environment, REMSEM",
                          "creator_name": "Goyens Clémence",
                          "creator_email": "cgoyens@naturalsciences.be",
                          "topic_category": "oceans, environment, inland waters, geoscientific information"
			  "keyword":"Environmental monitoring Facilities (INSPIRE Spatial Data Theme)," 
			  "reflectance (http://aims.fao.org/aos/agrovoc/c_28538), optical properties"
			  "(http://aims.fao.org/aos/agrovoc/c_5371),inland waters (http://www.eionet.europa.eu/gemet/concept/4333),"
			  "sea (http://www.eionet.europa.eu/gemet/concept/7495)"
}



INSTRUMENT_METADATA={"instrument_id":"HYDERv01001234",
			"instrument_manufacturer":"Tartu University",
			"instrument_model":"HYDER",
			"instrument_date_manufacture":"2020-04-01",
			"instrument_version":"v001",
			"instrument_firmware":"Firmware4",
			"instrument_firmware_version":"v001",
			"instrument_documentation_references":"www.hypernets/firmware4/",
			"instrument_history":"2020-04-01T00:02:00Z :Creation,2028-03-23T11:56:12Z :Radiance head replaced",
			"instrument_deployment_date":"2020-04-25",
			"system_id":"HYPSTAR001234" # key metadata
}
SYSTEM_METADATA={"system_id":"HYPSTAR001234",
		"system_model":"HYPSTARv01.0",
		"system_manufacturer":"Laboratoire d'Océanographie de Villefranche UMR 7093 - CNRS / Sorbonne Univ",
		"system_date_manufacture":"2028-03-01",
		"system_version":"v0.1",
		"system_firmaware_version":"v01",
		"system_logfile":"www.waterhypernet/01_GBNA/logfile.txt",
		"system_documentation_references":"www.hypernets.eu/system_documentation",
		"system_deployment_date":"2028-03-23",
		"system_calibration_file":"HYPSTAR_L_BSBE_CDB_202001041130.nc",
		"instrument_id":"001", # key metadata
		"pointing_system_id":"MAD01234", # key metadata
		"calibration_device_id":"CALspars01234", # key metadata
		"irr_vis_head_id":"IBSENUVNIR001", # key metadata
		"rad_vis_head_id":"IBSENUVNIR001", # key metadata
		"rain_sensor_id":"rainsensorID01234", # key metadata 
		"rgb_camera_id":"cameraID01234", # key metadata
		"site_id":"BSBE" # key metadata
}


PAN_TILT_METADATA={"pointing_system_id":"MAD01234",
			"pointing_system_manufacturer":"Will Burt",
			"pointing_system_model":"Bowler-RX",
			"pointing_system_date_manufacture":"20180101",
			"pointing_system_version":"RX001",
			"pointing_system_documentation_directory":"https://www.willburt.com/mad/pan-and-tilt-heads/light-duty",
			"pointing_system_description":"pan and tilt with custom azimuth to 359°"
}

CALIBRATION_DEVICE_METADATA={"calibration_device_id":"CALspars01234",
				"calibration_device_manufacturer":"Tartu University",
				"calibration_device_model":"Calspars01",
				"calibration_device_date_manufacture":"20200101",
				"calibration_device_version":"v01",
				"Calibration_device_LED_ID":"LOLTW01234",
				"Calibration_device_LED_model":"LTW-2S3D7",
				"Calibration_device_LED_manufacturer":"Lite-On",
				"calibration_device_documentation_directory":"https://www.hypernets/eu/Calspars_CalibrationDevice",
				"calibration_device_description":"Nothing to add"
}

IRR_HEAD_METADATA={"irr_vis_head_id":"SJ1002SMA001234",
			"irr_vis_head_manufacturer":"CMS Schreder",
			"irr_vis_head_model":"J1002-SMA",
			"irr_vis_head_manufacture":"20190120",
			"irr_vis_head_version":"1002",
			"irr_vis_head_firmware_version":"v001",
			"irr_vis_head_ documentation_reference":"https://hypernets.to.ee/documentation",
			"irr_vis_head_description":"or will we have an in-house designed irradiance head",
			"irr_vis_head_cosine_documentation_reference":"www.waterhypernet.org/calibration/SJ1002SMA001234"
}

RAD_HEAD_METADATA={"rad_vis_head_id":"IBSENUVNIR001",
			"rad_vis_head_manufacturer":"Ibsen",
			"rad_vis_head_model":"Freedom FSA-101",
			"rad_vis_head_manufacture":"20190120",
			"rad_vis_head_version":"101",
			"rad_vis_head_firmware_version":"v001",
			"rad_vis_head_ documentation_reference":"https://hypernets.to.ee/documentation",
			"rad_vis_head_description":"custom 25 μm slit width for the VNIR spectral region",
			"rad_vis_head_radiometric_resolution":"16",
			"rad_vis_head_spectral_range":"190-1100",
			"rad_vis_head_spectral_sampling":"1.5",
			"rad_vis_head_spectral_resolution":"3",
			"rad_vis_head_spectral_accuracy":"0.3",
			"rad_vis_head_spectral_fov":"7",
			"rad_vis_head_cosine_documentation_reference":"www.waterhypernet.org/calibration/IBSENUVNIR001/cosine",
			"rad_vis_head_calibration_documentation_reference":"www.waterhypernet.org/calibration/IBSENUVNIR001/spectralResp",
			"rad_vis_head_linearity_documentation_reference":"www.waterhypernet.org/calibration/IBSENUVNIR001/lin"
}

RAIN_SENSOR_METADATA={"rain_sensor_id":"rainsensorID01234",
			"rain_sensor_manufacturer":"KemoElectronic",
			"rain_sensor_date_manufacture":"20191102"}

RGB_CAMERA_METADATA={"rgb_camera_id":"cameraID01234",
		 "rgb_camera_manufacturer":"ABUS",
		 "rgb_camera_date_manufacture":"20191102"}

SITE_METADATA={"site_id":"BSBE",
		"site_description":"De Blankaart, Belgium Viewing direction, southern side of the reservoir",
		"site_latitude":"50.836404",
		"site_longitude":"4.375634",
		"site_owner":"De Watergoep",
		"site_operator":"RBINS",
		"site_manager":"De Watergroep",
		"site_contact_details":"Clémence Goyens, cgoyens@naturalsciences.be",
		"site_documentation reference":"www.waterhypernet.org/sites/deBlankaart/South",
		"system_id":"HYPSTAR001234" # key metadata
}

L1_METADATA = {"title": "HYPERNETS network dataset of downwelling irradiance",
  		"product_name":"HYPSTAR_W_BSBE_RAD_202002041130_v01.0.nc",
		"product_version":"HYPSTAR_W_BSBE_RAD_202002041130_v01.0.nc",
		"processor_name":"hypernets_processor",
		"processor_version":"v001",
		"processor_configuration_file":"https://github.com/HYPERNETS/hypernets_processor/tree/master/examples/config_files/config.txt",
		"processor_atbd":"https://github.com/HYPERNETS/hypernets_processor/atbd/L1",
		"history":"2020-04-01T00:02:00Z :Creation, 2028-03-23T11:56:12Z :Reviewed calibration",
		"sequence_id":"SEQ20200312T135926",
		"series_id":"01_002_-030_2_057_8_01_0000",
		"system_id":"HYPSTAR001234",
		"sequence_config_file":"https://github.com/HYPERNETS/hypernets_processor/blob/metareader/hypernets_processor/data_io/tests/reader/SEQ20200312T135926/config.txt",
		"sequence_file":"https://github.com/HYPERNETS/hypernets_processor/blob/metareader/hypernets_processor/data_io/tests/reader/SEQ20200312T135926/test_STD.csv",
		"inputfile":"https://github.com/HYPERNETS/hypernets_processor/blob/metareader/hypernets_processor/data_io/tests/reader/SEQ20200312T135926/RADIOMETER/01_002_-030_2_180_8_01_0000.spe",
		"scans_total":"1",
		"units":"Wm-2m-1",
		"vza_average":"180.000",
		"saa_average":"190.123",
		"raa_average":"330.000",
		"sza_average":"52.000",
		"vza_min":"180.000",
		"saa_min":"190.123",
		"raa_min":"330.000",
		"sza_min":"52.000",
		"vza_max":"180.000"
		"saa_max":"190.123",
		"raa_max":"330.000",
		"sza_max":"52.000"
}

L2_METADATA = {"title": "HYPERNETS network dataset of spectral surface reflectance"}

L2_L_METADATA = {"resource_title": "HYPERNETS network dataset of spectral surface reflectance"}

L2_W_METADATA = {"resource_title": "HYPERNETS network dataset of spectral surface reflectance"}




