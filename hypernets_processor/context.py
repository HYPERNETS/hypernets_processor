"""
Context class
"""
from hypernets_processor.version import __version__
from hypernets_processor.utils.config import get_config_value
import dataset
import configparser

"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"

PROCESSOR_CONFIG_PROTECTED_VALUES = []


class Context:
    """
    Class to determine and store processor state

    :type processor_config: configparser.RawConfigParser
    :param processor_config: processor config data object

    :type job_config: configparser.RawConfigParser
    :param job_config: job config data object
    """

    def __init__(self, processor_config=None, job_config=None, logger=None):

        # Initialise attributes
        self.config_values = {}
        self.logger = logger
        self.metadata_db = None
        self.anomoly_db = None


        # Unpack processor_config to set relevant attributes
        if processor_config is not None:
            self.unpack_config(processor_config)

        # Unpack processor_config to set relevant attributes
        if job_config is not None:
            self.unpack_config(
                job_config, protected_values=PROCESSOR_CONFIG_PROTECTED_VALUES
            )

        # Connect to metadata database
        if "metadata_db_url" in self.get_config_names():
            self.metadata_db = dataset.connect(self.get_config_value("metadata_db_url"))

        # Connect to anomoly database
        if "anomoly_db_url" in self.get_config_names():
            self.anomoly_db = dataset.connect(self.get_config_value("anomoly_db_url"))
                                              
    def unpack_config(self, config, protected_values=None):
        """
        Unpacks config data, sets relevant entries to values instance attribute

        :type config: configparser.RawConfigParser
        :param config: config data
        """
        cp = configparser.ConfigParser()
        cp.read(config)

        protected_values = [] if protected_values is None else protected_values
        for section in cp.sections():
            for name in cp[section].keys():

                if name not in protected_values:
                    value = get_config_value(cp, section, name)
                    self.set_config_value(name, value)

    def set_config_value(self, name, value):
        """
        Sets config data to values instance attribute

        :type name: str
        :param name: config data name

        :param value: config data value
        """

        self.config_values[name] = value

    def get_config_value(self, name):
        """
        Get config value

        :type name: str
        :param name: config data name

        :return: config value
        """

        return self.config_values[name] if name in self.get_config_names() else None

    def get_config_names(self):
        """
        Get available config value names

        :return: config value names
        :rtype: list
        """

        return list(self.config_values.keys())


if __name__ == "__main__":
    pass
