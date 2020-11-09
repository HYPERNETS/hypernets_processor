"""
Tests for Calibrate class
"""

import unittest
from unittest.mock import MagicMock, patch, call
from hypernets_processor.version import __version__
from hypernets_processor.data_utils.average import Average
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.context import Context
from hypernets_processor import HypernetsDSBuilder
from hypernets_processor.test.test_functions import setup_test_context, teardown_test_context

import os.path
import matplotlib.pyplot as plt
import numpy as np
import random
import string
import shutil

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "2/9/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

def setup_test_files(context):
    arr = np.load(r"C:\Users\pdv\PycharmProjects\hypernets_processor\examples\test_radiance_and_irradiance_libradtran.npy",allow_pickle=True)
    N_WAVELENGTHS=len(arr[1])
    N_WAVELENGTHS_2=len(arr[12])
    n_series=len(arr[0])
    print(N_WAVELENGTHS,n_series)
    dsb = HypernetsDSBuilder(context)

    ds_l0_rad = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L0_RAD")
    ds_l0_irr = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L0_IRR")
    ds_l0_bla = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L0_BLA")

    ds_l1a_rad = dsb.create_ds_template({"wavelength":N_WAVELENGTHS_2,"scan":n_series*10},
        "L_L1A_RAD")
    ds_l1a_irr = dsb.create_ds_template({"wavelength":N_WAVELENGTHS_2,"scan":n_series*10},
        "L_L1A_IRR")

    ds_l1b_rad = dsb.create_ds_template({"wavelength":N_WAVELENGTHS_2,"series":n_series},
        "L_L1B_RAD")
    ds_l1b_irr = dsb.create_ds_template({"wavelength":N_WAVELENGTHS_2,"series":n_series},
                                        "L_L1B_IRR")

    ds_l2a = dsb.create_ds_template({"wavelength":N_WAVELENGTHS_2,"series":n_series},"L_L2A")
    ds_l2a_avg = dsb.create_ds_template({"wavelength":N_WAVELENGTHS_2,"series":n_series},"L_L2A")

    ds_l0_rad = ds_l0_rad.assign_coords(wavelength=arr[1])
    ds_l0_irr = ds_l0_irr.assign_coords(wavelength=arr[1])
    ds_l0_bla = ds_l0_bla.assign_coords(wavelength=arr[1])
    ds_l1a_rad = ds_l1a_rad.assign_coords(wavelength=arr[12])
    ds_l1a_irr = ds_l1a_irr.assign_coords(wavelength=arr[12])
    ds_l1b_rad = ds_l1b_rad.assign_coords(wavelength=arr[12])
    ds_l1b_irr = ds_l1b_irr.assign_coords(wavelength=arr[12])
    ds_l2a = ds_l2a.assign_coords(wavelength=arr[12])

    ds_l0_rad["digital_number"].values = arr[7]/1000
    ds_l0_rad["acquisition_time"].values = np.arange(30)
    ds_l0_rad["series_id"].values = np.repeat([1,2,3],10)
    ds_l0_rad["integration_time"].values = np.repeat(1024,30)
    ds_l0_irr["digital_number"].values = arr[8]/1000
    ds_l0_irr["acquisition_time"].values = np.arange(30)
    ds_l0_irr["series_id"].values = np.repeat([1,2,3],10)
    ds_l0_irr["integration_time"].values = np.repeat(1024,30)
    ds_l0_bla["digital_number"].values = np.zeros(ds_l0_bla["digital_number"].values.shape)
    ds_l0_bla["acquisition_time"].values = np.arange(30)
    ds_l0_bla["series_id"].values =  np.repeat([1,2,3],10)
    ds_l0_bla["integration_time"].values = np.repeat(1024,30)


    ds_l1a_rad["radiance"].values=arr[5]/1000
    ds_l1a_irr["irradiance"].values=arr[6]/1000

    ds_l1b_rad["radiance"].values = arr[2]/1000
    ds_l1b_irr["irradiance"].values = arr[3]/1000

    ds_l2a["reflectance"].values = arr[4]
    ds_l2a_avg["reflectance"].values = arr[11]

    return ds_l0_rad,ds_l0_irr,ds_l0_bla,ds_l1a_rad,ds_l1a_irr,ds_l1b_rad,ds_l1b_irr,ds_l2a,ds_l2a_avg

class TestEndToEnd(unittest.TestCase):

    def test_end_to_end(self):
        this_directory_path = os.path.abspath(os.path.dirname(__file__))
        this_directory_path = os.path.join(this_directory_path,"..\\")

        tmpdir = "tmp_"+"".join(random.choices(string.ascii_lowercase,k=6))
        #context = setup_test_context()

        context = setup_test_context(
        raw_data_directory = os.path.join(tmpdir,"data"),
        archive_directory = os.path.join(tmpdir,"out"),
        metadata_db_url = "sqlite:///"+tmpdir+"/metadata.db",
        anomaly_db_url = "sqlite:///"+tmpdir+"/anomoly.db",
        archive_db_url = "sqlite:///"+tmpdir+"/archive.db",
        create_directories = True,
        create_dbs = False )

        context.set_config_value('network', 'l')
        context.set_config_value('measurement_function_calibrate', 'StandardMeasurementFunction')
        context.set_config_value('measurement_function_interpolate', 'LandNetworkInterpolationIrradianceLinear')
        context.set_config_value('measurement_function_surface_reflectance', 'LandNetworkProtocol')
        context.set_config_value("processor_directory",this_directory_path)
        context.set_config_value("calibration_directory",os.path.join(this_directory_path,"..\\calibration_files\\HYPSTAR_cal\\"))
        context.set_config_value("archive_directory", os.path.join(tmpdir,"out"))

        context.set_config_value('version','0.1')
        context.set_config_value('site_abbr','test')
        context.set_config_value('product_format','netcdf4')
        context.set_config_value('hypstar_cal_number','220241')
        context.set_config_value('cal_date','200728')
        context.set_config_value('outliers',7)

        context.set_config_value('write_l2a',True)
        context.set_config_value('write_l1a',True)
        context.set_config_value('write_l1b',True)
        context.set_config_value('plot_l2a',True)
        context.set_config_value('plot_l1a',True)
        context.set_config_value('plot_l1b',True)
        context.set_config_value('plot_diff',True)
        context.set_config_value('plotting_directory',os.path.join(tmpdir,"out/plots/"))
        context.set_config_value('plotting_format',"png")

        cal = Calibrate(context,MCsteps=100)
        avg = Average(context)
        intp = Interpolate(context,MCsteps=1000)
        surf = SurfaceReflectance(context,MCsteps=1000)

        test_l0_rad,test_l0_irr,test_l0_bla,test_l1a_rad,test_l1a_irr,test_l1b_rad,test_l1b_irr,test_l2a,test_l2a_avg=setup_test_files(context)

        L1a_rad = cal.calibrate_l1a("radiance",test_l0_rad,test_l0_bla)
        L1a_irr = cal.calibrate_l1a("irradiance",test_l0_irr,test_l0_bla)
        L1b_rad = avg.average_l1b("radiance",L1a_rad)
        L1b_irr = avg.average_l1b("irradiance",L1a_irr)
        L1c = intp.interpolate_l1c(L1b_rad,L1b_irr)
        L2a = surf.process_l2(L1c)
        # np.testing.assert_allclose(test_l1a_rad["radiance"].values[:,0],L1a_rad["radiance"].values[:,0],rtol=0.12,equal_nan=True)
        # np.testing.assert_allclose(test_l1b_rad["radiance"].values,L1b_rad["radiance"].values,rtol=0.12,equal_nan=True)
        #np.testing.assert_allclose(np.nansum(test_l1b_rad["radiance"].values),np.nansum(L1b_rad["radiance"].values),rtol=0.05,equal_nan=True)

        #np.testing.assert_allclose(test_l1b_rad["radiance"].values,L1b_rad["radiance"].values,rtol=0.03,equal_nan=True)
        #np.testing.assert_allclose(L1b_irr["irradiance"].values,test_l1b_irr["irradiance"].values,rtol=0.04,equal_nan=True)
        np.testing.assert_allclose(test_l2a["reflectance"].values,L2a["reflectance"].values,rtol=0.19,equal_nan=True)
        np.testing.assert_allclose(np.nansum(test_l2a["reflectance"].values),np.nansum(L2a["reflectance"].values),rtol=0.05,equal_nan=True)
        np.testing.assert_allclose(np.nansum(test_l2a_avg["reflectance"].values),np.nansum(L2a["reflectance"].values),rtol=0.001,equal_nan=True)
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    unittest.main()
