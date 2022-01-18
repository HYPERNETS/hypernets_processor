"""
HypernetsWriter class
"""

from hypernets_processor.version import __version__
import os
import numpy as np

import xarray as xr

"""___Authorship___"""
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

    def write(
        self, ds, directory=None, overwrite=False, fmt=None, compression_level=None, remove_vars_strings=None
    ):
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
        :param fmt: (optional, required if self.context is None) format to write to, may be 'netCDF4' or 'csv'.
        overwrites directory determined from self.context

        :type compression_level: int
        :param compression_level: the file compression level if 'netCDF4' fmt, 0 - 9 (default is 5)
        """

        fmt = self.return_fmt(fmt)
        directory = self.return_directory(directory)

        if not os.path.exists(directory):
            os.makedirs(directory)

        path = os.path.join(directory, ds.attrs["product_name"]) + "." + fmt

        if os.path.isfile(path):
            if overwrite is True:
                os.remove(path)
            else:
                raise IOError("The file already exists: " + path)

        if remove_vars_strings is not None:
            for remove_var_string in remove_vars_strings.split(','):
                for var_name in ds.data_vars:
                    if remove_var_string.strip() in var_name:
                        ds = ds.drop_vars(var_name)

        #ds = HypernetsWriter.fill_ds(ds)
        if fmt == "nc":
            HypernetsWriter._write_netcdf(ds, path, compression_level=compression_level)

        elif fmt == "csv":
            HypernetsWriter._write_csv(ds, path)

        # Add dataset set to archive db if required
        self.archive_ds(ds, path)

    def return_fmt(self, fmt=None):
        """
        Return product fmt, with respect to context and specified value

        :type fmt: str
        :param fmt: (optional, required if self.context is None) format to write to, may be 'netCDF4' or 'csv'.
        overwrites directory determined from self.context

        :return: product format
        :rtype: str
        """

        if fmt is None:
            if self.context is None:
                raise ValueError(
                    "cannot write without either the self.context or fmt parameters specified"
                )
            fmt = self.context.get_config_value("product_format")

        if (fmt.lower() == "netcdf4") or (fmt.lower() == "netcdf"):
            return "nc"
        elif fmt.lower() == "csv":
            return "csv"
        else:
            raise NameError("Invalid fmt: " + fmt)

    def return_directory(self, directory=None):
        """
        Return product directory, with respect to context and specified value

        :type directory: str
        :param directory: (optional, required if self.context is None) directory to write to.
        overwrites directory determined from self.context

        :return: directory
        :rtype: str
        """

        if directory is None:
            if self.context is None:
                raise ValueError(
                    "cannot write without either the self.context or directory parameters specified"
                )

            directory = self.context.get_config_value("archive_directory")
            if "to_archive" in self.context.get_config_names():
                if self.context.get_config_value("to_archive"):
                    archive_directory = self.context.get_config_value(
                        "archive_directory"
                    )

                    site = self.context.get_config_value("site_id")
                    year = self.context.get_config_value("time").year
                    month = self.context.get_config_value("time").month
                    day = self.context.get_config_value("time").day
                    seq = self.context.get_config_value("sequence_name")

                    directory = os.path.join(
                        archive_directory, site, str(year), str('{:02d}'.format(month)), str('{:02d}'.format(day), seq)
                    )

        return directory

    def return_plot_directory(self, directory=None):
        """
        Return plots directory, with respect to context and specified value

        :type directory: str
        :param directory: (optional, required if self.context is None) directory to write to.
        overwrites directory determined from self.context

        :return: directory
        :rtype: str
        """

        return os.path.join(self.return_directory(directory), "plots")

    def return_image_directory(self, directory=None):
        """
        Return image directory, with respect to context and specified value

        :type directory: str
        :param directory: (optional, required if self.context is None) directory to write to.
        overwrites directory determined from self.context

        :return: directory
        :rtype: str
        """

        return os.path.join(self.return_directory(directory), "image")

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

        ds.to_netcdf(path, format="netCDF4", engine="netcdf4", encoding=encoding)

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
        with open(metadata_path, "w") as f:
            for meta_name in ds.attrs.keys():
                f.write(meta_name + ": " + ds.attrs[meta_name] + "\n")

    @staticmethod
    def fill_ds(ds):
        """
        Fill nan's in ds will fillValue

        :type ds: xarray.Dataset
        :param ds: dataset

        :return: filled data
        :rtype: xarray.Dataset
        """

        for variable in ds.variables.keys():
            idx = np.where(np.isnan(ds[variable].values))

            if np.sum(idx) > 0:
                ds[variable][idx] = ds[variable]._FillValue

        return ds

    def archive_ds(self, ds, path):
        """
        Add dataset to archive database

        :type ds: xarray.Dataset
        :param ds: dataset

        :type path: str
        :param path: file path
        """

        if self.context is not None:
            if (self.context.get_config_value("to_archive") is True) and (self.context.archive_db is not None):
                self.context.archive_db.archive_product(ds, path)

if __name__ == "__main__":
    pass
