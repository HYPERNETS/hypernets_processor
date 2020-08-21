"""
Tests for Context class
"""

import unittest
from unittest.mock import MagicMock, patch, call
from hypernets_processor.version import __version__
from hypernets_processor.test.test_functions import setup_test_job_config, setup_test_processor_config
from hypernets_processor.context import Context

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def test_context_default_job_config(self, context):
    self.assertEqual(context.network, "land")
    self.assertEqual(context.site, "site")
    self.assertEqual(context.raw_data_directory, "data")
    self.assertEqual(context.anomoly_db_url, "sqlite:///anomoly.db")
    self.assertEqual(context.l1_mf_name, "standard_measurement_function")
    self.assertEqual(context.l2_mf_name, "standard_protocol")
    self.assertEqual(context.write_l1a, False)


def test_context_default_processor_config(self, context):
    self.assertEqual(context.version, "0.0")
    self.assertEqual(context.metadata_db_url, "sqlite:///metadata.db")
    self.assertEqual(context.archive_directory, "out")


class TestContext(unittest.TestCase):

    def test__unpack_processor_config(self):

        processor_config = setup_test_processor_config()

        context = Context()
        context._unpack_processor_config(processor_config)

        test_context_default_processor_config(self, context)

    def test__unpack_job_config(self):
        job_config = setup_test_job_config()

        context = Context()
        context._unpack_job_config(job_config)

        test_context_default_job_config(self, context)

    @patch('hypernets_processor.context.dataset')
    def test___init__(self, mock_dataset):
        job_config = setup_test_job_config()
        processor_config = setup_test_processor_config()
        logger = MagicMock()

        context = Context(job_config=job_config, processor_config=processor_config, logger=logger)

        test_context_default_processor_config(self, context)
        test_context_default_job_config(self, context)

        self.assertEqual(context.logger, logger)

        self.assertEqual(context.metadata_db, mock_dataset.connect.return_value)
        self.assertEqual(context.anomoly_db, mock_dataset.connect.return_value)

        self.assertCountEqual([call("sqlite:///anomoly.db"), call("sqlite:///metadata.db")],
                              mock_dataset.connect.call_args_list)


if __name__ == '__main__':
    unittest.main()
