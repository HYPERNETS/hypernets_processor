"""
Data template class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates

import numpy as np
import os
import glob
import punpy

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "27/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"




class CalibrationConverter:
    def __init__(self,context):
        self.context=context
        self.templ = DataTemplates(context)

    def prepare_calibration_data(self,measurandstring,swir=False):
        hypstar = self.context.get_config_value("hypstar_cal_number")
        directory = self.context.get_config_value("calibration_directory")
        caldates = [os.path.basename(path) for path in glob.glob(
            os.path.join(directory,"hypstar_"+str(hypstar)+"/radiometric/*"))]
        caldate = caldates[-1]
        for f in glob.glob(os.path.join(directory,
                                        "hypstar_"+str(hypstar)+"\\radiometric\\"+str(
                                            caldate)+"\\hypstar_"+str(
                                            hypstar)+"_nonlin_corr_coefs_*.dat")):
            non_linear_cals = np.genfromtxt(f)

        if swir:
            sensortag = "swir"
        else:
            sensortag = "vnir"

        if measurandstring == "radiance":
            for f in glob.glob(os.path.join(directory,
                                            "hypstar_"+str(hypstar)+"/radiometric/"+str(
                                                caldate)+"/hypstar_"+str(
                                                hypstar)+"_radcal_L_*_%s.dat"%(
                                            sensortag))):
                gains = np.genfromtxt(f)
        else:
            for f in glob.glob(os.path.join(directory,
                                            "hypstar_"+str(hypstar)+"/radiometric/"+str(
                                                caldate)+"/hypstar_"+str(
                                                hypstar)+"_radcal_E_*_%s.dat"%(
                                            sensortag))):
                gains = np.genfromtxt(f)

        wavs = gains[:,1]
        calibration_data = self.templ.calibration_dataset(wavs,non_linear_cals[:,0])

        calibration_data["wavpix"].values = gains[:,0]
        calibration_data["gains"].values = gains[:,2]
        #calibration_data["u_random_gains"].values = None
        #calibration_data["corr_random_gains"].values = None

        calibration_data["u_systematic_indep_gains"].values = gains[:,2]*(
                    gains[:,6]**2+gains[:,7]**2+gains[:,8]**2+gains[:,9]**2+
                    gains[:,10]**2+gains[:,11]**2+gains[:,12]**2+gains[:,13]**2+
                    gains[:,14]**2+gains[:,15]**2+gains[:,16]**2+gains[:,17]**2+
                    gains[:,19]**2)**0.5/100

        cov_diag = punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),
                                             gains[:,2]*(gains[:,19])/100)

        cov_other = punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),
                    gains[:,2]*(gains[:,8]**2+gains[:,9]**2+gains[:,11]**2+
                                gains[:,16]**2+gains[:,17]**2)**0.5/100)

        cov_full = punpy.convert_corr_to_cov(
                    np.ones((len(gains[:,2]),len(gains[:,2]))),
                    gains[:,2]*(gains[:,7]**2+gains[:,10]**2+gains[:,12]**2+
                                gains[:,13]**2+gains[:,14]**2+gains[:,15]**2)**0.5/100)

        cov_filament = punpy.convert_corr_to_cov(
                    np.ones((len(gains[:,2]),len(gains[:,2]))),
                    gains[:,2]*(gains[:,6]**2)**0.5/100)

        calibration_data["corr_systematic_indep_gains"].values = \
            punpy.correlation_from_covariance(cov_diag+cov_other+cov_full+cov_filament)

        calibration_data["u_systematic_corr_rad_irr_gains"].values = gains[:,2]*(
                    gains[:,4]**2+gains[:,5]**2+gains[:,18]**2)**0.5/100

        cov_other = punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),gains[:,2]*(
                    gains[:,4]**2+gains[:,18]**2)**0.5/100)

        cov_filament = punpy.convert_corr_to_cov(
                    np.ones((len(gains[:,2]),len(gains[:,2]))),
                    gains[:,2]*(gains[:,5]**2)**0.5/100)

        calibration_data["corr_systematic_corr_rad_irr_gains"].values = \
            punpy.correlation_from_covariance(cov_other+cov_filament)

        calibration_data["non_linearity_coefficients"].values = non_linear_cals[:,0]
        #calibration_data["u_random_non_linearity_coefficients"].values = None
        #calibration_data["u_systematic_non_linearity_coefficients"].values = None

        return calibration_data