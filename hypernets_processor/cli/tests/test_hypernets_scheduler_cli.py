"""
Tests for hypernets_scheduler_cli module
"""

import unittest
from hypernets_processor.version import __version__
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "31/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


jobs_list = "../../../data/tests/cli/jobs.list"




class TestHypernetsSchedulerCLI(unittest.TestCase):
    def test_entrypoint(self):
        exit_status = os.system('hypernets_processor --help')
        self.assertEqual(exit_status, 0)

    def test_main(self):
        pass



if __name__ == "__main__":
    unittest.main()
