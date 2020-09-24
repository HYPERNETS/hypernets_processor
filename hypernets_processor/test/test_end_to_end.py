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
from hypernets_processor.test.test_functions import setup_test_context, teardown_test_context
from hypernets_processor import HypernetsDSBuilder

import xarray as xr

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "2/9/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

def setup_test_files(context,calibration_data):
    arr = np.load('../examples/test_radiance_and_irradiance_libradtran.npy')
    N_WAVELENGTHS=len(arr[1])
    n_sequence=len(arr[0])
    print(N_WAVELENGTHS,n_sequence)
    dsb = HypernetsDSBuilder(context)

    ds_l0_rad = dsb.create_ds_template(
        {"wavelength":N_WAVELENGTHS,"scan":n_sequence*10},"L0_RAD")
    ds_l0_irr = dsb.create_ds_template(
        {"wavelength":N_WAVELENGTHS,"scan":n_sequence*10},"L0_IRR")
    ds_l0_bla = dsb.create_ds_template(
        {"wavelength":N_WAVELENGTHS,"scan":n_sequence*10},"L0_BLA")

    ds_l0_rad["digital_number"].values=arr[5]
    ds_l0_irr["digital_number"].values=arr[6]
    ds_l0_bla["digital_number"].values=np.ones(["digital_number"].values.shape)

    return ds_l0_rad,ds_l0_irr,ds_l0_bla

class TestCalibrate(unittest.TestCase):

    def test_here(self):
        self.assertEqual(1,1)

#
    def test_end_to_end(self):
        context = setup_test_context()
        cal=Calibrate(context,MCsteps=100)
        intp = InterpolateL1c(context,MCsteps=1000)
        surf = SurfaceReflectance(context,MCsteps=1000)

        calibration_data={}
        calibration_data["gains"] = np.ones(len(ds_rad["wavelength"]))
        calibration_data["temp"] = 20*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_random_gains"] = 0.1*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_random_dark_signal"] = np.zeros((len(ds_rad["wavelength"])))
        calibration_data["u_random_temp"] = 1*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_systematic_gains"] = 0.05*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_systematic_dark_signal"] = np.zeros((len(ds_rad["wavelength"])))
        calibration_data["u_systematic_temp"] = 1*np.ones(len(ds_rad["wavelength"]))

        test_l0_rad,test_l0_irr,test_l0_bla,test_l1a_rad,test_l1a_irr,test_l1b_rad,test_l1b_irr,test_l2a=setup_test_files(context,calibration_data)

        L1a_rad = cal.calibrate_l1a("radiance",test_l0_rad,test_l0_bla,calibration_data,
                                    measurement_function='StandardMeasurementFunction')
        L1a_irr = cal.calibrate_l1a("irradiance",test_l0_irr,test_l0_bla,calibration_data,
                                    measurement_function='StandardMeasurementFunction')
        L1b_rad = cal.average_l1b("radiance",L1a_rad)
        L1b_irr = cal.average_l1b("irradiance",L1a_irr)
        L1c = intp.interpolate_l1c(L1b_rad,L1b_irr,
                                   "LandNetworkInterpolationIrradianceLinear")
        L2a = surf.process(L1c,"LandNetworkProtocol")

        self.assertEqual(test_l2a["reflectance"].values,L2a["reflectance"].values)


if __name__ == '__main__':
    unittest.main()
