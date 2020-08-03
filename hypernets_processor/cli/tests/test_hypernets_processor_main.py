"""
Tests for hypernets_processor_main module
"""

import unittest
from unittest.mock import patch
from hypernets_processor.version import __version__
from hypernets_processor.cli.hypernets_processor_main import main
from hypernets_processor.cli.common import configure_logging
from configparser import RawConfigParser


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "15/4/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestHypernetsProcessorMain(unittest.TestCase):

    @patch('hypernets_processor.cli.hypernets_processor_main.configure_logging')
    @patch('hypernets_processor.cli.hypernets_processor_main.HypernetsProcessor')
    def test_main(self, mock_hp, mock_cf):
        job_config = RawConfigParser()
        processor_config = RawConfigParser()

        main(processor_config, job_config)

        self.assertTrue(mock_hp.called)
        mock_hp.assert_called_once_with(processor_config=processor_config,
                                        job_config=job_config,
                                        logger=mock_cf.return_value)
        self.assertTrue(mock_hp.return_value.run.called)


if __name__ == "__main__":
    unittest.main()
