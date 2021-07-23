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
        "error_msg": None
    },
    "s": {
            "description": "sequence data incomplete",
            "error": IOError,
            "error_msg": "sequence data incomplete (review log for more details)"
        },
    "x": {
            "description": "unexpected error during processing",
            "error": None,
            "error_msg": None
        },
    "m": {
                "description": "Metadata file missing",
                "error": IOError,
                "error_msg": None
            }
}
