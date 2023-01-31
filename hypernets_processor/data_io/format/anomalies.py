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
    "s": {"description": "sequence data incomplete", "error": None, "error_msg": None},
    "x": {
        "description": "unexpected error during processing",
        "error": None,
        "error_msg": None,
    },
    "m": {"description": "Metadata file missing", "error": IOError, "error_msg": None},
    "e": {"description": "Meteo file missing", "error": IOError, "error_msg": None},
    "l": {
        "description": "Ld missing for fresnel correction",
        "error": IOError,
        "error_msg": None,
    },
    "q": {
        "description": "None of the scans in a series passed the quality controll",
        "error": None,
        "error_msg": None,
    },
    "nlu": {"description": "Not enough Lu scans", "error": IOError, "error_msg": None},
    "nls": {
        "description": "Not enough Lsky scans",
        "error": IOError,
        "error_msg": None,
    },
    "i": {
        "description": "No valid irradiance measurements",
        "error": None,
        "error_msg": None,
    },
}
