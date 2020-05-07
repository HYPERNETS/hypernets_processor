"""
HypernetsWriter class
"""

from hypernets_processor.version import __version__
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class HypernetsWriter:
    """
    Class to write Hypernets output files
    """

    @staticmethod
    def write(dataset, path, overwrite=False, fmt='netCDF4', compression_level=None):
        """
        Write xarray dataset to file

        :type dataset: xarray.Dataset
        :param dataset: dataset

        :type path: str
        :param path: file path

        :type overwrite: bool
        :param overwrite: set to true to overwrite existing file

        :type fmt: str
        :param fmt: format to write to, may be 'netCDF4' or 'csv'

        :type compression_level: int
        :param compression_level: the file compression level if 'netCDF4' fmt, 0 - 9 (default is 5)
        """

        if (fmt.lower() == 'netcdf4') or (fmt.lower() == 'netcdf'):
            if os.path.isfile(path):
                if overwrite is True:
                    os.remove(path)
                else:
                    raise IOError("The file already exists: " + path)

            if compression_level is None:
                compression_level = 5

            comp = dict(zlib=True, complevel=compression_level)

            encoding = dict()
            for var_name in dataset.data_vars:
                var_encoding = dict(comp)
                var_encoding.update(dataset[var_name].encoding)
                encoding.update({var_name: var_encoding})

            dataset.to_netcdf(path, format='netCDF4', engine='netcdf4', encoding=encoding)

        elif fmt == 'csv':
            # todo - Add csv write format to write for debug mode
            pass

        else:
            raise NameError("Invalid fmt: "+fmt)


if __name__ == '__main__':
    pass
