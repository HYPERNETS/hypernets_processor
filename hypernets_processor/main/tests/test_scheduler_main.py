"""
Tests for scheduler_main module
"""

import unittest
from unittest.mock import patch, call
from hypernets_processor.version import __version__
from hypernets_processor.main.scheduler_main import main, unpack_scheduler_config
from hypernets_processor.utils.config import JOBS_FILE_PATH
from hypernets_processor.main.sequence_processor_main import main as hpmain
from configparser import RawConfigParser
import os
import random
import string


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "16/4/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

SCHEDULE_CONFIG_DICT = {
    "minutes": 3,
    "seconds": "",
    "hours": "",
    "start_time": "2",
    "parallel": False,
    "jobs_list": "path",
}

SCHEDULE_LOG_DICT = {"path": None, "verbose": False, "quiet": False}

JOBS_LIST = ["job1.config", "job2.config"]

this_directory = os.path.dirname(__file__)


def create_scheduler_config():
    scheduler_config = RawConfigParser()
    scheduler_config["Processor Schedule"] = SCHEDULE_CONFIG_DICT
    scheduler_config["Log"] = SCHEDULE_LOG_DICT
    return scheduler_config


def write_test_config_files(directory=this_directory):

    # Define temporary file paths
    temp_name = "".join(random.choices(string.ascii_lowercase, k=6))
    sched_path = os.path.join(directory, "schedule_" + temp_name + ".config")
    jobs_path = os.path.join(directory, "jobs_" + temp_name + ".txt")
    job_config1_path = os.path.join(directory, "job1_" + temp_name + ".config")
    job_config2_path = os.path.join(directory, "job2_" + temp_name + ".config")
    job_list = [job_config1_path, job_config2_path]

    # Create scheduler file
    sc = create_scheduler_config()
    sc["Processor Schedule"]["jobs_list"] = jobs_path

    with open(sched_path, "w") as configfile:
        sc.write(configfile)

    # Create job list file
    text = job_config1_path + "\n" + job_config2_path

    with open(jobs_path, "w") as f:
        f.write(text)

    with open(job_config1_path, "w") as f:
        f.write("[DEFAULT]")
    with open(job_config2_path, "w") as f:
        f.write("[DEFAULT]")

    return sched_path, jobs_path, job_list


class TestHypernetsSchedulerMain(unittest.TestCase):
    @patch("hypernets_processor.main.scheduler_main.Scheduler")
    def test_main(self, mock_sched):

        # main input parameters
        sched_path, jobs_path, job_list = write_test_config_files()

        main(scheduler_config_path=sched_path)

        self.assertTrue(mock_sched.called)

        # test schedule calls
        self.assertTrue(mock_sched.return_value.schedule.called)
        self.assertEqual(mock_sched.return_value.schedule.call_count, 2)

        # define expected calls
        calls = []
        for job in job_list:
            calls.append(
                call(
                    hpmain,
                    job_config_path=job,
                    to_archive=True,
                    scheduler_job_config={
                        "name": job,
                        "seconds": None,
                        "minutes": 3,
                        "hours": None,
                        "parallel": False,
                    },
                ),
            )

        mock_sched.return_value.schedule.assert_has_calls(calls)

        # test run call
        mock_sched.return_value.run.assert_called_once_with(start_time="2")

        os.remove(sched_path)
        os.remove(jobs_path)
        for job in job_list:
            os.remove(job)

    def test_unpack_scheduler_config(self):
        schedule_config = create_scheduler_config()
        d = unpack_scheduler_config(schedule_config)
        self.assertEqual(type(d), dict)

        expected_d = {
            "Processor Schedule": {
                "minutes": 3,
                "seconds": None,
                "hours": None,
                "start_time": "2",
                "parallel": False,
                "jobs_list": "path",
            }
        }
        self.assertDictEqual(expected_d, d)

    def test_unpack_scheduler_config_nojoblist(self):
        schedule_config = create_scheduler_config()
        schedule_config.remove_option("Processor Schedule", "jobs_list")

        d = unpack_scheduler_config(schedule_config)
        self.assertEqual(type(d), dict)

        expected_d = {
            "Processor Schedule": {
                "minutes": 3,
                "seconds": None,
                "hours": None,
                "start_time": "2",
                "parallel": False,
                "jobs_list": JOBS_FILE_PATH,
            }
        }
        self.assertDictEqual(expected_d, d)


if __name__ == "__main__":
    unittest.main()
