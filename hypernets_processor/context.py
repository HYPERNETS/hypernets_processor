"""
Context class
"""
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class Context:
    """
    Class to store processor state
    """

    def __init__(self, job_config=None, processor_config=None, logger=None):
        self.logger = None
        self.network = None
        self.metadata_db = None

        if logger is not None:
            self.logger = logger

        if job_config is not None:
            self.unpack_job_config(job_config)

        if processor_config is not None:
            self.unpack_processor_config(processor_config)

    def unpack_job_config(self, job_config):
        # Job Configuration
        job_config_dict["name"] = fname
        if "Job" in job_config.keys():
            job_config_dict["name"] = job_config["Job"]["name"] if "name" in job_config["Job"].keys() else fname

        return None

    def unpack_processor_config(self, job_config):
        return None


if __name__ == '__main__':
    pass
