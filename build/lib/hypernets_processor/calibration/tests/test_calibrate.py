"""
Tests for Calibrate class
"""

import unittest
from unittest.mock import MagicMock, patch, call
from hypernets_processor.version import __version__
from hypernets_processor.test.test_functions import (
    setup_test_job_config,
    setup_test_processor_config,
)
from hypernets_processor.calibration.calibrate import Calibrate
import xarray as xr
import numpy as np

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "2/9/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


def setup_test_files():
    ds_irr = xr.open_dataset("../examples/HYPERNETS_W_VFFR_L0_IRR_202008211547_v0.0.nc")
    ds_rad = xr.open_dataset("../examples/HYPERNETS_W_VFFR_L0_RAD_202008211547_v0.0.nc")
    ds_bla = xr.open_dataset("../examples/HYPERNETS_W_VFFR_L0_BLA_202008211547_v0.0.nc")

    ds_rad["digital_number"].values = np.ones(["digital_number"].values.shape)
    ds_irr["digital_number"].values = np.ones(["digital_number"].values.shape)
    ds_bla["digital_number"].values = np.ones(["digital_number"].values.shape)


class TestCalibrate(unittest.TestCase):
    def test_here(self):
        self.assertEqual(1 + 1, 2)


#
# def test_calibrate_l1a(self,measurandstring,dataset_l0,dataset_l0_bla,calibration_data,
#                   measurement_function='StandardMeasurementFunction'):
#     self.assertEqual(1,1)
#
#
# def test_average_l1b(self,measurandstring,dataset_l1a):
#     self.assertEqual(1,1)
#
# def test_calc_mean_masked(self,dataset,var,rand_unc=False,corr=False):
#     self.assertEqual(1,1)
#
# def test_find_nearest_black(self,dataset,acq_time,int_time):
#     self.assertEqual(1,1)
#
# def test_find_input(self,variables,dataset,datasetbla,ancillary_dataset):
#     self.assertEqual(1,1)
#
# def test_find_u_random_input(self,variables,dataset,datasetbla,ancillary_dataset,masked_avg=False):
#     self.assertEqual(1,1)
#
# def test_find_u_systematic_input(self,variables,dataset,datasetbla,ancillary_dataset,masked_avg=False):
#     self.assertEqual(1,1)
#
# def test_preprocess_l0(self,datasetl0,datasetl1a):
#     self.assertEqual(1,1)
#
# def test_clip_and_mask(self,dataset,k_unc=2):
#     self.assertEqual(1,1)
#
# def test_sigma_clip(self,values,tolerance=0.001,median=True,sigma_thresh=3.0):
#     self.assertEqual(1,1)
#
# def test_l1a_template_from_l0_dataset(self,measurandstring,datasetl0):
#     self.assertEqual(1,1)
#
#
# def test_process_measurement_function(self,measurandstring,dataset,measurement_function,input_quantities,
#                                  u_random_input_quantities,u_systematic_input_quantities):
#     self.assertEqual(1,1)
#

if __name__ == "__main__":
    pass
