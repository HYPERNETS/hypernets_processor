"""
Tests for main_processor.HypernetsProcessor class
"""

import unittest
from unittest.mock import patch
from hypernets_processor.main_processor import HypernetsProcessor
from hypernets_processor.test.test_functions import setup_test_context


'''___Authorship___'''
__author__ = ""
__created__ = "16/10/2020"
__email__ = ""
__status__ = "Development"


# This tests won't work atm!
class TestHypernetsProcessor(unittest.TestCase):
    # One way of testing is to set up the module to run the specific method you're interested in. You can then test
    # the output of that module.
    def test_run(self):

        context = setup_test_context()

        hp = HypernetsProcessor()
        hp.context = context

        hp.run()

        self.assertTrue(True)

    # An issue with testing high level modules is that changes to the low level code change the output of the high
    # level modules too. This means you would have to update all your tests every time you make a change.
    # Really when you test a high level module you just want to check it calls the right low level modules with the
    # right input. This is where mocks come in.
    # In this example I'm mocking RhymerHypstar, so when you run the code it doesn't actually run RhymerHypstar.
    @patch('hypernets_processor.main_processor.RhymerHypstar')
    def test_run_mock(self, mock_RhymerHypstar):
        context = setup_test_context()

        hp = HypernetsProcessor()
        hp.context = context

        hp.run()

        # Here you can check what RhymerHypstar was called with to see that that works correctly
        mock_RhymerHypstar.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
