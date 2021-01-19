"""
Tests for FilenameUtil class
"""

import unittest
from unittest.mock import patch
from freezegun import freeze_time
from datetime import datetime
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
        with freeze_time("2020/1/8 9:45:30"):

            context = setup_test_context()
            context.set_config_value("time", datetime(2018, 4, 3, 11, 0, 0))
            pnu = ProductNameUtil(context=context)
            pname = pnu.create_product_name("L_L1A_RAD")
            self.assertEqual("HYPERNETS_L_TEST_L1A_RAD_201804031100_202001080945_v0.0", pname)

    def test_create_product_name_params(self):
        with freeze_time("2020/1/8 9:45:30"):

            pnu = ProductNameUtil()
            pname = pnu.create_product_name("L_L1A_RAD", network="l", site_id="test", version="0.0",
                                            time=datetime(2018, 4, 3, 11, 0, 0))
            self.assertEqual("HYPERNETS_L_TEST_L1A_RAD_201804031100_202001080945_v0.0", pname)

    def test_create_product_name_none(self):
        with freeze_time("2020/1/8 9:45:30"):
            pnu = ProductNameUtil()
            pname = pnu.create_product_name("L_L1A_RAD")
            self.assertEqual("HYPERNETS_L1A_RAD_202001080945", pname)


if __name__ == '__main__':
    unittest.main()
