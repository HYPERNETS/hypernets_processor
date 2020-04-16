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

    :type processor_config: dict
    :param processor_config: processor configuration information, with entries:

    * ...

    :type job_config: dict
    :param job_config: job configuration information, with entries:

    * name (str) - Job name, default path of job config file
    * log_path (str) - Path to write log to, default None (means log goes to stdout)
    * verbose (bool) - Switch for verbose output, default False
    * quiet (bool) - Switch for quiet output, default False

    """

    # Configure logging
    logger = configure_logging(fname=job_config["log_path"], verbose=job_config["verbose"], quiet=job_config["quiet"])

    # Run processor
    hp = HypernetsProcessor(logger=logger)
    hp.run()

    return None


if __name__ == "__main__":
    pass
