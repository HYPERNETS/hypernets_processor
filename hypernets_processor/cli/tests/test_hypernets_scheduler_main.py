"""
Tests for hypernets_scheduler_main module
"""

import unittest
from unittest.mock import patch, call
from hypernets_processor.version import __version__
from hypernets_processor.cli.hypernets_scheduler_main import main, unpack_scheduler_config
from hypernets_processor.cli.hypernets_processor_main import main as hpmain
from configparser import RawConfigParser


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "16/4/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

SCHEDULE_CONFIG_DICT = {"minutes": 3,
                        "seconds": None,
                        "hours": None,
                        "start_time": "2",
                        "parallel": False}

SCHEDULE_LOG_DICT = {"path": None,
                     "verbose": False,
                     "quiet": False}


def create_scheduler_config():
    scheduler_config = RawConfigParser()
    scheduler_config["Schedule"] = SCHEDULE_CONFIG_DICT
    scheduler_config["Log"] = SCHEDULE_LOG_DICT
    return scheduler_config


class TestHypernetsSchedulerMain(unittest.TestCase):

    @patch('hypernets_processor.cli.hypernets_scheduler_main.read_config_file')
    @patch('hypernets_processor.cli.hypernets_scheduler_main.Scheduler')
    def test_main(self, mock_sched, mock_read):

        # main input parameters
        jobs_list = ["job1", "job2", "job3"]
        processor_config = RawConfigParser()
        scheduler_config = create_scheduler_config()

        main(jobs_list, processor_config, scheduler_config)

        self.assertTrue(mock_sched.called)

        # test schedule calls
        self.assertTrue(mock_sched.return_value.schedule.called)
        self.assertEqual(mock_sched.return_value.schedule.call_count, len(jobs_list))

        # define expected calls
        calls = []
        for job in jobs_list:
            calls.append(call(hpmain,
                              job_config=mock_read.return_value,
                              processor_config=processor_config,
                              scheduler_job_config={'name': job, 'seconds': None, 'minutes': 3,
                                                    'hours': None, 'parallel': False}))

        mock_sched.return_value.schedule.assert_has_calls(calls)

        # test run call
        mock_sched.return_value.run.assert_called_once_with(start_time='2')

    def test_unpack_scheduler_config(self):
        schedule_config = create_scheduler_config()
        d = unpack_scheduler_config(schedule_config)
        self.assertEqual(type(d), dict)

        self.assertDictEqual(SCHEDULE_CONFIG_DICT, d)


if __name__ == "__main__":
    unittest.main()
