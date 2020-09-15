"""
Context class
"""
from hypernets_processor.version import __version__
from hypernets_processor.utils.config import get_config_value
import dataset


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "3/8/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class Context:
    """
    Class to determine and store processor state
    """

    def __init__(self, job_config=None, processor_config=None, logger=None):

        # Initialise attributes
        self.logger = None
        self.metadata_db = None
        self.anomoly_db = None

        # File attributes
        self.time = None

        # Processor Attributes
        # Processor
        self.version = None

        # Input
        self.metadata_db_url = None

        # Output
        self.raw_data_directory = None

        # Job attributes
        # Info
        self.network = None
        self.site = None
        self.measurement_function_calibrate = 'StandardMeasurementFunction'
        self.measurement_function_interpolate = None
        self.measurement_function_surface_reflectance = None



        # Input
        self.raw_data_directory = None
        self.anomoly_db_url = None

        # Processing Options
        self.l1_mf_name = None
        self.l2_mf_name = None
        self.write_l1a = None
        self.wind_default=None

        self.wind_default = None
        self.wind_ancillary = None
        self.fresnel_option = None

        ## SimSpec settings
        self.similarity_test = None
        self.similarity_correct = None
        self.similarity_wr = None
        self.similarity_wp = None
        self.similarity_w1 = None
        self.similarity_w2 = None
        self.similarity_alpha = None

        # Set logger attribute
        if logger is not None:
            self.logger = logger

        # Unpack job_config to set relevant attributes
        if job_config is not None:
            self._unpack_job_config(job_config)

            # Connect to anomoly database
            self.anomoly_db = dataset.connect(self.anomoly_db_url)

        # Unpack processor_config to set relevant attributes
        if processor_config is not None:
            self._unpack_processor_config(processor_config)

            # Connect to metadata database
            self.metadata_db = dataset.connect(self.metadata_db_url)

    def _unpack_job_config(self, job_config):
        """
        Unpacks processor_config, sets relevant object attributes

        :type job_config: configparser.RawConfigParser
        :param job_config: job configuration information

        """

        # Unpack Info
        self.network = get_config_value(job_config, "Info", "network")
        self.site = get_config_value(job_config, "Info", "site")

        # Unpack Input
        self.raw_data_directory = get_config_value(job_config, "Input", "raw_data_directory")

        # Unpack Output
        self.anomoly_db_url = get_config_value(job_config, "Output", "anomoly_db_url")

        # Unpack processing options
        self.l1_mf_name = get_config_value(job_config, "Processing Options", "measurement_function_name")
        self.l2_mf_name = get_config_value(job_config, "Processing Options", "reflectance_protocol_name")
        self.write_l1a = get_config_value(job_config, "Processing Options", "write_l1a", dtype=bool)


    def _unpack_processor_config(self, processor_config):
        """
        Unpacks processor_config, sets relevant object attributes

        :type processor_config: configparser.RawConfigParser
        :param processor_config: processor configuration information
        """

        self.version = get_config_value(processor_config, "Processor", "version")
        self.metadata_db_url = get_config_value(processor_config, "Input", "metadata_db_url")
        self.archive_directory = get_config_value(processor_config, "Output", "archive_directory")
        self.wind_default= get_config_value(processor_config, "WaterStandardProtocol", "wind_default")
        self.wind_ancillary= get_config_value(processor_config, "WaterStandardProtocol", "wind_ancillary")
        self.fresnel_option= get_config_value(processor_config, "WaterStandardProtocol", "fresnel_option")
        self.rhymer_data_dir=get_config_value(processor_config, "WaterStandardProtocol", "rhymer_data_dir")

        ## SimSpec settings
        self.similarity_test= get_config_value(processor_config, "WaterStandardProtocol", "similarity_test")
        self.similarity_correct= get_config_value(processor_config, "WaterStandardProtocol", "similarity_correct")
        self.similarity_wr= get_config_value(processor_config, "WaterStandardProtocol", "similarity_wr")
        self.similarity_wp= get_config_value(processor_config, "WaterStandardProtocol", "similarity_wp")
        self.similarity_w1= get_config_value(processor_config, "WaterStandardProtocol", "similarity_w1")
        self.similarity_w2= get_config_value(processor_config, "WaterStandardProtocol", "similarity_w2")
        self.similarity_alpha= get_config_value(processor_config, "WaterStandardProtocol", "similarity_alpha")


if __name__ == '__main__':
    pass
