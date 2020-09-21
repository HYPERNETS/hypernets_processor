"""
Module of helper functions for configfile operations
"""


from hypernets_processor.version import __version__
import os


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "4/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def get_config_value(config, section, key, dtype=None):
    """
    Return value from config file

    :type config: configparser.RawConfig
    :param config: parsed config file

    :type section: str
    :param section: section to retrieve data from

    :type key: str
    :param key: key in section to retrieve data from

    :type dtype: type
    :param dtype: type of data to return

    :return: config value
    :rtype: str/bool/int/float
    """

    val = config.get(section, key, fallback=None)

    dtype = infer_dtype(val) if dtype is None else dtype

    if (val == "") or (val is None):
        if dtype == bool:
            return False
        return None

    if dtype == str:
        return val

    elif dtype == bool:
        return config.getboolean(section, key)

    elif dtype == int:
        return config.getint(section, key)

    elif dtype == float:
        return config.getfloat(section, key)


def infer_dtype(val):

    # Check bool
    if (val == "True") or (val == "False"):
        return bool

    # Check int
    is_int = True
    try:
        int(val)
    except:
        is_int = False

    if is_int:
        return int

    # Check float
    is_float = True
    try:
        float(val)
    except:
        is_float = False

    if is_float:
        return float

    return str


if __name__ == "__main__":
    pass
