"""
HypernetsWriter class
"""

from hypernets_processor.data_io.template_util import TemplateUtil
import xarray as xr
import os

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = "0.0"
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


TIME_FMT_L12A = "%Y%m%d%H%M"
TIME_FMT_L2B = "%Y%m%d"


class HypernetsWriter:
    """
    Class to write Hypernets output files
    """

    @staticmethod
    def write(dataset, path, overwrite=False):

        if os.path.isfile(path):
            if overwrite is True:
                os.remove(path)
            else:
                raise IOError("The file already exists: " + path)

        dataset.to_write(path)

    @staticmethod
    def create_template_dataset_l1(n_wavelengths, n_series):
        """
        Returns empty Hypernets Level 1 dataset to be populated with data

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        # Initialise dataset
        dataset = xr.Dataset()

        tu = TemplateUtil()

        # Add variables from template
        tu.add_common_variables(dataset, n_wavelengths, n_series)
        tu.add_l1_variables(dataset, n_wavelengths, n_series)

        # Add metadata from template
        tu.add_common_metadata(dataset)
        tu.add_l1_metadata(dataset)

        return dataset

    @staticmethod
    def create_template_dataset_l2a(n_wavelengths, n_series):
        """
        Returns empty Hypernets Level 2a dataset to be populated with data

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        # Initialise dataset
        dataset = xr.Dataset()

        tu = TemplateUtil()

        # Add variables from template
        tu.add_common_variables(dataset, n_wavelengths, n_series)
        tu.add_l2a_variables(dataset, n_wavelengths, n_series)

        # Add metadata from template
        tu.add_common_metadata(dataset)
        tu.add_l2_metadata(dataset)

        return dataset

    @staticmethod
    def create_template_dataset_l2b(n_wavelengths, n_series):
        """
        Returns empty Hypernets Level 2b dataset to be populated with data

        :type n_wavelengths: int
        :param n_wavelengths: number of wavelengths

        :type n_series:
        :param n_series: number of series

        :returns:
            dataset *xarray.Dataset*

            Empty dataset
        """

        # Initialise dataset
        dataset = xr.Dataset()

        tu = TemplateUtil()

        # Add variables from template
        tu.add_common_variables(dataset, n_wavelengths, n_series)
        tu.add_l2b_variables(dataset, n_wavelengths, n_series)

        # Add metadata from template
        tu.add_common_metadata(dataset)
        tu.add_l2_metadata(dataset)

        return dataset

    @staticmethod
    def create_file_name_l1(network, site, time, version):
        """
        Return a valid file name for Hypernets Level 1 file

        :type network: str
        :param network: abbreviated network name

        :type site: str
        :param site: abbreviated site name

        :type time: datetime.datetime
        :param time: acquisition time

        :type version: str
        :param version: processing version

        :return:
            fname *str*

            Level 1 filename
        """

        time_string = time.strftime(TIME_FMT_L12A)
        return HypernetsWriter._create_file_name(network, site, "RAD", time_string, version)

    @staticmethod
    def create_file_name_l2a(network, site, time, version):
        """
        Return a valid file name for Hypernets Level 2a file

        :type network: str
        :param network: abbreviated network name

        :type site: str
        :param site: abbreviated site name

        :type time: datetime.datetime
        :param time: acquisition time

        :type version: str
        :param version: processing version

        :return:
            fname *str*

            Level 2a filename
        """

        time_string = time.strftime(TIME_FMT_L12A)
        return HypernetsWriter._create_file_name(network, site, "REF", time_string, version)

    @staticmethod
    def create_file_name_l2b(network, site, time, version):
        """
        Return a valid file name for Hypernets Level 2b file

        :type network: str
        :param network: abbreviated network name

        :type site: str
        :param site: abbreviated site name

        :type time: datetime.datetime
        :param time: acquisition time

        :type version: str
        :param version: processing version

        :return:
            fname *str*

            Level 2b filename
        """

        time_string = time.strftime(TIME_FMT_L2B)
        return HypernetsWriter._create_file_name(network, site, "REFD", time_string, version)

    @staticmethod
    def _create_file_name(network, site, ptype, time_string, version):
        return "_".join(["HYPERNETS", network.upper(), site.upper(), ptype, time_string, "v"+version]) + ".nc"


if __name__ == '__main__':
    pass
