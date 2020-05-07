"""
Variable definitions for Hypernets land a water network data products
"""

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
SEQ_DIM = "sequence"

# Contributing variable sets
# --------------------------

# > COMMON_VARIABLES - Variables are required for a data products
COMMON_VARIABLES = {"wavelength": {"dim": [WL_DIM],
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

                    "viewing_azimuth_angle": {"dim": [SERIES_DIM],
                                              "dtype": np.float32,
                                              "attributes": {"standard_name": "sensor_azimuth_angle",
                                                             "long_name": "sensor_azimuth_angle is the horizontal angle"
                                                                          " between the line of sight from the "
                                                                          "observation point to the sensor and a "
                                                                          "reference direction at the observation "
                                                                          "point, which is often due north. The angle "
                                                                          "is measured clockwise positive, starting "
                                                                          "from the reference direction. A comment "
                                                                          "attribute should be added to a data variable"
                                                                          " with this standard name to specify the "
                                                                          "reference direction.",
                                                             "units": "degrees",
                                                             "reference": "True North",
                                                             "preferred_symbol": "vaa"},
                                              "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},

                    "viewing_zenith_angle": {"dim": [SERIES_DIM],
                                             "dtype": np.float32,
                                             "attributes": {"standard_name": "sensor_zenith_angle",
                                                            "long_name": "sensor_zenith_angle is the angle between the "
                                                                         "line of sight to the sensor and the local "
                                                                         "zenith at the observation target. This angle "
                                                                         "is measured starting from directly overhead "
                                                                         "and its range is from zero (directly overhead"
                                                                         " the observation target) to 180 degrees "
                                                                         "(directly below the observation target). "
                                                                         "Local zenith is a line perpendicular to the "
                                                                         "Earth's surface at a given location. "
                                                                         "'Observation target' means a location on the "
                                                                         "Earth defined by the sensor performing the "
                                                                         "observations.",
                                                            "units": "degrees",
                                                            "preferred_symbol": "vza"},
                                             "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},

                    "solar_azimuth_angle": {"dim": [SERIES_DIM],
                                            "dtype": np.float32,
                                            "attributes": {"standard_name": "solar_azimuth_angle",
                                                           "long_name": "Solar azimuth angle is the horizontal angle "
                                                                        "between the line of sight to the sun and a "
                                                                        "reference direction which is often due north."
                                                                        " The angle is measured clockwise.",
                                                           "units": "degrees",
                                                           "reference": "True North",
                                                           "preferred_symbol": "saa"},
                                            "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},

                    "solar_zenith_angle": {"dim": [SERIES_DIM],
                                           "dtype": np.float32,
                                           "attributes": {"standard_name": "solar_zenith_angle",
                                                          "long_name": "Solar zenith angle is the the angle between "
                                                                       "the line of sight to the sun and the local "
                                                                       "vertical.",
                                                          "units": "degrees",
                                                          "preferred_symbol": "sza"},
                                           "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},

                    "quality_flag": {"dim": [SERIES_DIM],
                                     "dtype": "flag",
                                     "attributes": {"standard_name": "quality_flag",
                                                    "long_name": "A variable with the standard name of quality_flag "
                                                                 "contains an indication of assessed quality "
                                                                 "information of another data variable. The linkage "
                                                                 "between the data variable and the variable or "
                                                                 "variables with the standard_name of quality_flag is "
                                                                 "achieved using the ancillary_variables attribute.",
                                                    "flag_meanings": FLAG_MEANINGS},
                                     "encoding": {}},

                    "acquisition_time": {"dim": [SERIES_DIM],
                                         "dtype": np.int32,
                                         "attributes": {"standard_name": "time",
                                                        "long_name": "Acquisition time in seconds since 1970-01-01 "
                                                                     "00:00:00",
                                                        "units": "s"},
                                         "encoding": {'dtype': np.uint32, "scale_factor": 1, "offset": 0.0}}}

# > L0_VARIABLES - Variables required for the L0 dataset
L0_VARIABLES = {}

# > L1A_RAD_VARIABLES - Radiance Variables required for L1 data products (except water L1B)
L1A_RAD_VARIABLES = {"u_random_radiance": {},
                     "u_systematic_radiance": {},
                     "cov_random_radiance": {},
                     "cov_systematic_radiance": {},
                     "radiance": {}}

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
                                                             "NRC URI":"http://vocab.nerc.ac.uk/collection/P01/"
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
                                                               "NRC URI":"http://vocab.nerc.ac.uk/collection/"
                                                                         "P01/current/SKYIRR01/",
                                                               "preferred_symbol": "ld"},
                                                "encoding": {'dtype': np.uint16, "scale_factor": 0.1, "offset": 0.0}},
                       "downwelling_irradiance": {"dim": [WL_DIM, SEQ_DIM],
                                                  "dtype": np.float32,
                                                  "attributes": {"standard_name":"downwelling_irradiance_per_unit_"
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
W_L2A_REFLECTANCE_VARIABLES = {}

# L_L2B_REFLECTANCE_VARIABLES - Reflectance variables required for L2A land data product
L_L2B_REFLECTANCE_VARIABLES = {}

# W_L2B_REFLECTANCE_VARIABLES - Reflectance variables required for L2A land data product
W_L2B_REFLECTANCE_VARIABLES = {}


# File format variable defs
# -------------------------

VARIABLES_DICT_DEFS = {"L0": {**COMMON_VARIABLES, **L0_VARIABLES},
                       "L1A_RAD": {**COMMON_VARIABLES, **L1A_RAD_VARIABLES},
                       "L1A_IRR": {**COMMON_VARIABLES, **L1A_IRR_VARIABLES},
                       "L_L1B": {**COMMON_VARIABLES, **L1A_RAD_VARIABLES, **L1A_IRR_VARIABLES},
                       "W_L1B": {**COMMON_VARIABLES, **L1B_WATER_VARIABLES},
                       "L_L2A": {**COMMON_VARIABLES, **L_L2A_REFLECTANCE_VARIABLES},
                       "W_L2A": {**COMMON_VARIABLES, **W_L2A_REFLECTANCE_VARIABLES},
                       "L_L2B": {**COMMON_VARIABLES, **L_L2B_REFLECTANCE_VARIABLES},
                       "W_L2B": {**COMMON_VARIABLES, **W_L2B_REFLECTANCE_VARIABLES}
                       }
