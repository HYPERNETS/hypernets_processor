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
        "description": "angle achieved by pan tilt >5 deg away from target angle during sequence",
        "error": None,
        "error_msg": None,
    },
    "s": {
            "description": "sequence data incomplete",
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
    "m": {
        "description": "Metadata file missing",
        "error": IOError,
        "error_msg": "Metadata file missing",
    },
    "e": {
        "description": "Meteo file missing",
        "error": None,
        "error_msg": None,
    },
    "o": {
        "description": "more than 50% of data has random error above 100% (probably corrupted data)",
        "error": ValueError,
        "error_msg": "more than 50% of data has random error above 100% (probably corrupted data)",
    },
    "q": {
        "description": "None of the scans in a series passed the quality controll",
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
        "error": ValueError,
        "error_msg": "Not enough Lu scans",
    },
    "nls": {
        "description": "Not enough Lsky scans",
        "error": ValueError,
        "error_msg": "Not enough Lsky scans",
    },
    "i": {
        "description": "No valid irradiance measurements",
        "error": None,
        "error_msg": None,
    },
    "nu": {
        "description": "Non constant illumination",
        "error": None,
        "error_msg": None
    },
}
