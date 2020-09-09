"""
Tests for Calibrate class
"""

import unittest
from unittest.mock import MagicMock, patch, call
from hypernets_processor.version import __version__
from hypernets_processor.test.test_functions import setup_test_job_config, setup_test_processor_config
from hypernets_processor.calibration.calibrate import Calibrate

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "2/9/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class TestCalibrate(unittest.TestCase):

    def test_calibrate_l1a(self,measurandstring,dataset_l0,dataset_l0_bla,calibration_data,
                      measurement_function='StandardMeasurementFunction'):



    def test_average_l1b(self,measurandstring,dataset_l1a):

    def test_calc_mean_masked(self,dataset,var,rand_unc=False,corr=False):

    def test_find_nearest_black(self,dataset,acq_time,int_time):

    def test_find_input(self,variables,dataset,datasetbla,ancillary_dataset):

    def test_find_u_random_input(self,variables,dataset,datasetbla,ancillary_dataset,masked_avg=False):


    def test_find_u_systematic_input(self,variables,dataset,datasetbla,ancillary_dataset,masked_avg=False):


    def test_preprocess_l0(self,datasetl0,datasetl1a):

    def test_clip_and_mask(self,dataset,k_unc=2):


    def test_sigma_clip(self,values,tolerance=0.001,median=True,sigma_thresh=3.0):


    def test_l1a_template_from_l0_dataset(self,measurandstring,datasetl0):


    def test_process_measurement_function(self,measurandstring,dataset,measurement_function,input_quantities,
                                     u_random_input_quantities,u_systematic_input_quantities):


if __name__ == '__main__':
    unittest.main()
