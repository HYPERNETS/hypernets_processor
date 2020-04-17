"""
Tests for hypernets_scheduler_main module
"""

import unittest
from unittest.mock import patch, call
from hypernets_processor.version import __version__
from hypernets_processor.cli.hypernets_scheduler_main import main
from hypernets_processor.cli.hypernets_processor_main import main as hpmain

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "16/4/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestHypernetsSchedulerMain(unittest.TestCase):

    @patch('hypernets_processor.cli.hypernets_scheduler_main.Scheduler')
    def test_main(self, mock_sched):

        # main input parameters
        jobs_list = ["job1", "job2", "job3"]
        processor_config = {}
        scheduler_config = {"minutes": 3,
                            "seconds": None,
                            "hours": None,
                            "start_time": 2,
                            "parallel": False,
                            "log_path": None,
                            "verbose": False,
                            "quiet": False}

        main(jobs_list, processor_config, scheduler_config)

        self.assertTrue(mock_sched.called)

        # test schedule calls
        self.assertTrue(mock_sched.return_value.schedule.called)
        self.assertEqual(mock_sched.return_value.schedule.call_count, len(jobs_list))

        # define expected calls
        calls = []
        for job in jobs_list:
            calls.append(call(hpmain,
                              job_config={'log_path': None, 'verbose': False, 'quiet': False, 'name': job},
                              processor_config={},
                              scheduler_job_config={'name': job, 'seconds': None, 'minutes': 3,
                                                    'hours': None, 'parallel': False}))

        mock_sched.return_value.schedule.assert_has_calls(calls)

        # test run call
        mock_sched.return_value.run.assert_called_once_with(start_time=2)


if __name__ == "__main__":
    unittest.main()
