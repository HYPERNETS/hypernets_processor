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

    def __init__(self, context=None):
        self.context = context

    def write(self, ds, directory=None, overwrite=False, fmt='netcdf4', compression_level=None):
        """
        Write xarray dataset to file

        :type ds: xarray.Dataset
        :param ds: dataset

        :type directory: str
        :param directory: (optional, required if self.context is None) directory to write to.
        overwrites directory determined from self.context

        :type overwrite: bool
        :param overwrite: set to true to overwrite existing file

        :type fmt: str
        :param fmt: format to write to, may be 'netCDF4' (default) or 'csv'

        :type compression_level: int
        :param compression_level: the file compression level if 'netCDF4' fmt, 0 - 9 (default is 5)
        """

        if (fmt.lower() == 'netcdf4') or (fmt.lower() == 'netcdf'):
            fmt = "nc"

        if directory is None:
            if self.context is None:
                raise ValueError("cannot write without either the self.context or directory parameters specified")

            directory = os.path.join(self.context.archive_directory, self.context.site, str(self.context.time.year),
                                     str(self.context.time.month), str(self.context.time.day))

        path = os.path.join(directory, ds.attrs["product_name"]) + "." + fmt

        if os.path.isfile(path):
            if overwrite is True:
                os.remove(path)
            else:
                raise IOError("The file already exists: " + path)

        if fmt == 'nc':
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
