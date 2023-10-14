"""
ProductNameUtil class
"""

from hypernets_processor.version import __version__
from datetime import datetime

"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "7/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


TIME_FMT_L12A = "%Y%m%dT%H%M"
TIME_FMT_L2B = "%Y%m%d"


DS_FORMAT_FNAMES = {
    "L0_RAD": "L0_RAD",
    "L0_BLA": "L0_BLA",
    "L0_IRR": "L0_IRR",
    "CAL": "CAL",
    "L_L0B": "L_L0B",
    "L_L1A_RAD": "L1A_RAD",
    "W_L1A_RAD": "L1A_RAD",
    "L_L1A_IRR": "L1A_IRR",
    "W_L1A_IRR": "L1A_IRR",
    "L_L1B_RAD": "L1B_RAD",
    "L_L1B_IRR": "L1B_IRR",
    "W_L1B_RAD": "L1B_RAD",
    "W_L1B_IRR": "L1B_IRR",
    "W_L1B": "L1B",
    "L_L1C": "L1C",
    "W_L1C": "L1C_ALL",
    "W_L1D": "L1D",
    "L_L2A": "L2A_REF",
    "W_L2A": "L2A_REF",
    "L_L2B": "L2B_REF",
    "W_L2B": "L2B_REF",
    "IMG": "IMG",
}


class ProductNameUtil:
    """
    Class to generate Hypernets product product names
    """

    def __init__(self, context=None):
        self.context = context

    def create_product_name(
        self,
        ds_format,
        network=None,
        site_id=None,
        time=None,
        time_processing=None,
        version=None,
        swir=None,
        angles=None,
    ):
        """
        Return a valid product name for Hypernets file

        :type ds_format: str
        :param ds_format: data product format

        :type context: hypernets_process.context.Context
        :param context: processor context

        :type network: str
        :param network: (optional, overrides value in context) abbreviated network name

        :type site_id: str
        :param site_id: (optional, overrides value in context) abbreviated site name

        :type time: datetime.datetime
        :param time: (optional, overrides value in context) acquisition time

        :type version: str
        :param version: (optional, overrides value in context) processing version

        :type swir: bool
        :param swir: if swir file

        :return: product name
        :rtype: str
        """

        # Unpack params
        if (network is None) and (self.context is not None):
            network = self.context.get_config_value("network")

        if (site_id is None) and (self.context is not None):
            site_id = self.context.get_config_value("site_id")

        if (time is None) and (self.context is not None):
            time = self.context.get_config_value("time")

        if (time_processing is None) and (self.context is not None):
            time_processing = self.context.get_config_value("start_time_processing_sequence")

        if (version is None) and (self.context is not None):
            version = str(self.context.get_config_value("version"))

        if swir:
            swir = "SWIR"
        if angles:
            angles = angles

        # Prepare product name parts
        ptype = DS_FORMAT_FNAMES[ds_format]

        if type(time) is not datetime and time is not None:
            time = datetime.strptime(time, "%Y%m%dT%H%M%S")

        if type(time_processing) is not datetime and time_processing is not None:
            time_processing = datetime.strptime(time_processing, "%Y%m%dT%H%M%S")

        time_string = time.strftime(TIME_FMT_L12A) if time is not None else None
        time_processing_string = time_processing.strftime(TIME_FMT_L12A) if time_processing is not None else None
        network = network.upper() if network is not None else None
        site_id = site_id.upper() if site_id is not None else None
        version = "v" + version if version is not None else None

        if time_processing_string is None:
            time_processing_string = datetime.now().strftime(TIME_FMT_L12A)

        # Assemble parts
        product_name_parts = [
            "HYPERNETS",
            network,
            site_id,
            ptype,
            time_string,
            time_processing_string,
            angles,
            version,
            swir,
        ]
        product_name_parts = filter(None, product_name_parts)
        return "_".join(product_name_parts)


if __name__ == "__main__":
    pass
