"""
Tests for FilenameUtil class
"""

import unittest
import datetime
from hypernets_processor.data_io.product_name_util import ProductNameUtil
from hypernets_processor.version import __version__
from hypernets_processor.test.test_functions import setup_test_context


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "7/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestProductNameUtil(unittest.TestCase):

    def test_create_product_name_context(self):

        context = setup_test_context()
        context.time = datetime.datetime(2018, 4, 3, 11, 0, 0)
        pnu = ProductNameUtil()
        pname = pnu.create_product_name("L_L1A_RAD", context=context)
        self.assertEqual("HYPERNETS_LAND_SITE_L1A_RAD_201804031100_v0.0.nc", pname)

    def test_create_product_name_params(self):

        pnu = ProductNameUtil()
        pname = pnu.create_product_name("L_L1A_RAD", network="land", site="site", version="0.0",
                                        time=datetime.datetime(2018, 4, 3, 11, 0, 0))
        self.assertEqual("HYPERNETS_LAND_SITE_L1A_RAD_201804031100_v0.0.nc", pname)

    def test_create_product_name_none(self):

        pnu = ProductNameUtil()
        pname = pnu.create_product_name("L_L1A_RAD")
        self.assertEqual("HYPERNETS_L1A_RAD.nc", pname)


if __name__ == '__main__':
    unittest.main()
