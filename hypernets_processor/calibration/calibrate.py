"""
Calibration class
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import \
    MeasurementFunctionFactory
import punpy
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.plotting.plotting import Plotting
import numpy as np
import os
import glob
import warnings


'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

class Calibrate:
    def __init__(self, context, MCsteps=1000, parallel_cores=0):
        self._measurement_function_factory = MeasurementFunctionFactory()
        self.prop = punpy.MCPropagation(MCsteps, parallel_cores=parallel_cores)
        self.templ = DataTemplates(context=context)
        self.writer = HypernetsWriter(context)
        self.plot = Plotting(context)
        self.context = context

    def calibrate_l1a(self, measurandstring, dataset_l0, dataset_l0_bla, swir=False):
        if measurandstring != "radiance" and measurandstring != "irradiance":
            self.context.logger.error("the measurandstring needs to be either 'radiance' or 'irradiance")
            exit()


        if self.context.get_config_value("plot_l0"):
            if swir:
                dataset_l0.attrs['product_name'] = dataset_l0.attrs[
                                                        'product_name']+"_SWIR"
            self.plot.plot_scans_in_series("digital_number",dataset_l0)

        calibrate_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate"))
        input_vars = calibrate_function.get_argument_names()

        calibration_data, wavids = self.prepare_calibration_data(measurandstring,swir)
        dataset_l0,dataset_l0_bla = self.preprocess_l0(dataset_l0,dataset_l0_bla,wavids)
        dataset_l1a = self.templ.l1a_template_from_l0_dataset(measurandstring, dataset_l0)
        input_qty = self.find_input(input_vars, dataset_l0, dataset_l0_bla, calibration_data)
        u_random_input_qty = self.find_u_random_input(input_vars, dataset_l0, calibration_data)
        u_systematic_input_qty_indep,u_systematic_input_qty_corr,\
        cov_systematic_input_qty_indep,cov_systematic_input_qty_corr = self.find_u_systematic_input(input_vars, dataset_l0, calibration_data)

        dataset_l1a = self.process_measurement_function(measurandstring, dataset_l1a,
                                                        calibrate_function.function,
                                                        input_qty,
                                                        u_random_input_qty,
                                                        u_systematic_input_qty_indep,
                                                        u_systematic_input_qty_corr,
                                                        cov_systematic_input_qty_indep,
                                                        cov_systematic_input_qty_corr)
        if swir:
            dataset_l1a.attrs['product_name']= dataset_l1a.attrs['product_name']+"_SWIR"

        if self.context.get_config_value("write_l1a"):
            self.writer.write(dataset_l1a, overwrite=True)

        if self.context.get_config_value("plot_l1a"):
            self.plot.plot_scans_in_series(measurandstring,dataset_l1a)

        if self.context.get_config_value("plot_l1a_diff"):
            self.plot.plot_diff_scans(measurandstring,dataset_l1a)

        return dataset_l1a

    def prepare_calibration_data(self,measurandstring, swir=False):
        hypstar=self.context.get_config_value("hypstar_cal_number")
        directory=self.context.get_config_value("calibration_directory")
        caldates=[os.path.basename(path) for path in glob.glob
        (os.path.join(directory,"hypstar_"+str(hypstar)+"/radiometric/*"))]
        caldate=caldates[0]
        for f in glob.glob(os.path.join(directory,
                            "hypstar_"+str(hypstar)+"\\radiometric\\"+str(caldate)+
                            "\\hypstar_"+str(hypstar)+"_nonlin_corr_coefs_*.dat")):
            non_linear_cals = np.genfromtxt(f)

        if swir:
            sensortag="swir"
        else:
            sensortag="vnir"

        if measurandstring == "radiance":
            for f in glob.glob(os.path.join(directory,
                                            "hypstar_"+str(hypstar)+"/radiometric/"+str(
                                                caldate)+"/hypstar_"+str(
                                                hypstar)+"_radcal_L_*_%s.dat"%(sensortag))):
                gains = np.genfromtxt(f)
                wavids=[int(gains[0,0])-1,int(gains[-1,0])]
        else:
            for f in glob.glob(os.path.join(directory,
                                            "hypstar_"+str(hypstar)+"/radiometric/"+str(
                                                caldate)+"/hypstar_"+str(
                                                hypstar)+"_radcal_E_*_%s.dat"%(sensortag))):
                gains = np.genfromtxt(f)
                wavids=[int(gains[0,0])-1,int(gains[-1,0])]


        calibration_data = {}
        calibration_data["gains"] = gains[:,2]
        calibration_data["u_random_gains"] = None
        calibration_data["u_systematic_indep_gains"] = gains[:,2]*(gains[:,6]**2+
                gains[:,7]**2+gains[:,8]**2+gains[:,9]**2+gains[:,10]**2+gains[:,11]**2+
                gains[:,12]**2+gains[:,13]**2+gains[:,14]**2+gains[:,15]**2+
                gains[:,16]**2+gains[:,17]**2+gains[:,19]**2)**0.5/100

        cov_diag=punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),
                gains[:,2]*(gains[:,19])/100)

        cov_other=punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),
                gains[:,2]*(gains[:,8]**2+gains[:,9]**2+gains[:,11]**2+gains[:,16]**2+gains[:,17]**2)**0.5/100)

        cov_full=punpy.convert_corr_to_cov(np.ones((len(gains[:,2]),len(gains[:,2]))),
                gains[:,2]*(gains[:,7]**2+gains[:,10]**2+gains[:,12]**2+gains[:,13]**2+gains[:,14]**2+gains[:,15]**2)**0.5/100)

        cov_filament=punpy.convert_corr_to_cov(np.ones((len(gains[:,2]),len(gains[:,2]))),
                gains[:,2]*(gains[:,6]**2)**0.5/100)

        calibration_data["cov_systematic_indep_gains"] = cov_diag + cov_other + cov_full + cov_filament


        calibration_data["u_systematic_corr_rad_irr_gains"] = gains[:,2]*(gains[:,4]**2+
                gains[:,5]**2+gains[:,18]**2)**0.5/100

        cov_other = punpy.convert_corr_to_cov(np.eye(len(gains[:,2])),gains[:,2]*(
                gains[:,4]**2+gains[:,18]**2)**0.5/100)

        cov_filament = punpy.convert_corr_to_cov(
            np.ones((len(gains[:,2]),len(gains[:,2]))),
            gains[:,2]*(gains[:,5]**2)**0.5/100)

        calibration_data["cov_systematic_corr_rad_irr_gains"] = cov_other + cov_filament

        calibration_data["non_linearity_coefficients"] = non_linear_cals[:,0]
        calibration_data["u_random_non_linearity_coefficients"] = None
        calibration_data["u_systematic_non_linearity_coefficients"] = None

        return calibration_data, wavids

    def find_nearest_black(self, dataset, acq_time, int_time):
        ids = np.where(
            (abs(dataset['acquisition_time'] - acq_time) == min(abs(dataset['acquisition_time'] - acq_time))) & (
                        dataset['integration_time'] == int_time)) #todo check if interation time alwasy has to be same
        return np.mean(dataset["digital_number"].values[:, ids], axis=2)[:, 0]

    def find_input(self, variables, dataset, datasetbla, ancillary_dataset):
        """
        returns a list of the data for a given list of input variables

        :param variables:
        :type variables:
        :param dataset:
        :type dataset:
        :return:
        :rtype:
        """
        inputs = []
        for var in variables:
            if var == "dark_signal":
                dark_signals = []
                acqui = dataset['acquisition_time'].values
                inttimes = dataset['integration_time'].values
                for i in range(len(acqui)):
                    dark_signals.append(self.find_nearest_black(datasetbla, acqui[i], inttimes[i]))
                inputs.append(np.array(dark_signals).T)
            else:
                try:
                    inputs.append(dataset[var].values)
                except:
                    inputs.append(ancillary_dataset[var])
        return inputs

    def find_u_random_input(self, variables, dataset, ancillary_dataset):
        """
        returns a list of the random uncertainties on the data for a given list of input variables

        :param variables:
        :type variables:
        :param dataset:
        :type dataset:
        :return:
        :rtype:
        """
        inputs = []
        for var in variables:
            try:
                inputs.append(dataset["u_random_" + var].values)
            except:
                try:
                    inputs.append(ancillary_dataset["u_random_" + var])
                except:
                    inputs.append(None)
        return inputs

    def find_u_systematic_input(self, variables, dataset, ancillary_dataset):
        """
        returns a list of the systematic uncertainties on the data for a given list of input variables

        :param variables:
        :type variables:
        :param dataset:
        :type dataset:
        :return:
        :rtype:
        """
        inputs_indep = []
        covs_indep = []
        inputs_corr = []
        covs_corr = []
        for var in variables:
            try:
                inputs_indep.append(dataset["u_systematic_" + var].values)
                covs_indep.append(punpy.convert_corr_to_cov(dataset["corr_systematic_" + var].values,dataset["u_systematic_" + var].values))
            except:
                try:
                    inputs_indep.append(ancillary_dataset["u_systematic_indep_"+var])
                    covs_indep.append(ancillary_dataset["cov_systematic_indep_"+var])
                except:
                    inputs_indep.append(None)
                    covs_indep.append(None)
                try:
                    inputs_corr.append(ancillary_dataset["u_systematic_corr_rad_irr_"+var])
                    covs_corr.append(ancillary_dataset["cov_systematic_corr_rad_irr_"+var])
                except:
                    inputs_corr.append(None)
                    covs_corr.append(None)

        return inputs_indep,inputs_corr,covs_indep,covs_corr

    def preprocess_l0(self, datasetl0, datasetl0_bla, wavids):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """
        datasetl0=datasetl0.isel(wavelength=slice(wavids[0],wavids[1]))
        datasetl0_bla=datasetl0_bla.isel(wavelength=slice(wavids[0],wavids[1]))
        mask = self.clip_and_mask(datasetl0,datasetl0_bla)

        datasetl0["quality_flag"][np.where(mask==1)] = DatasetUtil.set_flag(datasetl0["quality_flag"][np.where(mask==1)],"outliers") #for i in range(len(mask))]

        DN_rand = DatasetUtil.create_variable([len(datasetl0["wavelength"]), len(datasetl0["scan"])],
                                     dim_names=["wavelength", "scan"], dtype=np.uint32, fill_value=0)
        DN_syst = DatasetUtil.create_variable([len(datasetl0["wavelength"]), len(datasetl0["scan"])],
                                     dim_names=["wavelength", "scan"], dtype=np.uint32, fill_value=0)

        datasetl0["u_random_digital_number"] = DN_rand

        std = (datasetl0['digital_number'].where(mask==1)-datasetl0['digital_number'].where(datasetl0.quality_flag == 0)).std(dim="scan")
        rand = np.zeros_like(DN_rand.values)
        for i in range(len(datasetl0["scan"])):
            rand[:, i] = std
        datasetl0["u_random_digital_number"].values = rand
        datasetl0["u_systematic_digital_number"] = DN_syst

        return datasetl0, datasetl0_bla

    def clip_and_mask(self, dataset, dataset_bla, k_unc=3):
        mask = []

        # check if zeros, max, fillvalue:

        # check if integrated signal is outlier
        series_ids = np.unique(dataset['series_id'])
        out = np.empty((len(series_ids), len(dataset['wavelength'])))
        for i in range(len(series_ids)):
            ids = np.where(dataset['series_id'] == series_ids[i])
            dark_signals = self.find_nearest_black(dataset_bla,np.mean(
                dataset['acquisition_time'].values[ids]),np.mean(
                dataset['integration_time'].values[ids]))
            intsig = np.nanmean((dataset["digital_number"].values[:, ids]-dark_signals[:,None,None]), axis=0)[0]
            noisestd, noiseavg = self.sigma_clip(intsig) # calculate std and avg for non NaN columns
            maski = np.zeros_like(intsig) # mask the columns that have NaN
            maski[np.where(np.abs(intsig - noiseavg) >= k_unc * noisestd)] = 1
            mask = np.append(mask, maski)


        # check if 10% of pixels are outiers

        # mask_wvl = np.zeros((len(datasetl0["wavelength"]),len(datasetl0["scan"])))
        # for i in range(len(dataset["wavelength"])):

        return mask

    def sigma_clip(self,values,tolerance=0.01,median=True,sigma_thresh=3.0):
        # Remove NaNs from input values
        values = np.array(values)
        values = values[np.where(np.isnan(values) == False)]
        values_original = np.copy(values)

        # Continue loop until result converges
        diff = 10E10
        while diff > tolerance:
            # Assess current input iteration
            if median == False:
                average = np.mean(values)
            elif median == True:
                average = np.median(values)
            sigma_old = np.std(values)

            # Mask those pixels that lie more than 3 stdev away from mean
            check = np.zeros([len(values)])
            check[np.where(values > (average+(sigma_thresh*sigma_old)))] = 1
            # check[ np.where( values<(average-(sigma_thresh*sigma_old)) ) ] = 1
            values = values[np.where(check < 1)]

            # Re-measure sigma and test for convergence
            sigma_new = np.std(values)
            diff = abs(sigma_old-sigma_new)/sigma_old

        # Perform final mask
        check = np.zeros([len(values)])
        check[np.where(values > (average+(sigma_thresh*sigma_old)))] = 1
        check[np.where(values < (average-(sigma_thresh*sigma_old)))] = 1
        values = values[np.where(check < 1)]

        # Return results
        return sigma_new,average



    def process_measurement_function(self, measurandstring, dataset, measurement_function, input_quantities,
                                     u_random_input_quantities,
                                     u_systematic_input_quantities_indep,
                                     u_systematic_input_quantities_corr,
                                     cov_systematic_input_quantities_indep,
                                     cov_systematic_input_quantities_corr):
        datashape = input_quantities[0].shape
        for i in range(len(input_quantities)):
            if len(input_quantities[i].shape) < len(datashape):
                if input_quantities[i].shape[0]==datashape[1]:
                    input_quantities[i] = np.tile(input_quantities[i],(datashape[0],1))
                else:
                    input_quantities[i] = np.tile(input_quantities[i],(datashape[1],1)).T

            if u_random_input_quantities[i] is not None:
                if len(u_random_input_quantities[i].shape) < len(datashape):
                    u_random_input_quantities[i] = np.tile(u_random_input_quantities[i], (datashape[1], 1)).T
            if u_systematic_input_quantities_indep[i] is not None:
                if len(u_systematic_input_quantities_indep[i].shape) < len(datashape):
                    u_systematic_input_quantities_indep[i] = np.tile(u_systematic_input_quantities_indep[i], (datashape[1], 1)).T
            if u_systematic_input_quantities_corr[i] is not None:
                if len(u_systematic_input_quantities_corr[i].shape) < len(datashape):
                    u_systematic_input_quantities_corr[i] = np.tile(u_systematic_input_quantities_corr[i], (datashape[1], 1)).T

        measurand = measurement_function(*input_quantities)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u_random_measurand = self.prop.propagate_random(measurement_function, input_quantities,
                                                            u_random_input_quantities,repeat_dims=1)
            u_syst_measurand_indep,corr_syst_measurand_indep = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_indep,
                cov_x=cov_systematic_input_quantities_indep,return_corr=True,
                repeat_dims=1,corr_axis=0)
            u_syst_measurand_corr,corr_syst_measurand_corr = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_corr,
                cov_x=cov_systematic_input_quantities_corr,return_corr=True,
                repeat_dims=1,corr_axis=0)

        dataset[measurandstring].values = measurand
        dataset["u_random_" + measurandstring].values = u_random_measurand
        dataset["u_systematic_indep_" + measurandstring].values = u_syst_measurand_indep
        dataset["u_systematic_corr_rad_irr_" + measurandstring].values = u_syst_measurand_corr
        dataset["corr_random_" + measurandstring].values = np.eye(len(u_random_measurand))
        dataset["corr_systematic_indep_" + measurandstring].values = corr_syst_measurand_indep
        dataset["corr_systematic_corr_rad_irr_" + measurandstring].values = corr_syst_measurand_corr

        return dataset
