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
    "b": {
        "description": "Not a standard sequence (too much missing data to keep processing)",
        "error": IOError,
        "error_msg": "Not a standard sequence (too much missing data to keep processing)",
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
    "q": {
        "description": "None of the scans in one or more series of the sequences passed the quality control",
        "error": None,
        "error_msg": None,
    },
    "l": {
        "description": "Ld missing for fresnel correction",
        "error": ValueError,
        "error_msg": "Ld missing for fresnel correction",
    },
    "nlu": {
        "description": "Not enough Lu scans",
        "error": None,
        "error_msg": None,
    },
    "nls": {
        "description": "Not enough Lsky scans",
        "error": None,
        "error_msg": None,
    },
    "ned": {
        "description": "Not enough Ed scans",
        "error": None,
        "error_msg": None,
    },
    "nld": {
        "description": "Not enough dark scans",
        "error": ValueError,
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
}
