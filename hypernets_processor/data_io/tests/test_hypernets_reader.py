"""
Tests for HypernetsReader class
"""

import unittest
from hypernets_processor.data_io.hypernets_reader import HypernetsReader


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestHypernetsReader(unittest.TestCase):
    def test_create_default_vector(self):
        du = HypernetsReader()


if __name__ == '__main__':
    unittest.main()
