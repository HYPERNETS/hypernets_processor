"""
Variable definitions for Hypernets land a water network data products
"""

from copy import deepcopy

import numpy as np

from hypernets_processor.data_io.format.flags import FLAG_MEANINGS

# Sets variables are defined in the below dictionaries. Each entry in a dictionary defines a product variable, the value
# of each entry defines the variable attributes with a dictionary that must contain the following entries:
#
# * "dim" - list of variable dimensions, selected from defined dimension names
# * "dtype" - dtype of data as numpy type
# * "attributes" - dictionary of variable attributes
# * "encoding" - dictionary of variable encoding parameters
#
# Following the variable set definitions a dictionary of is built with an entry for each Hypernets product type, with
# entry of its variables built by combining the variables from the variable sets. This is called VARIABLES_DICT_DEFS
#
# Product variables are defined following the specification defined in:
# Hypernets Team, Product Data Format Specification, v0.5 (2020)


# Dimensions
WL_DIM = "wavelength"
SERIES_DIM = "series"
SCAN_DIM = "scan"
SEQ_DIM = "sequence"

# Contributing variable sets
# --------------------------

# > COMMON_VARIABLES - Variables are required for a data products
COMMON_VARIABLES_SERIES = {"wavelength": {"dim": [WL_DIM],
                                          "dtype": np.float32,
                                          "attributes": {"standard_name": "wavelength",
                                                         "long_name": "Wavelength",
                                                         "units": "nm",
                                                         "preferred_symbol": "wv"},
                                          "encoding": {'dtype': np.uint16, "scale_factor": 1.0, "offset": 0.0}},

                           "bandwidth": {"dim": [WL_DIM],
                                         "dtype": np.float32,
                                         "attributes": {},
                                         "encoding": {'dtype': np.uint16, "scale_factor": 1.0, "offset": 0.0}},

                           "viewing_azimuth_angle": {"dim": [SCAN_DIM],
                                                     "dtype": np.float32,
                                                     "attributes": {"standard_name": "sensor_azimuth_angle",
                                                                    "long_name": "sensor_azimuth_angle is the "
                                                                                 "horizontal angle between the line of "
                                                                                 "sight from the observation point to "
                                                                                 "the sensor and a reference direction "
                                                                                 "at the observation point, which is "
                                                                                 "often due north. The angle is "
                                                                                 "measured clockwise positive, starting"
                                                                                 " from the reference direction. A "
                                                                                 "comment attribute should be added to "
                                                                                 "a data variable with this standard "
                                                                                 "name to specify the reference "
                                                                                 "direction.",
                                                                    "units": "degrees",
                                                                    "reference": "True North",
                                                                    "preferred_symbol": "vaa"},
                                                     "encoding": {'dtype': np.uint16, "scale_factor": 0.1,
                                                                  "offset": 0.0}},

                           "viewing_zenith_angle": {"dim": [SCAN_DIM],
                                                    "dtype": np.float32,
                                                    "attributes": {"standard_name": "sensor_zenith_angle",
                                                                   "long_name": "sensor_zenith_angle is the angle "
                                                                                "between the line of sight to the "
                                                                                "sensor and the local zenith at the "
                                                                                "observation target. This angle is "
                                                                                "measured starting from directly "
                                                                                "overhead and its range is from zero "
                                                                                "(directly overhead the observation "
                                                                                "target) to 180 degrees (directly below"
                                                                                " the observation target). Local zenith"
                                                                                " is a line perpendicular to the "
                                                                                "Earth's surface at a given location. "
                                                                                "'Observation target' means a location"
                                                                                " on the Earth defined by the sensor "
                                                                                "performing the observations.",
                                                                   "units": "degrees",
                                                                   "preferred_symbol": "vza"},
                                                    "encoding": {'dtype': np.uint16, "scale_factor": 0.1,
                                                                 "offset": 0.0}},

                           "solar_azimuth_angle": {"dim": [SCAN_DIM],
                                                   "dtype": np.float32,
                                                   "attributes": {"standard_name": "solar_azimuth_angle",
                                                                  "long_name": "Solar azimuth angle is the horizontal "
                                                                               "angle between the line of sight to the "
                                                                               "sun and a reference direction which "
                                                                               "is often due north. The angle is "
                                                                               "measured clockwise.",
                                                                  "units": "degrees",
                                                                  "reference": "True North",
                                                                  "preferred_symbol": "saa"},
                                                   "encoding": {'dtype': np.uint16, "scale_factor": 0.1,
                                                                "offset": 0.0}},

                           "solar_zenith_angle": {"dim": [SCAN_DIM],
                                                  "dtype": np.float32,
                                                  "attributes": {"standard_name": "solar_zenith_angle",
                                                                 "long_name": "Solar zenith angle is the the angle "
                                                                              "between the line of sight to the sun and"
                                                                              " the local vertical.",
                                                                 "units": "degrees",
                                                                 "preferred_symbol": "sza"},
                                                  "encoding": {'dtype': np.uint16, "scale_factor": 0.1,
                                                               "offset": 0.0}},

                           "quality_flag": {"dim": [SCAN_DIM],
                                            "dtype": "flag",
                                            "attributes": {"standard_name": "quality_flag",
                                                           "long_name": "A variable with the standard name of quality_"
                                                                        "flag contains an indication of assessed "
                                                                        "quality information of another data variable."
                                                                        " The linkage between the data variable and the"
                                                                        " variable or variables with the standard_name"
                                                                        " of quality_flag is achieved using the "
                                                                        "ancillary_variables attribute.",
                                                           "flag_meanings": FLAG_MEANINGS},
                                            "encoding": {}},

                           "acquisition_time": {"dim": [SCAN_DIM],
                                                "dtype": np.uint32,
                                                "attributes": {"standard_name": "time",
                                                               "long_name": "Acquisition time in seconds since "
                                                                            "1970-01-01 "
                                                                            "00:00:00",
                                                               "units": "s"},
                                                "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}}}

COMMON_VARIABLES_SEQ = deepcopy(COMMON_VARIABLES_SERIES)
COMMON_VARIABLES_SCAN = deepcopy(COMMON_VARIABLES_SERIES)

for variable in COMMON_VARIABLES_SEQ.keys():
    COMMON_VARIABLES_SEQ[variable]["dim"] = [d if d != SERIES_DIM else SEQ_DIM
                                             for d in COMMON_VARIABLES_SERIES[variable]["dim"]]
for variable in COMMON_VARIABLES_SCAN.keys():
    COMMON_VARIABLES_SCAN[variable]["dim"] = [d if d != SERIES_DIM else SCAN_DIM
                                              for d in COMMON_VARIABLES_SERIES[variable]["dim"]]

# > L0_VARIABLES - Variables required for the L0 dataset
# SHOULD I ADD MAX NUMBER OF CHARACTERS FOR SERIES ID.... or is acquisition time sufficient - extra check required ????
# "series_id": {"dim": [SCAN_DIM],
#                                   "dtype": np.unicode_,
#                                   "attributes": {"standard_name": "series_id",
#                                                  "long_name": "series identification for the scan",
#                                                  "units": "-"},
#                                   "encoding": {'dtype': np.unicode_}},


L0_RAD_VARIABLES = {"integration_time": {"dim": [SCAN_DIM],
                                         "dtype": np.uint32,
                                         "attributes": {"standard_name": "integration_time",
                                                        "long_name": "Integration time during measurement",
                                                        "units": "s"},
                                         "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "temperature": {"dim": [SCAN_DIM],
                                    "dtype": np.uint32,
                                    "attributes": {"standard_name": "temperature",
                                                   "long_name": "temperature of instrument",
                                                   "units": "degrees"},
                                    "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "acceleration_x_mean": {"dim": [SCAN_DIM],
                                            "dtype": np.uint32,
                                            "attributes": {"standard_name": "acceleration_x_mean",
                                                           "long_name": "Time during measurement",
                                                           "units": "-"},
                                            "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "acceleration_x_std": {"dim": [SCAN_DIM],
                                           "dtype": np.uint32,
                                           "attributes": {"standard_name": "acceleration_x_std",
                                                          "long_name": "",
                                                          "units": "-"},
                                           "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "acceleration_y_mean": {"dim": [SCAN_DIM],
                                            "dtype": np.uint32,
                                            "attributes": {"standard_name": "acceleration_y_mean",
                                                           "long_name": "",
                                                           "units": "-"},
                                            "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "acceleration_y_std": {"dim": [SCAN_DIM],
                                           "dtype": np.uint32,
                                           "attributes": {"standard_name": "acceleration_y_std",
                                                          "long_name": "",
                                                          "units": "-"},
                                           "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "acceleration_z_mean": {"dim": [SCAN_DIM],
                                            "dtype": np.uint32,
                                            "attributes": {"standard_name": "acceleration_z_mean",
                                                           "long_name": "",
                                                           "units": "-"},
                                            "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "acceleration_z_std": {"dim": [SCAN_DIM],
                                           "dtype": np.uint32,
                                           "attributes": {"standard_name": "acceleration_z_std",
                                                          "long_name": "",
                                                          "units": "-"},
                                           "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                    "digital_number": {"dim": [WL_DIM, SCAN_DIM],
                                       "dtype": np.uint32,
                                       "attributes": {"standard_name": "digital_number",
                                                      "long_name": "Digital number, raw data",
                                                      "units": "-"},
                                       "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}}
                    }

L0_IRR_VARIABLES = L0_RAD_VARIABLES
L0_BLA_VARIABLES = L0_RAD_VARIABLES

# > L1A_RAD_VARIABLES - Radiance Variables required for L1 data products (except water L1B)
L1A_RAD_VARIABLES = {"u_random_radiance": {"dim": [WL_DIM, SCAN_DIM],
                                       "dtype": np.uint32,
                                       "attributes": {"standard_name": "random uncertainty on radiance",
                                                      "long_name": "random uncertainty on upwelling radiance",
                                                      "units": "mW m^-2 nm^-1 sr^-1"},
                                       "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                     "u_systematic_radiance": {"dim": [WL_DIM, SCAN_DIM],
                                       "dtype": np.uint32,
                                       "attributes": {"standard_name": "systematic uncertainty on radiance",
                                                      "long_name": "systematic uncertainty on upwelling radiance",
                                                      "units": "mW m^-2 nm^-1 sr^-1"},
                                       "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                     "corr_random_radiance": {"dim": [WL_DIM, WL_DIM],
                                       "dtype": np.uint32,
                                       "attributes": {"standard_name": "correlation matrix of random error on radiance",
                                                      "long_name": "covariance between wavelengths for the random errors on radiance",
                                                      "units": "mW m^-2 nm^-1 sr^-1"},
                                       "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                     "corr_systematic_radiance": {"dim": [WL_DIM, WL_DIM],
                                       "dtype": np.uint32,
                                       "attributes": {"standard_name": "correlation matrix of systematic error on radiance",
                                                      "long_name": "covariance bewtween wavelengths for systematic error on radiance",
                                                      "units": "mW m^-2 nm^-1 sr^-1"},
                                       "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}},
                     "radiance": {"dim": [WL_DIM, SCAN_DIM],
                                       "dtype": np.uint32,
                                       "attributes": {"standard_name": "radiance",
                                                      "long_name": "upwelling radiance",
                                                      "units": "mW m^-2 nm^-1 sr^-1"},
                                       "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}}}

# > L1A_IRR_VARIABLES - Irradiance Variables required for L1 data products (except water L1B)
L1A_IRR_VARIABLES = {"u_random_irradiance": {},
                     "u_systematic_irradiance": {},
                     "cov_random_irradiance": {},
                     "cov_systematic_irradiance": {},
                     "irradiance": {}}

# > L1B_WATER_VARIABLES - Variables required for the water network L1b data product
L1B_WATER_VARIABLES = {"upwelling_radiance": {"dim": [WL_DIM, SEQ_DIM],
                                              "dtype": np.float32,
                                              "attributes": {"standard_name": "upwelling_radiance_per_unit_wavelength"
                                                                              "_in_air",
                                                             "long_name": "Upwelling radiation is radiation from "
                                                                          "below. It does not mean net upward. "
                                                                          "The sign convention is that upwelling "
                                                                          "is positive upwards and 'downwelling' "
                                                                          "is positive downwards. Radiance is the "
                                                                          "radiative flux in a particular direction, "
                                                                          "per unit of solid angle. The direction "
                                                                          "towards which it is going must be "
                                                                          "specified, for instance with a coordinate "
                                                                          "of zenith_angle.",
                                                             "reference": "",
                                                             "units": "mW m^-2 nm^-1 sr^-1",
                                                             "NRC URI": "http://vocab.nerc.ac.uk/collection/P01/"
                                                                        "current/TTWTIR01/",
                                                             "preferred_symbol": "lu"},
                                              "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "downwelling_radiance": {"dim": [WL_DIM, SEQ_DIM],
                                                "dtype": np.float32,
                                                "attributes": {"standard_name": "downwelling_radiance_per_unit_"
                                                                                "wavelength_in_air",
                                                               "long_name": "Downwelling radiation is radiation from "
                                                                            "above. It does not mean 'net downward'. "
                                                                            "The sign convention is that 'upwelling' is"
                                                                            " positive upwards and 'downwelling' is "
                                                                            "positive downwards. A coordinate variable "
                                                                            "for radiation wavelength should be given "
                                                                            "the standard name radiation_wavelength. "
                                                                            "Radiance is the radiative flux in a "
                                                                            "particular direction, per unit of solid "
                                                                            "angle. The direction from which it is "
                                                                            "coming must be specified, for instance "
                                                                            "with a coordinate of zenith_angle.",
                                                               "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                                               "units": "mW m^-2 nm^-1 sr^-1",
                                                               "NRC URI": "http://vocab.nerc.ac.uk/collection/"
                                                                          "P01/current/SKYIRR01/",
                                                               "preferred_symbol": "ld"},
                                                "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "downwelling_irradiance": {"dim": [WL_DIM, SEQ_DIM],
                                                  "dtype": np.float32,
                                                  "attributes": {"standard_name": "downwelling_irradiance_per_unit_"
                                                                                  "wavelength_in_air",
                                                                 "long_name": "Downwelling vector irradiance as energy"
                                                                              " of electromagnetic radiation "
                                                                              "(unspecified single wavelength) "
                                                                              "in the atmosphere by cosine-collector "
                                                                              "radiometer",
                                                                 "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                                                 "units": "mW m^-2 nm^-1",
                                                                 "NRC URI": "http://vocab.nerc.ac.uk/collection/"
                                                                            "P01/current/CSLRCCR1/",
                                                                 "preferred_symbol": "ed"},
                                                  "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "surface_reflectance": {"dim": [WL_DIM, SEQ_DIM],
                                               "dtype": np.float32,
                                               "attributes": {"standard_name": "surface_upwelling_radiance_per_unit_"
                                                                               "wavelength_in_air_reflected_by_water",
                                                              "long_name": "The surface called 'surface' means the "
                                                                           "lower boundary of the atmosphere. "
                                                                           "Upwelling radiation is radiation from "
                                                                           "below. It does not mean 'net upward''. "
                                                                           "The sign convention is that 'upwelling' "
                                                                           "is positive upwards and 'downwelling' "
                                                                           "is positive downwards. Radiance is the "
                                                                           "radiative flux in a particular "
                                                                           "direction, per unit of solid angle. The "
                                                                           "direction towards which it is going must be"
                                                                           " specified, for instance with a coordinate "
                                                                           "of zenith_angle. ",
                                                              "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                                              "units": "-",
                                                              "preferred_symbol": "ls"},
                                               "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "rhof": {"dim": [WL_DIM, SEQ_DIM],
                                "dtype": np.float32,
                                "attributes": {"standard_name": "fresnel_reflectance",
                                               "long_name": "Fraction of downwelling sky radiance reflected at the "
                                                            "air-water interface",
                                               "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                               "units": "-",
                                               "preferred_symbol": "rhof"},
                                "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "fresnel_wind": {"dim": [SEQ_DIM],
                                        "dtype": np.float32,
                                        "attributes": {"standard_name": "fresnel_wind",
                                                       "long_name": "Surface wind speed used for the retrieval of the "
                                                                    "fraction of downwelling sky radiance reflected at "
                                                                    "the air-water interface",
                                                       "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                                       "units": "ms^-1"},
                                        "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "fresnel_sza": {"dim": [SEQ_DIM],
                                       "dtype": np.float32,
                                       "attributes": {"standard_name": "fresnel_solar_zenith_angle",
                                                      "long_name": "Solar zenith angle used for the retrieval of the "
                                                                   "fraction of downwelling sky radiance reflected at "
                                                                   "the air-water interface",
                                                      "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                                      "units": "degrees"},
                                       "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "fresnel_raa": {"dim": [SEQ_DIM],
                                       "dtype": np.float32,
                                       "attributes": {"standard_name": "fresnel_relative_azimuth_angle",
                                                      "long_name": "Relative azimuth angle from sun to sensor (0° when "
                                                                   "sun and sensor are aligned 180° when the sensor is "
                                                                   "looking into the sunglint) used for the retrieval "
                                                                   "of the fraction of downwelling sky radiance "
                                                                   "reflected at the air-water interface",
                                                      "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
                                                      "units": "degrees"},
                                       "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "fresnel_vza": {"dim": [SEQ_DIM],
                                       "dtype": np.float32,
                                       "attributes": {"standard_name": "fresnel_sensor_zenith_angle",
                                                      "long_name": "Sensor zenith angle used for the retrieval of the "
                                                                   "fraction of downwelling sky radiance reflected at "
                                                                   "the air-water interface",
                                                      "reference": "",
                                                      "units": "degrees"},
                                       "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}}

                       }

# L_L2A_REFLECTANCE_VARIABLES - Reflectance variables required for L2A land data product
L_L2A_REFLECTANCE_VARIABLES = {}

# W_L2A_REFLECTANCE_VARIABLES - Reflectance variables required for L2A water data product
W_L2A_REFLECTANCE_VARIABLES = {"normalized_water_leaving_radiance": {"dim": [WL_DIM, SEQ_DIM],
                                                                     "dtype": np.float32,
                                                                     "attributes": {
                                                                         "standard_name":
                                                                             "normalized_water_leaving_radiance",
                                                                         "long_name": "Normalised water-leaving radiance"
                                                                                      " of electromagnetic radiation "
                                                                                      "(unspecified single wavelength)"
                                                                                      " from the water body by "
                                                                                      "cosine-collector radiometer",
                                                                         "reference": "",
                                                                         "units": "mW m^-2 nm^-1 sr^-1",
                                                                         "preferred_symbol": "nlw"},
                                                                     "encoding": {'dtype': np.uint16,
                                                                                  "scale_factor": 0.1, "offset": 0.0}},
                               "reflectance": {"dim": [WL_DIM, SEQ_DIM],
                                               "dtype": np.float32,
                                               "attributes": {"standard_name": "water_leaving_reflectance",
                                                              "long_name": "Reflectance of the water column at the "
                                                                           "surface corrected for the NIR Similarity "
                                                                           "spectrum (Ruddick et al., 2006)",
                                                              "units": "-",
                                                              "preferred_symbol": "rhow"},
                                               "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                               "reflectance_nosc": {"dim": [WL_DIM, SEQ_DIM],
                                                    "dtype": np.float32,
                                                    "attributes": {"standard_name": "water_leaving_reflectance_nosc",
                                                                   "long_name": "Reflectance of the water column at the "
                                                                                "surface without correction for the NIR "
                                                                                "similarity spectrum "
                                                                                "(see Ruddick et al., 2006)",
                                                                   "units": "-",
                                                                   "preferred_symbol": "rhow_nosc"},
                                                    "encoding": {'dtype': np.uint16, "scale_factor": 0.1,
                                                                 "offset": 0.0}},
                               "u_random_nlw": {"dim": [WL_DIM, SEQ_DIM],
                                                "dtype": np.float32,
                                                "attributes": {
                                                    "standard_name": "u_random_normalized_water_leaving_radiance",
                                                    "long_name": "Random normalized water leaving radiance "
                                                                 "uncertainty",
                                                    "units": "%"},
                                                "encoding": {'dtype': np.uint16, "scale_factor": 0.01, "offset": 0.0}},
                               "u_systematic_nlw": {"dim": [WL_DIM, SEQ_DIM],
                                                    "dtype": np.float32,
                                                    "attributes": {
                                                        "standard_name": "u_systematic_normalized_water_leaving_radiance",
                                                        "long_name": "Systematic normalized water leaving radiance "
                                                                     "uncertainty",
                                                        "units": "%"},
                                                    "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                 "offset": 0.0}},
                               "cov_random_nlw": {"dim": [WL_DIM, SEQ_DIM],
                                                  "dtype": np.float32,
                                                  "attributes": {
                                                      "standard_name": "cov_random_normalized_water_leaving_radiance",
                                                      "long_name": "Covariance matrix of random normalized water "
                                                                   "leaving radiance uncertainty",
                                                      "units": "-"},
                                                  "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                               "offset": 0.0}},
                               "cov_systematic_nlw": {"dim": [WL_DIM, SEQ_DIM],
                                                      "dtype": np.float32,
                                                      "attributes": {
                                                          "standard_name":
                                                              "cov_systematic_normalized_water_leaving_radiance",
                                                          "long_name":
                                                              "Covariance matrix of systematic normalized water "
                                                              "leaving radiance uncertainty",
                                                          "units": "-"},
                                                      "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                   "offset": 0.0}},
                               "u_random_rhow": {"dim": [WL_DIM, SEQ_DIM],
                                                 "dtype": np.float32,
                                                 "attributes": {"standard_name": "u_random_water_leaving_reflectance",
                                                                "long_name": "Random water leaving reflectance "
                                                                             "uncertainty",
                                                                "units": "%"},
                                                 "encoding": {'dtype': np.uint16, "scale_factor": 0.01, "offset": 0.0}},
                               "u_systematic_rhow": {"dim": [WL_DIM, SEQ_DIM],
                                                     "dtype": np.float32,
                                                     "attributes": {
                                                         "standard_name": "u_systematic_water_leaving_reflectance",
                                                         "long_name": "Systematic water leaving reflectance uncertainty",
                                                         "units": "%"},
                                                     "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                  "offset": 0.0}},
                               "cov_random_rhow": {"dim": [WL_DIM, SEQ_DIM],
                                                   "dtype": np.float32,
                                                   "attributes": {
                                                       "standard_name": "cov_random_water_leaving_reflectance",
                                                       "long_name": "Covariance matrix of random water leaving "
                                                                    "reflectance uncertainty",
                                                       "units": "-"},
                                                   "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                "offset": 0.0}},
                               "cov_systematic_rhow": {"dim": [WL_DIM, SEQ_DIM],
                                                       "dtype": np.float32,
                                                       "attributes": {
                                                           "standard_name": "cov_systematic_water_leaving_reflectance",
                                                           "long_name": "Covariance matrix of systematic water leaving "
                                                                        "reflectance uncertainty",
                                                           "units": "-"},
                                                       "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                    "offset": 0.0}},
                               "u_random_rhow_nosc": {"dim": [WL_DIM, SEQ_DIM],
                                                      "dtype": np.float32,
                                                      "attributes": {
                                                          "standard_name": "u_random_water_leaving_reflectance_nosc",
                                                          "long_name": "Random water leaving reflectance not corrected "
                                                                       "for NIR similarity spectrum uncertainty",
                                                          "units": "%"},
                                                      "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                   "offset": 0.0}},
                               "u_systematic_rhow_nosc": {"dim": [WL_DIM, SEQ_DIM],
                                                          "dtype": np.float32,
                                                          "attributes": {
                                                              "standard_name":
                                                                  "u_systematic_water_leaving_reflectance_nosc",
                                                              "long_name": "Systematic water leaving reflectance not "
                                                                           "corrected for NIR similarity spectrum "
                                                                           "uncertainty",
                                                              "units": "%"},
                                                          "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                       "offset": 0.0}},
                               "cov_random_rhow_nosc": {"dim": [WL_DIM, SEQ_DIM],
                                                        "dtype": np.float32,
                                                        "attributes": {
                                                            "standard_name": "cov_random_water_leaving_reflectance_nosc",
                                                            "long_name": "Covariance matrix of random water leaving "
                                                                         "reflectance not corrected for NIR similarity "
                                                                         "spectrum uncertainty",
                                                            "units": "-"},
                                                        "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                     "offset": 0.0}},
                               "cov_systematic_rhow_nosc": {"dim": [WL_DIM, SEQ_DIM],
                                                            "dtype": np.float32,
                                                            "attributes": {
                                                                "standard_name":
                                                                    "cov_systematic_water_leaving_reflectance_nosc",
                                                                "long_name": "Covariance matrix of systematic water "
                                                                             "leaving reflectance not corrected for NIR "
                                                                             "similarity spectrum uncertainty",
                                                                "units": "-"},
                                                            "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                         "offset": 0.0}}
                               }

# L_L2B_REFLECTANCE_VARIABLES - Reflectance variables required for L2A land data product
L_L2B_REFLECTANCE_VARIABLES = {"u_random_reflectance": {"dim": [WL_DIM, SERIES_DIM],
                                                        "dtype": np.float32,
                                                        "attributes": {"standard_name": "u_random_reflectance",
                                                                       "long_name": "Random reflectance uncertainty",
                                                                       "units": "%"},
                                                        "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                     "offset": 0.0}},
                               "u_systematic_reflectance": {"dim": [WL_DIM, SERIES_DIM],
                                                            "dtype": np.float32,
                                                            "attributes": {"standard_name": "u_systematic_reflectance",
                                                                           "long_name": "Systematic reflectance "
                                                                                        "uncertainty",
                                                                           "units": "%"},
                                                            "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                         "offset": 0.0}},
                               "cov_random_reflectance": {"dim": [WL_DIM, SERIES_DIM],
                                                          "dtype": np.float32,
                                                          "attributes": {"standard_name": "cov_random_reflectance",
                                                                         "long_name": "Covariance matrix of random "
                                                                                      "reflectance "
                                                                                      "uncertainty",
                                                                         "units": "-"},
                                                          "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                       "offset": 0.0}},
                               "cov_systematic_reflectance": {"dim": [WL_DIM, SERIES_DIM],
                                                              "dtype": np.float32,
                                                              "attributes": {
                                                                  "standard_name": "cov_systematic_reflectance",
                                                                  "long_name": "Covariance matrix of systematic "
                                                                               "reflectance "
                                                                               "uncertainty",
                                                                  "units": "-"},
                                                              "encoding": {'dtype': np.uint16, "scale_factor": 0.01,
                                                                           "offset": 0.0}},
                               "reflectance": {"dim": [WL_DIM, SERIES_DIM],
                                               "dtype": np.float32,
                                               "attributes": {"standard_name": "reflectance",
                                                              "long_name": "The surface called surface means the lower "
                                                                           "boundary of the atmosphere. "
                                                                           "Bidirectional_reflectance depends on"
                                                                           "the angles of incident and measured"
                                                                           "radiation.Reflectance is the ratio of the "
                                                                           "energy of the reflected to the incident "
                                                                           "radiation. A coordinate variable of "
                                                                           "radiation_wavelength or radiation_frequency "
                                                                           "can be used to specify the wavelength or "
                                                                           "frequency, respectively, of the radiation.",
                                                              "units": "-"},
                                               "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}}}

# W_L2B_REFLECTANCE_VARIABLES - Reflectance variables required for L2A land data product
W_L2B_REFLECTANCE_VARIABLES = {}

# File format variable defs
# -------------------------

VARIABLES_DICT_DEFS = {"L0_RAD": {**COMMON_VARIABLES_SCAN, **L0_RAD_VARIABLES},
                       "L0_IRR": {**COMMON_VARIABLES_SCAN, **L0_IRR_VARIABLES},
                       "L_L1A_RAD": {**COMMON_VARIABLES_SERIES, **L1A_RAD_VARIABLES},
                       "W_L1A_RAD": {**COMMON_VARIABLES_SERIES, **L1A_RAD_VARIABLES},
                       "L_L1A_IRR": {**COMMON_VARIABLES_SERIES, **L1A_IRR_VARIABLES},
                       "W_L1A_IRR": {**COMMON_VARIABLES_SERIES, **L1A_IRR_VARIABLES},
                       "L_L1B": {**COMMON_VARIABLES_SERIES, **L1A_RAD_VARIABLES, **L1A_IRR_VARIABLES},
                       "W_L1B": {**COMMON_VARIABLES_SEQ, **L1B_WATER_VARIABLES},
                       "L_L2A": {**COMMON_VARIABLES_SERIES, **L_L2A_REFLECTANCE_VARIABLES},
                       "W_L2A": {**COMMON_VARIABLES_SEQ, **W_L2A_REFLECTANCE_VARIABLES},
                       "L_L2B": {**COMMON_VARIABLES_SERIES, **L_L2B_REFLECTANCE_VARIABLES},
                       "W_L2B": {**COMMON_VARIABLES_SEQ, **W_L2B_REFLECTANCE_VARIABLES}
                       }
