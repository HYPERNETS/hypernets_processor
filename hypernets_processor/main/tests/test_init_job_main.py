"""
Tests for init_job_main module
"""

import unittest
from unittest.mock import patch
from hypernets_processor.version import __version__
from hypernets_processor.main.init_job_main import main
from hypernets_processor.utils.config import read_config_file
import random
import string
import os
import shutil


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/10/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestInitJobMain(unittest.TestCase):

    def test_main(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        settings = dict()
        settings["job_name"] = "test"
        settings["job_working_directory"] = os.path.join(tmpdir, "test_working")
        settings["raw_data_directory"] = os.path.join(tmpdir, "test_raw")
        settings["add_to_scheduler"] = False

        main(settings)

        expect_config_path = os.path.abspath(
            os.path.join(
                settings["job_working_directory"],
                settings["job_name"] + ".config"
            )
        )

        expect_log_path = os.path.abspath(
            os.path.join(
                settings["job_working_directory"],
                settings["job_name"] + ".log"
            )
        )

        self.assertTrue(os.path.exists(settings["job_working_directory"]))
        self.assertTrue(os.path.exists(settings["raw_data_directory"]))
        self.assertTrue(os.path.exists(expect_config_path))
        self.assertTrue(os.path.exists(expect_log_path))

        config = read_config_file(expect_config_path)
        self.assertEqual(config["Job"]["job_name"], "test")
        self.assertEqual(config["Job"]["job_working_directory"], os.path.abspath(settings["job_working_directory"]))
        self.assertEqual(config["Input"]["raw_data_directory"], os.path.abspath(settings["raw_data_directory"]))
        self.assertEqual(config["Log"]["log_path"], expect_log_path)

        shutil.rmtree(tmpdir)

    @patch('hypernets_processor.main.init_job_main.JOBS_FILE_PATH', "test1.txt")
    def test_main_add_to_scheduler_empty(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        settings = dict()
        settings["job_name"] = "test"
        settings["job_working_directory"] = os.path.join(tmpdir, "test_working")
        settings["raw_data_directory"] = os.path.join(tmpdir, "test_raw")
        settings["add_to_scheduler"] = True

        open("test1.txt", 'a').close()

        main(settings)

        expect_config_path = os.path.abspath(
            os.path.join(
                settings["job_working_directory"],
                settings["job_name"] + ".config"
            )
        )

        with open("test1.txt", "r") as f:
            t = f.read()
            self.assertEqual(t, expect_config_path)

        shutil.rmtree(settings["job_working_directory"])
        shutil.rmtree(settings["raw_data_directory"])

        shutil.rmtree(tmpdir)
        os.remove("test1.txt")

    @patch('hypernets_processor.main.init_job_main.JOBS_FILE_PATH', "test2.txt")
    def test_main_add_to_scheduler_append(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        settings = dict()
        settings["job_name"] = "test"
        settings["job_working_directory"] = os.path.join(tmpdir, "test_working")
        settings["raw_data_directory"] = os.path.join(tmpdir, "test_raw")
        settings["add_to_scheduler"] = True

        with open("test2.txt", 'w') as f:
            f.write("test")

        main(settings)

        expect_config_path = os.path.abspath(
            os.path.join(
                settings["job_working_directory"],
                settings["job_name"] + ".config"
            )
        )

        with open("test2.txt", "r") as f:
            t = f.read()
            self.assertEqual(t, "test"+"\n"+expect_config_path)

        shutil.rmtree(settings["job_working_directory"])
        shutil.rmtree(settings["raw_data_directory"])

        shutil.rmtree(tmpdir)
        os.remove("test2.txt")


if __name__ == "__main__":
    unittest.main()
