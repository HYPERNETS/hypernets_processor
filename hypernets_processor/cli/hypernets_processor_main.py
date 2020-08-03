"""
Main function for hypernets_processor_cli to run
"""

from hypernets_processor.version import __version__
from hypernets_processor.hypernets_processor import HypernetsProcessor
from hypernets_processor.cli.common import configure_logging


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(processor_config, job_config):
    """
    Main function to run hypernets_processor

    :type processor_config: configparser.RawConfigParser
    :param processor_config: processor configuration information

    :type job_config: configparser.RawConfigParser
    :param job_config: job configuration information

    """

    # Configure logging
    logger = configure_logging(config=job_config)

    # Run processor
    hp = HypernetsProcessor(processor_config=processor_config, job_config=job_config, logger=logger)
    hp.run()

    return None


if __name__ == "__main__":
    pass
