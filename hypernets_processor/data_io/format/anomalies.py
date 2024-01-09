"""
Anomaly definitions for Hypernets land and water network
"""

# The set of defined anomalies is defined below in DB_DICT_DEFS. Each entry is the anomaly_id of a defined anomaly, the
# value of which is a dictionary with the following entries:
#
# * description - text described anomaly
# * error - error object if the program should exit due to this anomaly, else None
# * error_msg - error message if the program should exit due to this anomaly, else None

ANOMALIES_DICT = {
    "a": {
        "description": "angle achieved by pan >3 and/or tilt >1 deg away from target angle during sequence",
        "error": None,
        "error_msg": None,
    },
    "m": {
        "description": "Metadata file missing",
        "error": IOError,
        "error_msg": "Metadata file missing",
    },
    "s": {
        "description": "meteo data missing",
        "error": None,
        "error_msg": None,
    },
    "x": {
        "description": "unexpected error during processing",
        "error": None,
        "error_msg": None,
    },
    "o": {
        "description": "more than 50% of data has random error above 100% (probably corrupted data)",
        "error": None,
        "error_msg": None,
    },
    "u": {
        "description": "some of the uncertainties have negative values",
        "error": ValueError,
        "error_msg": "some of the uncertainties have negative values",
    },
    "l": {
        "description": "Ld missing for sky reflectance correction",
        "error": ValueError,
        "error_msg": "Ld missing for sky reflectance correction",
    },
    "nlu": {
        "description": "Not enough Lu scans for series",
        "error": None,
        "error_msg": None,
    },
    "nld": {
        "description": "Not enough Lsky scans for series",
        "error": None,
        "error_msg": None,
    },
    "ned": {
        "description": "Not enough Ed scans for series",
        "error": None,
        "error_msg": None,
    },
    "nu": {
        "description": "Non constant illumination",
        "error": ValueError,
        "error_msg": "Coefficient of variation for Ed(550) is > 10%",
    },
    "nd": {
        "description": "Non constant illumination in downwelling radiance",
        "error": ValueError,
        "error_msg": "Coefficient of variation for Ld(550) is > 10%",
    },
    "cl": {
        "description": "No clear sky irradiance in sequence (i.e. overcast conditions)",
        "error": None,
        "error_msg": None,
    },
    "in": {
        "description": "Invalid sequence (due to not enough valid radiance or irradiance series)",
        "error": ValueError,
        "error_msg": "Invalid sequence (due to not enough valid radiance or irradiance series)",
    },
    "ms": {
        "description": "There are series missing from the standard sequence (either because not present, "
        "or flagged by `not_enough_dark_scans', `not_enough_irr_scans', `not_enough_rad_scans' "
        "or `vza_irradiance').",
        "error": None,
        "error_msg": None,
    },
    "d": {
        "description": "Discontinuity between VNIR and SWIR",
        "error": None,
        "error_msg": None,
    },
    "mf": {
        "description": "Invalid sequence,files mentioned in metadatafile are missing in DATA directory",
        "error": ValueError,
        "error_msg": None,
        "error_msg": None,
    },
}
