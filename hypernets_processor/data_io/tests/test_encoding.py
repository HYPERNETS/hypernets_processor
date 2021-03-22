"""
Tests for HypernetsReader class
"""

import unittest
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.version import __version__
import os
import glob
import xarray as xr
import numpy as np

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__status__ = "Development"

this_directory = os.path.dirname(__file__)
path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(this_directory))),'examples','test_encoding.nc')

class TestEncoding(unittest.TestCase):
    def test_encoding(self):
        wavs=np.arange(300,1907,1)
        data=np.random.random((1607,1607)).astype('float')
        foo = xr.Dataset({"foo":(["wavelength","wavelength"],data)},
            coords={"wavelength":(["wavelength"],wavs),},)
        print(foo["foo"])
        print(path)
        encoding = {'foo':{'dtype':'int8','scale_factor':0.01,'_FillValue':-9999}}
        foo.to_netcdf(path,format="netCDF4",engine="netcdf4",encoding=encoding)
        foo2=xr.open_dataset(path)
        for var_name in foo2.data_vars:
            np.testing.assert_allclose(foo[var_name].values,foo2[var_name].values,atol=0.01)



if __name__ == '__main__':
    unittest.main()
