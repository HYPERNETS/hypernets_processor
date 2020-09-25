"""
Tests for Calibrate class
"""

import unittest
from unittest.mock import MagicMock, patch, call
from hypernets_processor.version import __version__
from hypernets_processor.test.test_functions import setup_test_job_config, setup_test_processor_config
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import InterpolateL1c
from hypernets_processor.context import Context
from hypernets_processor import HypernetsDSBuilder
import os.path

import numpy as np

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
    n_series=len(arr[0])
    print(N_WAVELENGTHS,n_series)
    dsb = HypernetsDSBuilder(context)

    ds_l0_rad = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L0_RAD")
    ds_l0_irr = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L0_IRR")
    ds_l0_bla = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L0_BLA")

    ds_l1a_rad = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L_L1A_RAD")
    ds_l1a_irr = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"scan":n_series*10},
        "L_L1A_IRR")

    ds_l1b_rad = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"series":n_series},
        "L_L1B_RAD")
    ds_l1b_irr = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"series":n_series},
                                        "L_L1B_IRR")

    ds_l2a = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"series":n_series},"L_L2A")
    ds_l2a_avg = dsb.create_ds_template({"wavelength":N_WAVELENGTHS,"series":n_series},"L_L2A")

    ds_l0_rad["digital_number"].values = arr[5]
    ds_l0_rad["acquisition_time"].values = np.arange(30)
    ds_l0_rad["series_id"].values = np.repeat([1,2,3],10)
    ds_l0_irr["digital_number"].values = arr[6]
    ds_l0_irr["acquisition_time"].values = np.arange(30)
    ds_l0_irr["series_id"].values = np.repeat([1,2,3],10)
    ds_l0_bla["digital_number"].values = np.zeros(ds_l0_bla["digital_number"].values.shape)
    ds_l0_bla["acquisition_time"].values = np.arange(30)
    ds_l0_bla["series_id"].values =  np.repeat([1,2,3],10)

    ds_l1a_rad["radiance"].values=arr[5]
    ds_l1a_irr["irradiance"].values=arr[6]

    ds_l1b_rad["radiance"].values = arr[2]
    ds_l1b_irr["irradiance"].values = arr[3]

    ds_l2a["reflectance"].values = arr[4]
    ds_l2a_avg["reflectance"].values = arr[9]

    return ds_l0_rad,ds_l0_irr,ds_l0_bla,ds_l1a_rad,ds_l1a_irr,ds_l1b_rad,ds_l1b_irr,ds_l2a,ds_l2a_avg

class TestEndToEnd(unittest.TestCase):

    def test_end_to_end(self):
        this_directory_path = os.path.abspath(os.path.dirname(__file__))
        processor_config = os.path.join(this_directory_path,"../etc/processor.config")
        job_config = os.path.join(this_directory_path,"../etc/job.config")

        context = Context(processor_config=processor_config,job_config=job_config)
        context.set_config_value('network', 'L')
        context.set_config_value('measurement_function_calibrate', 'StandardMeasurementFunction')
        context.set_config_value('measurement_function_interpolate', 'LandNetworkInterpolationIrradianceLinear')
        context.set_config_value('measurement_function_surface_reflectance', 'LandNetworkProtocol')

        cal = Calibrate(context,MCsteps=100)
        intp = InterpolateL1c(context,MCsteps=1000)
        surf = SurfaceReflectance(context,MCsteps=1000)

        test_l0_rad,test_l0_irr,test_l0_bla,test_l1a_rad,test_l1a_irr,test_l1b_rad,test_l1b_irr,test_l2a,test_l2a_avg=setup_test_files(context)

        calibration_data={}
        calibration_data["gains"] = np.ones(len(test_l0_rad["wavelength"]))
        calibration_data["temp"] = 20*np.ones(len(test_l0_rad["wavelength"]))
        calibration_data["u_random_gains"] = 0.1*np.ones(len(test_l0_rad["wavelength"]))
        calibration_data["u_random_dark_signal"] = np.zeros((len(test_l0_rad["wavelength"])))
        calibration_data["u_random_temp"] = 1*np.ones(len(test_l0_rad["wavelength"]))
        calibration_data["u_systematic_gains"] = 0.05*np.ones(len(test_l0_rad["wavelength"]))
        calibration_data["u_systematic_dark_signal"] = np.zeros((len(test_l0_rad["wavelength"])))
        calibration_data["u_systematic_temp"] = 1*np.ones(len(test_l0_rad["wavelength"]))


        L1a_rad = cal.calibrate_l1a("radiance",test_l0_rad,test_l0_bla,calibration_data)
        print("flag",L1a_rad["quality_flag"].values)
        L1a_irr = cal.calibrate_l1a("irradiance",test_l0_irr,test_l0_bla,calibration_data)
        L1b_rad = cal.average_l1b("radiance",L1a_rad)
        L1b_irr = cal.average_l1b("irradiance",L1a_irr)
        L1c = intp.interpolate_l1c(L1b_rad,L1b_irr,)
        L2a = surf.process(L1c)

        np.testing.assert_allclose(test_l1b_rad["radiance"].values,L1b_rad["radiance"].values,rtol=0.12,equal_nan=True)
        np.testing.assert_allclose(np.nansum(test_l1b_rad["radiance"].values),np.nansum(L1b_rad["radiance"].values),rtol=0.05,equal_nan=True)

        #np.testing.assert_allclose(test_l1b_rad["radiance"].values,L1b_rad["radiance"].values,rtol=0.03,equal_nan=True)
        #np.testing.assert_allclose(L1b_irr["irradiance"].values,test_l1b_irr["irradiance"].values,rtol=0.04,equal_nan=True)
        np.testing.assert_allclose(test_l2a["reflectance"].values,L2a["reflectance"].values,rtol=0.19,equal_nan=True)
        np.testing.assert_allclose(np.nansum(test_l2a["reflectance"].values),np.nansum(L2a["reflectance"].values),rtol=0.05,equal_nan=True)
        np.testing.assert_allclose(np.nansum(test_l2a_avg["reflectance"].values),np.nansum(L2a["reflectance"].values),rtol=0.001,equal_nan=True)

if __name__ == '__main__':
    unittest.main()
