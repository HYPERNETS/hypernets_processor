"""
Contains main class for orchestrating hypernets data processing jobs
"""

from hypernets_processor.version import __version__
from hypernets_processor.context import Context


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class HypernetsProcessor:
    """
    Class to orchestrate Hypernets data processing jobs

    :type logger: logging.logger
    :param logger: logger
    """

    def __init__(self, job_config=None, processor_config=None, logger=None):
        """
        Constructor method
        """

        self.context = Context(job_config, processor_config, logger)

    def run(self):
        """
        Runs hypernets data processing jobs
        """

        return None


if __name__ == "__main__":
    pass
