"""
Tests for common module
"""

import unittest
from hypernets_processor.version import __version__
from hypernets_processor.cli.common import read_config, read_scheduler_config, read_jobs_list
from configparser import RawConfigParser
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "31/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


scheduler_config_fname = "../../../data/tests/cli/scheduler.config"
scheduler_config_default_fname = "../../../data/tests/cli/scheduler_defaults.config"
scheduler_config_empty_fname = "../../../data/tests/cli/scheduler_empty.config"
jobs_list_fname = "../../../data/tests/cli/jobs.list"


class TestCommon(unittest.TestCase):
    def test_read_config(self):
        c = read_config(scheduler_config_fname)
        self.assertEqual(type(c), RawConfigParser)

    def test_read_schedule_config(self):
        d = read_scheduler_config(scheduler_config_fname)
        self.assertEqual(type(d), dict)

        d["seconds"] = 10
        d["minutes"] = None
        d["hours"] = None
        d["start_time"] = "now"
        d["log_path"] = "test.log"
        d["verbose"] = True
        d["quiet"] = True

    def test_read_schedule_config_defaults(self):
        d = read_scheduler_config(scheduler_config_default_fname)
        self.assertEqual(type(d), dict)

        d["seconds"] = None
        d["minutes"] = 12
        d["hours"] = None
        d["start_time"] = None
        d["log_path"] = None
        d["verbose"] = False
        d["quiet"] = False

    def test_read_schedule_config_empty(self):
        with self.assertRaises(ValueError):
            read_scheduler_config(scheduler_config_empty_fname)


    def test_read_jobs_list(self):
        jobs = read_jobs_list(jobs_list_fname)

        expected_jobs = [os.path.abspath("../../../data/tests/cli/job1.config"),
                         os.path.abspath("../../../data/tests/cli/job2.config")]

        self.assertCountEqual(jobs, expected_jobs)



if __name__ == "__main__":
    unittest.main()
