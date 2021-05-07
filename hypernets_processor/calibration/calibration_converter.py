"""
Data template class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.test.test_functions import setup_test_context, teardown_test_context
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

import numpy as np
import os
import glob
import punpy
import xarray
from configparser import ConfigParser

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "27/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

version=0.1

class CalibrationConverter:
    def __init__(self,context):
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.path_ascii=os.path.join(dir_path,'data','calibration_files_ascii','HYPSTAR_cal')
        self.path_netcdf=os.path.join(dir_path,'hypernets_processor/calibration/calibration_files','HYPSTAR_cal')
        context.set_config_value("product_format","netcdf")
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context)
        self.context=context

    def read_calib_files(self, sequence_path):

        metadata = ConfigParser()
        if os.path.exists(os.path.join(sequence_path, "metadata.txt")):
            metadata.read(os.path.join(sequence_path, "metadata.txt"))
            # ------------------------------
            # global attributes + wavelengths -> need to check for swir
            # ----------------------------------
            globalattr = dict(metadata['Metadata'])
            if 'hypstar_sn' in (globalattr.keys()):
                instrument_id = int(globalattr['hypstar_sn'])
            elif 'sn_hypstar' in (globalattr.keys()):
                instrument_id = int(globalattr['sn_hypstar'])
            else:
                instrument_id = self.context.get_config_value("hypstar_cal_number")
                print("No SN set for hypstar instrument! using hypstar_cal_number from config file instead.")
        else:
            raise IOError(os.path.join(sequence_path, "metadata.txt") + " does not exist")


        hypstar = "hypstar_"+str(instrument_id) #self.context.get_config_value("hypstar_cal_number"))
        hypstar_path = os.path.join(self.path_netcdf,hypstar)
        name = "HYPERNETS_CAL_"+hypstar.upper()+"_RAD_v"+str(version)+".nc"

        if os.path.exists(os.path.join(hypstar_path, name)):
            calibration_data_rad = xarray.open_dataset(os.path.join(hypstar_path, name))
        else:
            raise IOError(os.path.join(hypstar_path, name) + " calibration file does not exist")

        name = "HYPERNETS_CAL_"+hypstar.upper()+"_IRR_v"+str(version)+".nc"

        if os.path.exists(os.path.join(hypstar_path, name)):
            calibration_data_irr = xarray.open_dataset(os.path.join(hypstar_path, name))
        else:
            raise IOError(os.path.join(hypstar_path, name) + " calibration file does not exist")

        calibration_data_times=calibration_data_rad["calibrationdates"].values
        nonlin_times=calibration_data_rad["nonlineardates"].values
        wav_times=calibration_data_rad["wavdates"].values
        calibration_data_rad=calibration_data_rad.sel(calibrationdates=
                                                       calibration_data_times[-1])
        calibration_data_rad = calibration_data_rad.sel(nonlineardates=
                                                         nonlin_times[-1])
        calibration_data_rad = calibration_data_rad.sel(wavdates=
                                                         wav_times[-1])
        calibration_data_irr=calibration_data_irr.sel(calibrationdates=
                                                       calibration_data_times[-1])
        calibration_data_irr=calibration_data_irr.sel(nonlineardates=
                                                       nonlin_times[-1])
        calibration_data_irr = calibration_data_irr.sel(wavdates=
                                                         wav_times[-1])
        if self.context.get_config_value("network") == "l":
            name = "HYPERNETS_CAL_"+hypstar.upper()+"_RAD_SWIR_v"+str(version)+".nc"
            if os.path.exists(os.path.join(hypstar_path, name)):
                calibration_data_rad_swir = xarray.open_dataset(os.path.join(hypstar_path, name))
            else:
                raise IOError(os.path.join(hypstar_path, name) + " calibration file does not exist")

            name = "HYPERNETS_CAL_"+hypstar.upper()+"_IRR_SWIR_v"+str(version)+".nc"
            if os.path.exists(os.path.join(hypstar_path, name)):
                calibration_data_irr_swir = xarray.open_dataset(os.path.join(hypstar_path, name))
            else:
                raise IOError(os.path.join(hypstar_path, name) + " calibration file does not exist")

            calibration_data_times = calibration_data_rad_swir["calibrationdates"].values
            nonlin_times = calibration_data_rad_swir["nonlineardates"].values
            calibration_data_rad_swir = calibration_data_rad_swir.sel(
                calibrationdates=calibration_data_times[-1])
            calibration_data_rad_swir = calibration_data_rad_swir.sel(
                nonlineardates=nonlin_times[-1])
            calibration_data_rad_swir = calibration_data_rad_swir.sel(
                wavdates=wav_times[-1])
            calibration_data_irr_swir = calibration_data_irr_swir.sel(
                calibrationdates=calibration_data_times[-1])
            calibration_data_irr_swir = calibration_data_irr_swir.sel(
                nonlineardates=nonlin_times[-1])
            calibration_data_irr_swir = calibration_data_irr_swir.sel(
                wavdates=wav_times[-1])

            return (calibration_data_rad,
                    calibration_data_irr,
                    calibration_data_rad_swir,
                    calibration_data_irr_swir)

        else:
            return calibration_data_rad, calibration_data_irr

    def convert_all_calibration_data(self):
        measurandstrings=["radiance","irradiance"]
        hypstars = [os.path.basename(path) for path in glob.glob(
            os.path.join(self.path_ascii,"hypstar_*"))]
        for hypstar in hypstars:
            print("processing "+hypstar)
            hypstar_path=os.path.join(self.path_netcdf,hypstar)
            if not os.path.exists(hypstar_path):
                os.makedirs(hypstar_path)

            for measurandstring in measurandstrings:
                if measurandstring=="radiance":
                    tag="_RAD_"
                else:
                    tag="_IRR_"

                calib_data = self.prepare_calibration_data(measurandstring,
                                                           hypstar=hypstar[8::])
                calib_data.attrs["product_name"] = "HYPERNETS_CAL_"+hypstar.upper()\
                                                   +tag+"v"+str(version)
                self.writer.write(calib_data,directory=hypstar_path,overwrite=True)
                if hypstar[8]=="2":
                    tag=tag+"SWIR_"
                    calib_data = self.prepare_calibration_data(measurandstring,
                                                               hypstar=hypstar[8::],
                                                               swir=True)
                    calib_data.attrs["product_name"] = "HYPERNETS_CAL_"+\
                                                hypstar.upper()+tag+"v"+str(version)
                    self.writer.write(calib_data,directory=hypstar_path,overwrite=True)


    def prepare_calibration_data(self,measurandstring,hypstar,swir=False):
        if swir:
            sensortag = "swir"
        else:
            sensortag = "vnir"

        directory = self.path_ascii
        caldatepaths = [os.path.basename(path) for path in glob.glob(
            os.path.join(directory,"hypstar_"+str(hypstar)+"/radiometric/*"))]
        nonlindates=[]
        caldates=[]

        for caldatepath in caldatepaths:
            caldate=caldatepath
            nonlinpath=glob.glob(os.path.join(directory,
                                   "hypstar_"+str(hypstar)+"\\radiometric\\"+str(
                                       caldatepath)+"\\hypstar_"+str(
                                       hypstar)+"_nonlin_corr_coefs_*.dat"))[0]
            if os.path.exists(nonlinpath):
                nonlindates=np.append(nonlindates,caldate)
                non_linear_cals = np.genfromtxt(nonlinpath)[:,0]

            if measurandstring == "radiance":
                calpath=glob.glob(os.path.join(directory,"hypstar_"+str(
                    hypstar)+"\\radiometric\\"+str(caldatepath)+"\\hypstar_"+str(
                    hypstar)+"_radcal_L_*_%s.dat"%(sensortag)))[0]

            else:
                calpath=glob.glob(os.path.join(directory,"hypstar_"+str(
                    hypstar)+"\\radiometric\\"+str(caldatepath)+"\\hypstar_"+str(
                    hypstar)+"_radcal_E_*_%s.dat"%(sensortag)))[0]

            if os.path.exists(calpath):
                caldates=np.append(caldates,caldate)
                gains = np.genfromtxt(calpath)
                wavs = gains[:,1]

        wavcaldatepaths = [os.path.basename(path) for path in glob.glob(
            os.path.join(directory,"hypstar_"+str(hypstar)+"/wavelength/*"))]
        wavcaldates = []

        for wavcaldatepath in wavcaldatepaths:
            wavcaldate = wavcaldatepath
            wavcalpath = glob.glob(os.path.join(directory,"hypstar_"+str(
                hypstar)+"\\wavelength\\"+str(wavcaldatepath)+"\\hypstar_"+str(
                hypstar)+"_wl_coefs_*.dat"))[0]
            if os.path.exists(wavcalpath):
                wavcaldates = np.append(wavcaldates,wavcaldate)
                wav_cals = np.genfromtxt(wavcalpath)[:,0]


        calibration_data = self.templ.calibration_dataset(wavs,non_linear_cals,wav_cals,
                                                    caldates,nonlindates,wavcaldates)
        i_nonlin=0
        for caldatepath in caldatepaths:
            nonlinpath = glob.glob(os.path.join(directory,"hypstar_"+str(
                hypstar)+"\\radiometric\\"+str(caldatepath)+"\\hypstar_"+str(
                hypstar)+"_nonlin_corr_coefs_*.dat"))[0]
            if os.path.exists(nonlinpath):
                non_linear_cals = np.genfromtxt(nonlinpath)[:,0]
                calibration_data["non_linearity_coefficients"].values[i_nonlin] =  non_linear_cals
                i_nonlin+=1

        i_wavcoef=0
        for wavcaldatepath in wavcaldatepaths:
            wavcaldate = wavcaldatepath
            wavcalpath = glob.glob(os.path.join(directory,"hypstar_"+str(
                hypstar)+"\\wavelength\\"+str(wavcaldatepath)+"\\hypstar_"+str(
                hypstar)+"_wl_coefs_*.dat"))[0]
            if os.path.exists(wavcalpath):
                wav_cals = np.genfromtxt(wavcalpath)
                if measurandstring == "radiance" and not swir:
                    wav_cals = wav_cals[:,0]
                if measurandstring == "irradiance" and not swir:
                    wav_cals = wav_cals[:,1]
                if measurandstring == "radiance" and swir:
                    wav_cals=wav_cals[:,2]
                if measurandstring == "irradiance" and swir:
                    wav_cals=wav_cals[:,3]
                calibration_data["wavelength_coefficients"].values[
                    i_wavcoef] = wav_cals
                i_wavcoef += 1

        i_cal=0
        for caldatepath in caldatepaths:
            if measurandstring == "radiance":
                calpath = glob.glob(os.path.join(directory,"hypstar_"+str(
                    hypstar)+"\\radiometric\\"+str(caldatepath)+"\\hypstar_"+str(
                    hypstar)+"_radcal_L_*_%s.dat"%(sensortag)))[0]
            else:
                calpath = glob.glob(os.path.join(directory,"hypstar_"+str(
                    hypstar)+"\\radiometric\\"+str(caldatepath)+"\\hypstar_"+str(
                    hypstar)+"_radcal_E_*_%s.dat"%(sensortag)))[0]

            if os.path.exists(calpath):
                caldates = np.append(caldates,caldate)
                gains = np.genfromtxt(calpath)

                calibration_data["wavelengths"].values[i_cal] = gains[:,1]
                calibration_data["wavpix"].values[i_cal] = gains[:,0]
                calibration_data["gains"].values[i_cal] = gains[:,2]
                #calibration_data["u_rel_random_gains"].values = None
                #calibration_data["corr_random_gains"].values = None
    
                calibration_data["u_rel_systematic_indep_gains"].values[i_cal] = (
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
    
                calibration_data["corr_systematic_indep_gains"].values[i_cal] = \
                    punpy.correlation_from_covariance(cov_diag+cov_other+cov_full+cov_filament)
    
                calibration_data["u_rel_systematic_corr_rad_irr_gains"].values[i_cal] = (
                            gains[:,4]**2+gains[:,5]**2+gains[:,18]**2)**0.5/100
    
                cov_other = punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),gains[:,2]*(
                            gains[:,4]**2+gains[:,18]**2)**0.5/100)
    
                cov_filament = punpy.convert_corr_to_cov(
                            np.ones((len(gains[:,2]),len(gains[:,2]))),
                            gains[:,2]*(gains[:,5]**2)**0.5/100)
    
                calibration_data["corr_systematic_corr_rad_irr_gains"].values[i_cal] = \
                    punpy.correlation_from_covariance(cov_other+cov_filament)
                i_cal+=1

        return calibration_data

if __name__ == '__main__':
    context = setup_test_context()
    calcov=CalibrationConverter(context)
    calcov.convert_all_calibration_data()
    teardown_test_context(context)