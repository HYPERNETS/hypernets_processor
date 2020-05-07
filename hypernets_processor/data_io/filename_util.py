"""
FilenameUtil class
"""

from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "7/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


TIME_FMT_L12A = "%Y%m%d%H%M"
TIME_FMT_L2B = "%Y%m%d"


class FilenameUtil:
    """
    Class to generate Hypernets product filenames
    """

    @staticmethod
    def create_file_name_l1a_rad(network, site, time, version):
        """
        Return a valid file name for Hypernets Level 1a radiance file

        :type network: str
        :param network: abbreviated network name

        :type site: str
        :param site: abbreviated site name

        :type time: datetime.datetime
        :param time: acquisition time

        :type version: str
        :param version: processing version

        :return: Level 1 filename
        :rtype: str
        """

        time_string = time.strftime(TIME_FMT_L12A)
        return FilenameUtil._create_file_name(network, site, "RAD", time_string, version)

    @staticmethod
    def create_file_name_l1a_irr(network, site, time, version):
        """
        Return a valid file name for Hypernets Level 1a irradiance file

        :type network: str
        :param network: abbreviated network name

        :type site: str
        :param site: abbreviated site name

        :type time: datetime.datetime
        :param time: acquisition time

        :type version: str
        :param version: processing version

        :return: Level 1 filename
        :rtype: str
        """

        time_string = time.strftime(TIME_FMT_L12A)
        return FilenameUtil._create_file_name(network, site, "IRR", time_string, version)

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

        :return: Level 2a filename
        :rtype: str
        """

        time_string = time.strftime(TIME_FMT_L12A)
        return FilenameUtil._create_file_name(network, site, "REF", time_string, version)

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

        :return: Level 2b filename
        :rtype: str
        """

        time_string = time.strftime(TIME_FMT_L2B)
        return FilenameUtil._create_file_name(network, site, "REFD", time_string, version)

    @staticmethod
    def _create_file_name(network, site, ptype, time_string, version):
        return "_".join(["HYPERNETS", network.upper(), site.upper(), ptype, time_string, "v"+version]) + ".nc"


if __name__ == '__main__':
    pass
