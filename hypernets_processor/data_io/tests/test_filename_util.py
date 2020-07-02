"""
Tests for FilenameUtil class
"""

import unittest
import datetime
from hypernets_processor.data_io.filename_util import FilenameUtil
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "7/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestFilenameUtil(unittest.TestCase):

    def test_create_file_name_l1a_irr(self):

        fname = FilenameUtil.create_file_name_l1a_irr("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_IRR_201804031100_v0.00.nc", fname)

    def test_create_file_name_l1a_rad(self):

        fname = FilenameUtil.create_file_name_l1a_rad("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_RAD_201804031100_v0.00.nc", fname)

    def test_create_file_name_l1b(self):

        fname = FilenameUtil.create_file_name_l1b("W", "BSBE", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_W_BSBE_L1B_201804031100_v0.00.nc", fname)


    def test_create_file_name_l2a(self):

        fname = FilenameUtil.create_file_name_l2a("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_REF_201804031100_v0.00.nc", fname)

    def test_create_file_name_l2b(self):

        fname = FilenameUtil.create_file_name_l2b("L", "GBNA", datetime.datetime(2018, 4, 3, 11, 00, 00), "0.00")
        self.assertEqual("HYPERNETS_L_GBNA_REFD_20180403_v0.00.nc", fname)


if __name__ == '__main__':
    unittest.main()
