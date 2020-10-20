"""
Context class
"""
from hypernets_processor.version import __version__
from hypernets_processor.utils.config import get_config_value
from hypernets_processor.data_io.format.databases import DB_DICT_DEFS
from hypernets_processor.data_io.hypernets_db_builder import open_database

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
        self.product_db = None

        # Unpack processor_config to set relevant attributes
        if processor_config is not None:
            self.unpack_config(processor_config)

        # Unpack processor_config to set relevant attributes
        if job_config is not None:
            self.unpack_config(
                job_config, protected_values=PROCESSOR_CONFIG_PROTECTED_VALUES
            )

        # Connect to anomoly databases
        db_fmts = DB_DICT_DEFS.keys()
        for db_fmt in db_fmts:
            if db_fmt + "_db_url" in self.get_config_names():
                setattr(
                    self,
                    db_fmt+"_db",
                    open_database(self.get_config_value(db_fmt + "_db_url"), create_format=db_fmt)
                )

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
