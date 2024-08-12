"""
Variable definitions for Hypernets land a water network data products
"""
from typing import Any

from copy import deepcopy

import numpy as np

from hypernets_processor.data_io.format.flags import FLAG_COMMON
from hypernets_processor.data_io.format.flags import FLAG_LAND
from hypernets_processor.data_io.format.flags import FLAG_WATER

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
CD_DIM = "calibrationdates"
NL_DIM = "nonlinearcoef"
ND_DIM = "nonlineardates"
WC_DIM = "wavcoef"
WD_DIM = "wavdates"

SERIES_DIM = "series"
SCAN_DIM = "scan"
Lu_SCAN_DIM = "scan"
SEQ_DIM = "sequence"

# Contributing variable sets
# --------------------------

# > COMMON_VARIABLES - Variables are required for a data products
COMMON_VARIABLES_SERIES = {
    "wavelength": {
        "dim": [WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "wavelength",
            "long_name": "wavelength as determined from lab calibration of HYPSTAR instrument",
            "units": "nm",
            "preferred_symbol": "wv",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.025, "offset": 320},
    },
    "bandwidth": {
        "dim": [WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "bandwidth",
            "long_name": "bandwidth FWHM assuming a Gaussian SRF",
            "units": "nm",
            "preferred_symbol": "FWHM",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.1, "offset": 0.0},
    },
    "viewing_azimuth_angle": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "viewing_azimuth_angle",
            "long_name": "viewing_azimuth_angle is the "
            "horizontal angle between the line of "
            "sight from the observation point to "
            "the sensor and True North. The angle is "
            "measured clockwise positive, starting"
            " from the North direction.",
            "units": "degrees",
            "reference": "True North",
            "preferred_symbol": "vaa",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "pointing_azimuth_angle": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pointing_azimuth_angle",
            "long_name": "pointing_azimuth_angle is the "
            "horizontal angle between the direction the sensor "
            "is pointing to, and True North. The angle is "
            "measured clockwise positive, starting "
            "from True North direction. This angle "
            "is 180 degrees different from the viewing_azimuth_angle.",
            "units": "degrees",
            "reference": "True North",
            "preferred_symbol": "vaa",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "viewing_zenith_angle": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "viewing_zenith_angle",
            "long_name": "viewing_zenith_angle is the angle "
            "between the local zenith and the direction "
            "from the location being measured"
            "to the sensor. This angle is "
            "measured starting from directly "
            "overhead and its range is from zero "
            "(directly overhead the observation "
            "target, i.e. sensor looking down) "
            "to 180 degrees (directly below"
            " the observation target, i.e. sensor"
            "pointing at local zenith).",
            "units": "degrees",
            "preferred_symbol": "vza",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0028, "offset": 0.0},
    },
    "solar_azimuth_angle": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "solar_azimuth_angle",
            "long_name": "solar_azimuth_angle is the horizontal "
            "angle between the line of sight to the "
            "sun and True North. The angle is "
            "measured clockwise.",
            "units": "degrees",
            "reference": "True North",
            "preferred_symbol": "saa",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "solar_zenith_angle": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "solar_zenith_angle",
            "long_name": "solar_zenith_angle is the the angle "
            "between the line of sight to the sun and"
            " the local zenith. This angle is "
            "measured starting from directly "
            "overhead and its range is from zero "
            "(directly overhead the observation "
            "target, i.e. sensor looking down) "
            "to 180 degrees (directly below"
            " the observation target, i.e. sensor"
            "pointing at local zenith).",
            "units": "degrees",
            "preferred_symbol": "sza",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0028, "offset": 0.0},
    },
    "acquisition_time": {
        "dim": [SERIES_DIM],
        "dtype": np.uint32,
        "attributes": {
            "standard_name": "time",
            "long_name": "Acquisition time in seconds since " "1970-01-01 " "00:00:00",
            "units": "s",
        },
    },
    "series_id": {
        "dim": [SERIES_DIM],
        "dtype": np.uint16,
        "attributes": {
            "standard_name": "series_id",
            "long_name": "Series id number",
            "units": "-",
        },
    },
}

COMMON_VARIABLES_SEQ = deepcopy(COMMON_VARIABLES_SERIES)
COMMON_VARIABLES_SCAN = deepcopy(COMMON_VARIABLES_SERIES)
COMMON_VARIABLES_Lu_SCAN = deepcopy(COMMON_VARIABLES_SERIES)

for variable in COMMON_VARIABLES_SEQ.keys():
    COMMON_VARIABLES_SEQ[variable]["dim"] = [
        d if d != SERIES_DIM else SEQ_DIM
        for d in COMMON_VARIABLES_SERIES[variable]["dim"]
    ]
for variable in COMMON_VARIABLES_SCAN.keys():
    COMMON_VARIABLES_SCAN[variable]["dim"] = [
        d if d != SERIES_DIM else SCAN_DIM
        for d in COMMON_VARIABLES_SERIES[variable]["dim"]
    ]
for variable in COMMON_VARIABLES_Lu_SCAN.keys():
    COMMON_VARIABLES_Lu_SCAN[variable]["dim"] = [
        d if d != SERIES_DIM else Lu_SCAN_DIM
        for d in COMMON_VARIABLES_SERIES[variable]["dim"]
    ]


L0A_RAD_VARIABLES = {
    "integration_time": {
        "dim": [SCAN_DIM],
        "dtype": np.uint32,
        "attributes": {
            "standard_name": "integration_time",
            "long_name": "Integration time during measurement",
            "units": "s",
        },
    },
    "temperature": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "temperature",
            "long_name": "temperature of instrument",
            "units": "degrees C",
        },
    },
    "acceleration_x_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_x_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "digital_number": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.int32,
        "attributes": {
            "standard_name": "digital_number",
            "long_name": "Digital number, raw data",
            "units": "-",
        },
    },
    "paa_ref": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ref in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ref",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_abs": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_abs as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_abs",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_ask": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ask as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ask",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
}

L0B_RAD_VARIABLES = {
    "integration_time": {
        "dim": [SERIES_DIM],
        "dtype": np.uint32,
        "attributes": {
            "standard_name": "integration_time",
            "long_name": "Integration time during measurement",
            "units": "s",
        },
    },
    "temperature": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "temperature",
            "long_name": "temperature of instrument",
            "units": "degrees C",
        },
    },
    "acceleration_x_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_x_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "digital_number": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.int32,
        "attributes": {
            "standard_name": "digital_number",
            "long_name": "Digital number, raw data",
            "units": "-",
            "unc_comps": [
                "u_rel_random_digital_number",
            ],
        },
    },
    "u_rel_random_digital_number": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on digital number",
            "long_name": "random relative uncertainty on digital number",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SERIES_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "dark_signal": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.uint32,
        "attributes": {
            "standard_name": "digital number for dark signal",
            "long_name": "Digital number, raw data, dark signal",
            "units": "-",
            "unc_comps": [
                "u_rel_random_dark_signal",
            ],
        },
    },
    "u_rel_random_dark_signal": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on digital number for dark signal",
            "long_name": "random relative uncertainty on digital number for dark signal",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SERIES_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "std_digital_number": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "standard deviation digital_number",
            "long_name": "standard deviation on digital number",
            "units": "-",
        },
    },
    "std_dark_signal": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "standard deviation dark_signal",
            "long_name": "standard deviation on digital number of dark signal",
            "units": "-",
        },
    },
    "n_valid_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid scans used in average of digital number",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total scans acquired",
            "long_name": "",
            "units": "-",
        },
    },
    "paa_ref": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ref in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ref",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_abs": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_abs as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_abs",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_ask": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ask as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ask",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
}

L0A_IRR_VARIABLES = L0A_RAD_VARIABLES
L0A_BLA_VARIABLES = L0A_RAD_VARIABLES

L0B_IRR_VARIABLES = L0B_RAD_VARIABLES

CAL_VARIABLES = {
    "wavelength": {
        "dim": [WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "wavelength",
            "long_name": "Wavelength",
            "units": "nm",
            "preferred_symbol": "wv",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.025, "offset": 320},
    },
    "wavpix": {
        "dim": [CD_DIM, WL_DIM],
        "dtype": np.uint16,
        "attributes": {
            "standard_name": "wavelength pixel",
            "long_name": "Wavelength pixel in L0 data that corresponds to the given wavelength",
        },
    },
    "gains": {
        "dim": [CD_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "gains",
            "long_name": "gains (calibration coefficients)",
            "units": "mW m^-2 nm^-1 sr^-1",
            "unc_comps": [
                "u_rel_systematic_indep_gains",
                "u_rel_systematic_corr_rad_irr_gains",
            ],
        },
    },
    "u_rel_systematic_indep_gains": {
        "dim": [CD_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on gains",
            "long_name": "the systematic relative uncertainty component on gains (calibration coefficients) that is not correlated between radiance and irradiance, in percent of the gains",
            "units": "%",
            "err_corr": [
                {"dim": CD_DIM, "form": "random", "params": [], "units": []},
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_gains"],
                    "units": [],
                },
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_gains": {
        "dim": [CD_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on gains (correlated radiance and irradiance)",
            "long_name": "the systematic relative uncertainty component on gains (calibration coefficients) that is correlated between radiance and irradiance, in percent of the gains",
            "units": "%",
            "err_corr": [
                {"dim": CD_DIM, "form": "random", "params": [], "units": []},
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_gains"],
                    "units": [],
                },
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_gains": {
        "dim": [CD_DIM, WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on gains",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on gains (calibration coefficients) that is not correlated between radiance and irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int16, "scale_factor": 0.0001, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_gains": {
        "dim": [CD_DIM, WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on gains (correlated radiance and irradiance)",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on gains (calibration coefficients) that is correlated between radiance and irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int16, "scale_factor": 0.0001, "offset": 0.0},
    },
    "wavelength_coefficients": {
        "dim": [WD_DIM, WC_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "wavelength coefficients",
            "long_name": "Polynomial coefficients for wavelength scale",
            "units": "-",
        },
    },
    "non_linearity_coefficients": {
        "dim": [ND_DIM, NL_DIM],
        "dtype": np.float64,
        "attributes": {
            "standard_name": "non linearity coefficients",
            "long_name": "non linearity coefficients",
            "units": "-",
        },
    },
    # "u_rel_random_non_linearity_coefficients": {"dim": [NL_DIM],
    #                           "dtype": np.uint32,
    #                           "attributes": {"standard_name": "random relative uncertainty on non linearity coefficients",
    #                                          "long_name": "random relative uncertainty on non linearity coefficients",
    #                                          "units": "-"},
    #                           "encoding": {'dtype': np.uint32, "scale_factor": 0.001, "offset": 0.0}},
    # "u_rel_systematic_indep_non_linearity_coefficients": {"dim": [NL_DIM],
    #                           "dtype": np.uint32,
    #                           "attributes": {"standard_name": "independent systematic relative uncertainty on non linearity coefficients",
    #                                          "long_name": "the systematic relative uncertainty component on non linearity coefficients that is not correlated between radiance and irradiance",
    #                                          "units": "-"},
    #                           "encoding": {'dtype': np.uint32, "scale_factor": 0.001, "offset": 0.0}},
    # "u_rel_systematic_corr_rad_irr_non_linearity_coefficients": {"dim": [NL_DIM],
    #                           "dtype": np.uint32,
    #                           "attributes": {"standard_name": "systematic relative uncertainty on non linearity coefficients (correlated radiance and irradiance)",
    #                                          "long_name": "the systematic relative uncertainty component on non linearity coefficients that is correlated between radiance and irradiance",
    #                                          "units": "-"},
    #                           "encoding": {'dtype': np.uint32, "scale_factor": 0.001, "offset": 0.0}},
    # "err_corr_systematic_indep_non_linearity_coefficients":{"dim":[NL_DIM,NL_DIM],
    #                                   "dtype":np.int16,"attributes":{
    #         "standard_name":"independent correlation matrix of systematic error on non linearity coefficients",
    #         "long_name":"Error-correlation matrix between wavelengths for the systematic error component on non linearity coefficients that is not correlated between radiance and irradiance",
    #         "units":"-"},"encoding":{'dtype':np.int16,
    #                                                    "scale_factor":0.001,
    #                                                    "offset":0.0}},
    # "err_corr_systematic_corr_rad_irr_non_linearity_coefficients":{"dim":[NL_DIM,NL_DIM],
    #                                          "dtype":np.int16,"attributes":{
    #         "standard_name":"correlation matrix of systematic error on non linearity coefficients (correlated radiance and irradiance)",
    #         "long_name":"Error-correlation matrix between wavelengths for the systematic error component on non linearity coefficients that is correlated between radiance and irradiance",
    #         "units":"-"},"encoding":{'dtype':np.int16,
    #                                                    "scale_factor":0.001,
    #                                                    "offset":0.0}},
}


# > L1A_RAD_VARIABLES - Radiance Variables required for L1 data products (except water L1B)
L1A_RAD_VARIABLES = {
    "u_rel_random_radiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on radiance",
            "long_name": "random relative uncertainty on upwelling radiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_radiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on radiance",
            "long_name": "the systematic relative uncertainty component on radiance that is not correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_radiance"],
                    "units": [],
                },
                {"dim": SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_radiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on radiance, correlated with irradiance",
            "long_name": "the systematic relative uncertainty component on radiance that is correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_radiance"],
                    "units": [],
                },
                {"dim": SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is not correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on radiance, correlated with irradiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "radiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "radiance",
            "long_name": "upwelling radiance",
            "units": "mW m^-2 nm^-1 sr^-1",
            "unc_comps": [
                "u_rel_random_radiance",
                "u_rel_systematic_indep_radiance",
                "u_rel_systematic_corr_rad_irr_radiance",
            ],
        },
    },
    "acceleration_x_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_x_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "paa_ref": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ref in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ref",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_abs": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_abs as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_abs",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_ask": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ask as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ask",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
}

L1A_IRR_VARIABLES = {
    "u_rel_random_irradiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on irradiance",
            "long_name": "random relative uncertainty on downwelling irradiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_irradiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on irradiance",
            "long_name": "the systematic relative uncertainty component on downwelling irradiance that is not correlated with radiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_irradiance"],
                    "units": [],
                },
                {"dim": SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_irradiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on irradiance, correlated with radiance",
            "long_name": "the systematic relative uncertainty component on downwelling irradiance that is correlated with radiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_irradiance"],
                    "units": [],
                },
                {"dim": SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_irradiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on irradiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on irradiance that is not correlated with radiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_irradiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on irradiance, correlated with radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on irradiance that is correlated with radiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "irradiance": {
        "dim": [WL_DIM, SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "irradiance",
            "long_name": "downwelling irradiance",
            "units": "mW m^-2 nm^-1",
            "unc_comps": [
                "u_rel_random_irradiance",
                "u_rel_systematic_indep_irradiance",
                "u_rel_systematic_corr_rad_irr_irradiance",
            ],
        },
    },
    "acceleration_x_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_x_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_mean": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_std": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "paa_ref": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ref in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ref",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_abs": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_abs as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_abs",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "paa_ask": {
        "dim": [SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "pan (pointing azimuth angle) from pt_ask as in metadata",
            "long_name": "",
            "units": "degrees",
            "reference": "no idea",
            "preferred_symbol": "paa_ask",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
}

L1B_RAD_VARIABLES = {
    "u_rel_random_radiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on radiance",
            "long_name": "random relative uncertainty on upwelling radiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SERIES_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_radiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on radiance",
            "long_name": "the systematic relative uncertainty component on upwelling radiance that is not correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_radiance"],
                    "units": [],
                },
                {"dim": SERIES_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_radiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on radiance, correlated with irradiance",
            "long_name": "the systematic relative uncertainty component on upwelling radiance that is correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_radiance"],
                    "units": [],
                },
                {"dim": SERIES_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is not correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on radiance, correlated with irradiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radianc that is correlated with irradiancee",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "n_valid_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid scans used in average of VNIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total scans acquired for VNIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_valid_scans_SWIR": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid scans used in average of SWIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans_SWIR": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total scans acquired for SWIR",
            "long_name": "",
            "units": "-",
        },
    },
    "radiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "radiance",
            "long_name": "upwelling radiance",
            "units": "mW m^-2 nm^-1 sr^-1",
            "unc_comps": [
                "u_rel_random_radiance",
                "u_rel_systematic_indep_radiance",
                "u_rel_systematic_corr_rad_irr_radiance",
            ],
        },
    },
    "std_radiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "standard deviation radiance",
            "long_name": "standard deviation on upwelling radiance",
            "units": "mW m^-2 nm^-1 sr^-1",
        },
    },
    "acceleration_x_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_x_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
}


L1B_IRR_VARIABLES = {
    "u_rel_random_irradiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on irradiance",
            "long_name": "random relative uncertainty on downwelling irradiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SERIES_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_irradiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on irradiance",
            "long_name": "the systematic relative uncertainty component on downwelling irradiance that is not correlated with radiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_irradiance"],
                    "units": [],
                },
                {"dim": SERIES_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_irradiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on irradiance, correlated with radiance",
            "long_name": "the systematic relative uncertainty component on downwelling irradiance that is correlated with radiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_irradiance"],
                    "units": [],
                },
                {"dim": SERIES_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_irradiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on irradiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on irradiance that is not correlated with radiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_irradiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on irradiance, correlated with radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on irradiance that is correlated with radiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "n_valid_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid scans used in average of VNIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total scans acquired for VNIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_valid_scans_SWIR": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid scans used in average of SWIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans_SWIR": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total scans acquired for SWIR",
            "long_name": "",
            "units": "-",
        },
    },
    "irradiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "irradiance",
            "long_name": "downwelling irradiance",
            "units": "mW m^-2 nm^-1",
            "unc_comps": [
                "u_rel_random_irradiance",
                "u_rel_systematic_indep_irradiance",
                "u_rel_systematic_corr_rad_irr_irradiance",
            ],
        },
    },
    "std_irradiance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "standard deviation irradiance",
            "long_name": "standard deviation on downwelling irradiance",
            "units": "mW m^-2 nm^-1",
        },
    },
    "acceleration_x_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_x_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_x_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_y_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_y_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_mean": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_mean",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "acceleration_z_std": {
        "dim": [SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "acceleration_z_std",
            "long_name": "",
            "units": "-",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
}


W_L1C_VARIABLES = {
    "u_rel_random_downwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on radiance",
            "long_name": "random relative uncertainty on upwelling radiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_downwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on radiance",
            "long_name": "the systematic relative uncertainty component on upwelling radiance that is not correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_downwelling_radiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_downwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on radiance",
            "long_name": "the systematic relative uncertainty component on upwelling radiance that is correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_downwelling_radiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_downwelling_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is not correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_downwelling_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "downwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "radiance",
            "long_name": "downwelling radiance",
            "units": "mW m^-2 nm^-1 sr^-1",
            "unc_comps": [
                "u_rel_random_downwelling_radiance",
                "u_rel_systematic_indep_downwelling_radiance",
                "u_rel_systematic_corr_rad_irr_downwelling_radiance",
            ],
        },
    },
    "std_downwelling_radiance": {
        "dim": [WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "std radiance",
            "long_name": "standard deviation for downwelling radiance",
            "units": "mW m^-2 nm^-1 sr^-1",
        },
    },
    "u_rel_random_upwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on radiance",
            "long_name": "random relative uncertainty on upwelling radiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_upwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on radiance",
            "long_name": "the systematic relative uncertainty component on upwelling radiance that is not correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_upwelling_radiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_upwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on radiance",
            "long_name": "the systematic relative uncertainty component on upwelling radiance that is correlated with irradiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_upwelling_radiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_upwelling_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is not correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_upwelling_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on radiance that is correlated with irradiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "upwelling_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "upwelling_radiance",
            "long_name": "upwelling radiance",
            "units": "mW m^-2 nm^-1 sr^-1",
            "unc_comps": [
                "u_rel_random_upwelling_radiance",
                "u_rel_systematic_indep_upwelling_radiance",
                "u_rel_systematic_corr_rad_irr_upwelling_radiance",
            ],
        },
    },
    "u_rel_random_irradiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "random relative uncertainty on irradiance",
            "long_name": "random relative uncertainty on downwelling irradiance",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_irradiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent systematic relative uncertainty on irradiance",
            "long_name": "the systematic relative uncertainty component on downwelling irradiance that is not correlated with radiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_irradiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_irradiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "systematic relative uncertainty on irradiance, correlated with radiance",
            "long_name": "the systematic relative uncertainty component on downwelling irradiance that is correlated with radiance",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_corr_rad_irr_irradiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_irradiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "independent correlation matrix of systematic error on irradiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on irradiance that is not correlated with radiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_irradiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "correlation matrix of systematic error on irradiance, correlated with radiance",
            "long_name": "Error-correlation matrix between wavelengths for the systematic error component on irradiance that is correlated with radiance",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "irradiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "irradiance",
            "long_name": "downwelling irradiance",
            "units": "mW m^-2 nm^-1",
            "unc_comps": [
                "u_rel_random_irradiance",
                "u_rel_systematic_indep_irradiance",
                "u_rel_systematic_corr_rad_irr_irradiance",
            ],
        },
    },
    "std_irradiance": {
        "dim": [WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "std irradiance",
            "long_name": "standard deviation for downwelling irradiance",
            "units": "mW m^-2 nm^-1",
        },
    },
    "rhof": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "air_water_int_radiance_ratio",
            "long_name": "Fraction of downwelling sky radiance reflected at the "
            "air-water interface",
            "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
            "units": "-",
            "preferred_symbol": "rhof",
        },
    },
    "rhof_wind": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "rhof_wind",
            "long_name": "Surface wind speed used for the retrieval of the "
            "fraction of downwelling sky radiance reflected at "
            "the air-water interface",
            "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
            "units": "ms^-1",
        },
    },
    "rhof_sza": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "rhof_solar_zenith_angle",
            "long_name": "Solar zenith angle used for the retrieval of the "
            "fraction of downwelling sky radiance reflected at "
            "the air-water interface",
            "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
            "units": "degrees",
        },
    },
    "rhof_raa": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "rhof_relative_azimuth_angle",
            "long_name": "Relative azimuth angle from sun to sensor (0° when "
            "sun and sensor are aligned 180° when the sensor is "
            "looking into the sunglint) used for the retrieval "
            "of the fraction of downwelling sky radiance "
            "reflected at the air-water interface",
            "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
            "units": "degrees",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0055, "offset": 0.0},
    },
    "rhof_vza": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "rhof_sensor_zenith_angle",
            "long_name": "Sensor zenith angle used for the retrieval of the "
            "fraction of downwelling sky radiance reflected at "
            "the air-water interface",
            "reference": "",
            "units": "degrees",
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.0028, "offset": 0.0},
    },
}

# L_L2A_REFLECTANCE_VARIABLES - Reflectance variables required for L2A land data product
L_L2A_REFLECTANCE_VARIABLES = {
    "u_rel_random_reflectance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_random_reflectance",
            "long_name": "Random relative uncertainty on hemispherical-conical reflectance factor",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": SERIES_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_reflectance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_systematic_reflectance",
            "long_name": "Systematic relative uncertainty on hemispherical-conical reflectance factor",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_reflectance"],
                    "units": [],
                },
                {"dim": SERIES_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_reflectance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "err_corr_systematic_reflectance",
            "long_name": "Error-correlation matrix of systematic uncertainty on hemispherical-conical reflectance factor"
            "reflectance "
            "uncertainty",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "n_valid_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid radiance scans used in average of VNIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total radiance scans acquired for VNIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_valid_scans_SWIR": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of valid radiance scans used in average of SWIR",
            "long_name": "",
            "units": "-",
        },
    },
    "n_total_scans_SWIR": {
        "dim": [SERIES_DIM],
        "dtype": np.uint8,
        "attributes": {
            "standard_name": "number of total radiance scans acquired for SWIR",
            "long_name": "",
            "units": "-",
        },
    },
    "reflectance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "reflectance",
            "long_name": "hemispherical-conical reflectance factor",
            "units": "-",
            "unc_comps": [
                "u_rel_random_reflectance",
                "u_rel_systematic_reflectance",
            ],
        },
    },
    "std_reflectance": {
        "dim": [WL_DIM, SERIES_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "standard deviation hemispherical-conical reflectance factor",
            "long_name": "standard deviation on hemispherical-conical reflectance factor that is due to the variability in radiance (i.e. not accounting for variability in darks or in irradiance)",
            "units": "-",
        },
    },
}

# W_L2A_REFLECTANCE_VARIABLES - Reflectance variables required for L2A water data product
W_L1C_REFLECTANCE_VARIABLES = {
    "reflectance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "surface_upwelling_radiance_per_unit_"
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
            "preferred_symbol": "rhow",
            "unc_comps": [
                "u_rel_random_reflectance",
                "u_rel_systematic_reflectance",
            ],
        },
    },
    "water_leaving_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "water_leaving_radiance",
            "long_name": "water-leaving radiance"
            " of electromagnetic radiation "
            "(unspecified single wavelength)"
            " from the water body by "
            "cosine-collector radiometer",
            "reference": "",
            "units": "mW m^-2 nm^-1 sr^-1",
            "preferred_symbol": "lw",
            "unc_comps": [
                "u_rel_random_water_leaving_radiance",
                "u_rel_systematic_indep_water_leaving_radiance",
                "u_rel_systematic_corr_rad_irr_water_leaving_radiance",
            ],
        },
    },
    "reflectance_nosc": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "reflectance_nosc",
            "long_name": "Reflectance of the water column at the "
            "surface without correction for the NIR "
            "similarity spectrum "
            "(see Ruddick et al., 2006)",
            "units": "-",
            "preferred_symbol": "rhow_nosc",
            "unc_comps": [
                "u_rel_random_reflectance_nosc",
                "u_rel_systematic_reflectance_nosc",
            ],
        },
    },
    "u_rel_random_water_leaving_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_random_normalized_water_leaving_radiance",
            "long_name": "Random normalized water leaving radiance "
            "relative uncertainty",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_indep_water_leaving_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_systematic_indep_water_leaving_radiance",
            "long_name": "water leaving radiance Systematic uncertainty component that is independent with uncertainties on irradiance "
            "relative uncertainty",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_water_leaving_radiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_indep_water_leaving_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "err_corr_systematic_indep_water_leaving_radiance",
            "long_name": "Error-correlation matrix of water leaving radiance Systematic uncertainty component that is independent with uncertainties on irradiance"
            "leaving radiance uncertainty",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_corr_rad_irr_water_leaving_radiance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_systematic_corr_rad_irr_water_leaving_radiance",
            "long_name": "water leaving radiance Systematic uncertainty component that is correlated with uncertainties on irradiance "
            "relative uncertainty",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_indep_water_leaving_radiance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_corr_rad_irr_water_leaving_radiance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "err_corr_systematic_corr_rad_irr_water_leaving_radiance",
            "long_name": "Error-correlation matrix of water leaving radiance Systematic uncertainty component that is correlated with uncertainties on irradiance"
            "leaving radiance uncertainty",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_random_reflectance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_random_reflectance",
            "long_name": "Random water leaving reflectance " "relative uncertainty",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_reflectance": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_systematic_reflectance",
            "long_name": "Systematic water leaving reflectance relative uncertainty",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_reflectance"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_reflectance": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "err_corr_systematic_reflectance",
            "long_name": "Error-correlation matrix of systematic water leaving "
            "reflectance uncertainty",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_random_reflectance_nosc": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_random_reflectance_nosc",
            "long_name": "Random water leaving reflectance not corrected "
            "for NIR similarity spectrum relative uncertainty",
            "units": "%",
            "err_corr": [
                {"dim": WL_DIM, "form": "random", "params": [], "units": []},
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_reflectance_nosc": {
        "dim": [WL_DIM, Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_systematic_water_leaving_reflectance_nosc",
            "long_name": "Systematic water leaving reflectance not "
            "corrected for NIR similarity spectrum "
            "relative uncertainty",
            "units": "%",
            "err_corr": [
                {
                    "dim": WL_DIM,
                    "form": "err_corr_matrix",
                    "params": ["err_corr_systematic_reflectance_nosc"],
                    "units": [],
                },
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "err_corr_systematic_reflectance_nosc": {
        "dim": [WL_DIM, WL_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "err_corr_systematic_reflectance_nosc",
            "long_name": "Error-correlation matrix of systematic water "
            "leaving reflectance not corrected for NIR "
            "similarity spectrum uncertainty",
            "units": "-",
        },
        "encoding": {"dtype": np.int8, "scale_factor": 0.01, "offset": 0.0},
    },
    "epsilon": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "epsilon",
            "long_name": "Similarity spectrum ratio at two wavelengths see Ruddick et al. (2016)",
            "reference": "",
            "units": "-",
            "unc_comps": [
                "u_rel_random_epsilon",
                "u_rel_systematic_epsilon",
            ],
        },
    },
    "u_rel_random_epsilon": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_random_epsilon",
            "long_name": "Random epsilon " "relative uncertainty",
            "units": "%",
            "err_corr": [
                {"dim": Lu_SCAN_DIM, "form": "random", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "u_rel_systematic_epsilon": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "u_rel_systematic_epsilon",
            "long_name": "Systematic epsilon relative uncertainty",
            "units": "%",
            "err_corr": [
                {"dim": Lu_SCAN_DIM, "form": "systematic", "params": [], "units": []},
            ],
        },
        "encoding": {"dtype": np.uint16, "scale_factor": 0.01, "offset": 0.0},
    },
    "rhof": {
        "dim": [Lu_SCAN_DIM],
        "dtype": np.float32,
        "attributes": {
            "standard_name": "air_water_int_radiance_ratio",
            "long_name": "Fraction of downwelling sky radiance reflected at the "
            "air-water interface",
            "reference": "SYSTEM_HEIGHT_DEPLOYEMENT",
            "units": "-",
            "preferred_symbol": "rhof",
        },
    },
}

W_L2A_REFLECTANCE_VARIABLES = deepcopy(W_L1C_REFLECTANCE_VARIABLES)

for variable in W_L2A_REFLECTANCE_VARIABLES.keys():
    W_L2A_REFLECTANCE_VARIABLES[variable]["dim"] = [
        d if d != Lu_SCAN_DIM else SERIES_DIM
        for d in W_L2A_REFLECTANCE_VARIABLES[variable]["dim"]
    ]
W_L2A_REFLECTANCE_VARIABLES["n_valid_scans"] = {
    "dim": [SERIES_DIM],
    "dtype": np.uint8,
    "attributes": {
        "standard_name": "number of valid radiance scans used in average of VNIR",
        "long_name": "",
        "units": "-",
    },
}

W_L2A_REFLECTANCE_VARIABLES["n_total_scans"] = {
    "dim": [SERIES_DIM],
    "dtype": np.uint8,
    "attributes": {
        "standard_name": "number of total radiance scans acquired",
        "long_name": "",
        "units": "-",
    },
}

W_L2A_REFLECTANCE_VARIABLES["std_reflectance"] = {
    "dim": [WL_DIM, SERIES_DIM],
    "dtype": np.float32,
    "attributes": {
        "standard_name": "standard deviation reflectance",
        "long_name": "standard deviation on reflectance that is due to the variability in radiance (i.e. not accounting for variability in darks or in irradiance)",
        "units": "-",
    },
}


W_L2A_REFLECTANCE_VARIABLES["std_water_leaving_radiance"] = {
    "dim": [WL_DIM, SERIES_DIM],
    "dtype": np.float32,
    "attributes": {
        "standard_name": "standard deviation water_leaving_radiance",
        "long_name": "standard deviation on water leaving radiance that is due to the variability in radiance (i.e. not accounting for variability in darks or in irradiance)",
        "units": "mW m^-2 nm^-1 sr^-1",
    },
}

W_L2A_REFLECTANCE_VARIABLES["std_reflectance_nosc"] = {
    "dim": [WL_DIM, SERIES_DIM],
    "dtype": np.float32,
    "attributes": {
        "standard_name": "standard deviation reflectance_nosc",
        "long_name": "standard deviation on Reflectance of the water column at the "
        "surface without correction for the NIR that is due to the variability in radiance (i.e. not accounting for variability in darks or in irradiance) ",
        "units": "-",
    },
}

W_L2A_REFLECTANCE_VARIABLES["std_epsilon"] = {
    "dim": [SERIES_DIM],
    "dtype": np.float32,
    "attributes": {
        "standard_name": "standard deviation epsilon",
        "long_name": "standard deviation on Similarity spectrum ratio at two wavelengths see Ruddick et al. (2016)  that is due to the variability in radiance (i.e. not accounting for variability in darks or in irradiance)",
        "units": "-",
    },
}


L_L2B_REFLECTANCE_VARIABLES = deepcopy(L_L2A_REFLECTANCE_VARIABLES)
W_L2B_REFLECTANCE_VARIABLES = deepcopy(W_L2A_REFLECTANCE_VARIABLES)

C_QUALITY_SCAN = {
    "quality_flag": {
        "dim": [SCAN_DIM],
        "dtype": "flag",
        "attributes": {
            "standard_name": "quality_flag",
            "long_name": "A variable with the standard name of quality_"
            "flag contains an indication of assessed "
            "quality information of another data variable."
            " The linkage between the data variable and the"
            " variable or variables with the standard_name"
            " of quality_flag is achieved using the "
            "ancillary_variables attribute.",
            "flag_meanings": FLAG_COMMON,
        },
    }
}

C_QUALITY_SERIES = {
    "quality_flag": {
        "dim": [SERIES_DIM],
        "dtype": "flag",
        "attributes": {
            "standard_name": "quality_flag",
            "long_name": "A variable with the standard name of quality_"
            "flag contains an indication of assessed "
            "quality information of another data variable."
            " The linkage between the data variable and the"
            " variable or variables with the standard_name"
            " of quality_flag is achieved using the "
            "ancillary_variables attribute.",
            "flag_meanings": FLAG_COMMON,
        },
    }
}

L_QUALITY = {
    "quality_flag": {
        "dim": [SERIES_DIM],
        "dtype": "flag",
        "attributes": {
            "standard_name": "quality_flag",
            "long_name": "The quality flag field consists of 32 bits. Every bit is related to the absence or presence of a a flag where each bit encodes a flag given in the flag_meanings attribute",
            "flag_meanings": FLAG_COMMON + FLAG_LAND,
        },
    }
}

W_QUALITY_SERIES = {
    "quality_flag": {
        "dim": [SERIES_DIM],
        "dtype": "flag",
        "attributes": {
            "standard_name": "quality_flag",
            "long_name": "A variable with the standard name of quality_"
            "flag contains an indication of assessed "
            "quality information of another data variable."
            " The linkage between the data variable and the"
            " variable or variables with the standard_name"
            " of quality_flag is achieved using the "
            "ancillary_variables attribute.",
            "flag_meanings": FLAG_COMMON + FLAG_WATER,
        },
    }
}

W_QUALITY_SCAN = deepcopy(W_QUALITY_SERIES)
for variable in W_QUALITY_SCAN.keys():
    W_QUALITY_SCAN[variable]["dim"] = [
        d if d != SERIES_DIM else Lu_SCAN_DIM for d in W_QUALITY_SCAN[variable]["dim"]
    ]
# File format variable defs
# -------------------------

VARIABLES_DICT_DEFS: Any = {
    "L0A_RAD": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L0A_RAD_VARIABLES},
    "L0A_IRR": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L0A_IRR_VARIABLES},
    "L0A_BLA": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L0A_BLA_VARIABLES},
    "L0B_RAD": {**COMMON_VARIABLES_SERIES, **C_QUALITY_SERIES, **L0B_RAD_VARIABLES},
    "L0B_IRR": {**COMMON_VARIABLES_SERIES, **C_QUALITY_SERIES, **L0B_RAD_VARIABLES},
    "CAL": {**CAL_VARIABLES},
    "L_L1A_RAD": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L1A_RAD_VARIABLES},
    "L_L1A_IRR": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L1A_IRR_VARIABLES},
    "W_L1A_RAD": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L1A_RAD_VARIABLES},
    "W_L1A_IRR": {**COMMON_VARIABLES_SCAN, **C_QUALITY_SCAN, **L1A_IRR_VARIABLES},
    "L_L1B_RAD": {**COMMON_VARIABLES_SERIES, **L_QUALITY, **L1B_RAD_VARIABLES},
    "L_L1B_IRR": {**COMMON_VARIABLES_SERIES, **L_QUALITY, **L1B_IRR_VARIABLES},
    "W_L1B_RAD": {**COMMON_VARIABLES_SERIES, **W_QUALITY_SERIES, **L1B_RAD_VARIABLES},
    "W_L1B_IRR": {**COMMON_VARIABLES_SERIES, **W_QUALITY_SERIES, **L1B_IRR_VARIABLES},
    "L_L1C": {
        **COMMON_VARIABLES_SERIES,
        **L_QUALITY,
        **L1B_RAD_VARIABLES,
        **L1B_IRR_VARIABLES,
    },
    "W_L1C": {
        **COMMON_VARIABLES_Lu_SCAN,
        **W_QUALITY_SCAN,
        **W_L1C_VARIABLES,
        **W_L1C_REFLECTANCE_VARIABLES,
    },
    "L_L2A": {**COMMON_VARIABLES_SERIES, **L_QUALITY, **L_L2A_REFLECTANCE_VARIABLES},
    "W_L2A": {
        **COMMON_VARIABLES_SERIES,
        **W_QUALITY_SERIES,
        **W_L2A_REFLECTANCE_VARIABLES,
    },
    "L_L2B": {**COMMON_VARIABLES_SERIES, **L_QUALITY, **L_L2B_REFLECTANCE_VARIABLES},
    "W_L2B": {**COMMON_VARIABLES_SERIES, **L_QUALITY, **W_L2B_REFLECTANCE_VARIABLES},
}
