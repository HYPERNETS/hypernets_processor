"""
ProductNameUtil class
"""

from hypernets_processor.version import __version__
from datetime import datetime

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "7/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


TIME_FMT_L12A = "%Y%m%d%H%M"
TIME_FMT_L2B = "%Y%m%d"


DS_FORMAT_FNAMES = {"L0_RAD": "L0_RAD",
                    "L0_BLA": "L0_BLA",
                    "L0_IRR": "L0_IRR",
                    "L_L1A_RAD": "L1A_RAD",
                    "W_L1A_RAD": "L1A_RAD",
                    "L_L1A_IRR": "L1A_IRR",
                    "W_L1A_IRR": "L1A_IRR",
                    "L_L1B_RAD": "L1B",
                    "W_L1B_RAD": "L1B",
                    "L_L1B_IRR": "L1B",
                    "W_L1B_IRR": "L1B",
                    "L_L2A": "L2A_REF",
                    "W_L2A": "L2A_REF",
                    "L_L2B": "L2B_REF",
                    "W_L2B": "L2B_REF"}


class ProductNameUtil:
    """
    Class to generate Hypernets product product names
    """

    @staticmethod
    def create_product_name(ds_format, context=None, network=None, site=None, time=None, version=None):
        """
        Return a valid product name for Hypernets file

        :type ds_format: str
        :param ds_format: data product format

        :type context: hypernets_process.context.Context
        :param context: processor context

        :type network: str
        :param network: (optional, overrides value in context) abbreviated network name

        :type site: str
        :param site: (optional, overrides value in context) abbreviated site name

        :type time: datetime.datetime
        :param time: (optional, overrides value in context) acquisition time

        :type version: str
        :param version: (optional, overrides value in context) processing version

        :return: product name
        :rtype: str
        """

        # Unpack params
        network = context.network if (network is None) and (context is not None) else network
        site = context.site if (site is None) and (context is not None) else site
        time = context.time if (time is None) and (context is not None) else time
        version = context.version if (version is None) and (context is not None) else version

        # Prepare product name parts
        print(DS_FORMAT_FNAMES)
        ptype = DS_FORMAT_FNAMES[ds_format]

        if type(time) is not datetime and time is not None:
            time = datetime.strptime(time, '%Y%m%dT%H%M%S')
        time_string = time.strftime(TIME_FMT_L12A) if time is not None else None
        network = network.upper() if network is not None else None
        site = site.upper() if network is not None else None
        version = "v" + version if version is not None else None

        # Assemble parts
        product_name_parts = ["HYPERNETS", network, site, ptype, time_string, version]
        product_name_parts = filter(None, product_name_parts)

        return "_".join(product_name_parts) + ".nc"


if __name__ == '__main__':
    pass
