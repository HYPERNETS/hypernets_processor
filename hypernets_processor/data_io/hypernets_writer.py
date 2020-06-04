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
    def write(ds, path, overwrite=False, fmt='netCDF4', compression_level=None):
        """
        Write xarray dataset to file

        :type ds: xarray.Dataset
        :param ds: dataset

        :type path: str
        :param path: file path

        :type overwrite: bool
        :param overwrite: set to true to overwrite existing file

        :type fmt: str
        :param fmt: format to write to, may be 'netCDF4' (default) or 'csv'

        :type compression_level: int
        :param compression_level: the file compression level if 'netCDF4' fmt, 0 - 9 (default is 5)
        """

        if os.path.isfile(path):
            if overwrite is True:
                os.remove(path)
            else:
                raise IOError("The file already exists: " + path)

        if (fmt.lower() == 'netcdf4') or (fmt.lower() == 'netcdf'):
            HypernetsWriter._write_netcdf(ds, path, compression_level=compression_level)

        elif fmt == 'csv':
            HypernetsWriter._write_csv(ds, path)

        else:
            raise NameError("Invalid fmt: "+fmt)

    @staticmethod
    def _write_netcdf(ds, path, compression_level=None):
        """
        Write xarray dataset to file to netcdf

        :type ds: xarray.Dataset
        :param ds: dataset

        :type path: str
        :param path: file path

        :type compression_level: int
        :param compression_level: the file compression level if 'netCDF4' fmt, 0 - 9 (default is 5)
        """

        if compression_level is None:
            compression_level = 5

        comp = dict(zlib=True, complevel=compression_level)

        encoding = dict()
        for var_name in ds.data_vars:
            var_encoding = dict(comp)
            var_encoding.update(ds[var_name].encoding)
            encoding.update({var_name: var_encoding})

        ds.to_netcdf(path, format='netCDF4', engine='netcdf4', encoding=encoding)

    @staticmethod
    def _write_csv(ds, path):
        """
        Write xarray dataset to file to csv

        :type ds: xarray.Dataset
        :param ds: dataset

        :type path: str
        :param path: file path
        """

        # write data variables (via pandas dataframe)
        ds.to_dataframe().to_csv(path)

        # write metadata
        metadata_path = os.path.splitext(path)[0] + "_meta.txt"
        with open(metadata_path, 'w') as f:
            for meta_name in ds.attrs.keys():
                f.write(meta_name + ": " + ds.attrs[meta_name] + "\n")


if __name__ == '__main__':
    pass
