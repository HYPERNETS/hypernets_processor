"""
Tests for hypernets_processor_main module
"""

import unittest
from unittest.mock import patch
from hypernets_processor.version import __version__
from hypernets_processor.main.sequence_processor_main import main, get_target_sequences
from hypernets_processor.test.test_functions import setup_test_context
import string
import random
import os
import shutil


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/10/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestSequenceProcessorMain(unittest.TestCase):

    @patch('hypernets_processor.main.sequence_processor_main.configure_logging')
    @patch('hypernets_processor.main.sequence_processor_main.SequenceProcessor')
    @patch('hypernets_processor.main.sequence_processor_main.get_target_sequences')
    @patch('hypernets_processor.main.sequence_processor_main.Context')
    def test_main(self, mock_con, mock_gts, mock_sp, mock_cf):
        job_config_path = "jpath"
        processor_config_path = "ppath"
        main(job_config_path=job_config_path, processor_config_path=processor_config_path, to_archive=True)

        self.assertTrue(mock_sp.called)
        mock_sp.assert_called_once_with(context=mock_con.return_value)

    def test_get_target_sequences_toarchive(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        context = setup_test_context(
            raw_data_directory=os.path.join(tmpdir, "data"),
            archive_directory=os.path.join(tmpdir, "out"),
            metadata_db_url="sqlite:///"+tmpdir+"/metadata.db",
            anomaly_db_url="sqlite:///"+tmpdir+"/anomaly.db",
            archive_db_url="sqlite:///"+tmpdir+"/archive.db",
            create_directories=True,
            create_dbs=True
        )

        expected_sequences = [os.path.join(tmpdir, "data", "SEQ20200311T112530")]
        sequences = get_target_sequences(context, True)

        self.assertCountEqual(expected_sequences, sequences)

        shutil.rmtree(tmpdir)

    def test_get_target_sequences_nottoarchive(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        context = setup_test_context(
            raw_data_directory=os.path.join(tmpdir, "data"),
            archive_directory=os.path.join(tmpdir, "out"),
            metadata_db_url="sqlite:///" + tmpdir + "/metadata.db",
            anomaly_db_url="sqlite:///" + tmpdir + "/anomaly.db",
            archive_db_url="sqlite:///" + tmpdir + "/archive.db",
            create_directories=True,
            create_dbs=True
        )

        expected_sequences = [
            os.path.join(tmpdir, "data", "SEQ20200311T112230"),
            os.path.join(tmpdir, "data", "SEQ20200311T112330"),
            os.path.join(tmpdir, "data", "SEQ20200311T112430"),
            os.path.join(tmpdir, "data", "SEQ20200311T112530")
        ]
        sequences = get_target_sequences(context, False)

        self.assertCountEqual(expected_sequences, sequences)

        shutil.rmtree(tmpdir)

    def test_get_target_sequences_1sequence(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        context = setup_test_context(
            raw_data_directory=os.path.join(tmpdir, "data"),
            archive_directory=os.path.join(tmpdir, "out"),
            metadata_db_url="sqlite:///" + tmpdir + "/metadata.db",
            anomaly_db_url="sqlite:///" + tmpdir + "/anomaly.db",
            archive_db_url="sqlite:///" + tmpdir + "/archive.db",
            create_directories=True,
            create_dbs=True
        )

        context.set_config_value(
            "raw_data_directory",
            os.path.join(context.get_config_value("raw_data_directory"), "SEQ20200311T112230"),
        )

        expected_sequences = [os.path.join(tmpdir, "data", "SEQ20200311T112230")]
        sequences = get_target_sequences(context, False)

        self.assertCountEqual(expected_sequences, sequences)

        shutil.rmtree(tmpdir)

    def test_get_target_sequences_0sequence(self):
        tmpdir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        context = setup_test_context(
            raw_data_directory=os.path.join(tmpdir, "data"),
            archive_directory=os.path.join(tmpdir, "out"),
            metadata_db_url="sqlite:///" + tmpdir + "/metadata.db",
            anomaly_db_url="sqlite:///" + tmpdir + "/anomaly.db",
            archive_db_url="sqlite:///" + tmpdir + "/archive.db",
            create_directories=True,
            create_dbs=True
        )

        context.set_config_value(
            "raw_data_directory",
            context.get_config_value("archive_directory"),
        )

        expected_sequences = []
        sequences = get_target_sequences(context, False)

        self.assertCountEqual(expected_sequences, sequences)

        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()
