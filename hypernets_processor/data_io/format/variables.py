"""
Variable definitions for Hypernets land a water network data products
"""

import numpy as np
from hypernets_processor.data_io.format.flags import FLAG_MEANINGS

# Variables are defined in the below dictionaries. Each entry in a dictionary defines a product variable, the value
# of each entry defines the variable attributes with a dictionary that must contain the following entries:
#
# * "dim" - list of variable dimensions, selected from defined dimension names
# * "dtype" - dtype of data as numpy type
# * "attributes" - dictionary of variable attributes
# * "encoding" - dictionary of variable encoding parameters
#
# Product variables are defined following the specification defined in:
# Hypernets Team, Product Data Format Specification, v0.5 (2020)

# Dimensions
WL_DIM = "wavelength"
SERIES_DIM = "series"
SEQUENCE_DIM = "sequence"


# COMMON_VARIABLES - Variables are required for a data products
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

# L1A_RAD_VARIABLES - Variables required for the L1a radiance data product (in addition to COMMON_VARIABLES)
L1A_RAD_VARIABLES = {"u_random_radiance": {},
                     "u_systematic_radiance": {},
                     "cov_random_radiance": {},
                     "cov_systematic_radiance": {},
                     "radiance": {}}

# L1A_IRR_VARIABLES - Variables required for the L1a irradiance data product (in addition to COMMON_VARIABLES)
L1A_IRR_VARIABLES = {"u_random_irradiance": {},
                     "u_systematic_irradiance": {},
                     "cov_random_irradiance": {},
                     "cov_systematic_irradiance": {},
                     "irradiance": {}}

# L_L1B_VARIABLES - Variables required for the land network L1b data product (in addition to COMMON_VARIABLES)
L_L1B_VARIABLES = {**L1A_RAD_VARIABLES, **L1A_IRR_VARIABLES}

# W_L1B_VARIABLES - Variables required for the water network L1b data product (in addition to COMMON_VARIABLES)
W_L1B_VARIABLES = {}

# L_L1B_VARIABLES - Variables required for the water network L1b data product (in addition to COMMON_VARIABLES)
L_L2A_VARIABLES = {}

L2B_VARIABLES = {"u_random_reflectance": {},
                 "u_systematic_reflectance": {},
                 "cov_random_reflectance": {},
                 "cov_systematic_reflectance": {},
                 "reflectance": {}}