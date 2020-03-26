"""
Main function for hypernets_processor_cli to run
"""

from hypernets_processor.version import __version__
from hypernets_processor.hypernets_processor import HypernetsProcessor

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(logger=None):
    """
    Main function to run hypernets_processor

    :type logger: logging.logger
    :param logger: logger
    """

    hp = HypernetsProcessor(logger=logger)
    hp.run()

    return None


if __name__ == "__main__":
    pass
