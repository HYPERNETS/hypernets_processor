"""
Main function for hypernets_processor_cli to run
"""

from hypernets_processor.version import __version__
from hypernets_processor.main_processor import HypernetsProcessor
from hypernets_processor.cli.common import configure_logging, read_config_file

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(processor_config_path, job_config_path):
    """
    Main function to run hypernets_processor file processing chain

    :type processor_config_path: str
    :param processor_config_path: processor configuration file path

    :type job_config_path: str
    :param job_config_path: job configuration file path
    """

    processor_config = read_config_file(processor_config_path)
    job_config = read_config_file(job_config_path)

    # Configure logging
    logger = configure_logging(config=job_config)

    # Run processor
    hp = HypernetsProcessor(processor_config=processor_config, job_config=job_config, logger=logger)
    hp.run()

    return None


if __name__ == "__main__":
    pass
