"""
Calibration class
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import \
    MeasurementFunctionFactory
from hypernets_processor.data_utils.propagate_uncertainties import PropagateUnc
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.plotting.plotting import Plotting

import numpy as np
import matplotlib.pyplot as plt

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

class Calibrate:
    def __init__(self, context, parallel_cores=0):
        self._measurement_function_factory = MeasurementFunctionFactory()
        self.prop = PropagateUnc(context, parallel_cores=parallel_cores)
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context)
        self.plot = Plotting(context)
        self.context = context

    def calibrate_l1a(self, measurandstring, dataset_l0, dataset_l0_bla, calibration_data, swir=False):
        if measurandstring != "radiance" and measurandstring != "irradiance":
            self.context.logger.error("the measurandstring needs to be either 'radiance' or 'irradiance")
            exit()

        if self.context.get_config_value("plot_l0"):
            self.plot.plot_scans_in_series("digital_number",dataset_l0)

        calibrate_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate"))
        input_vars = calibrate_function.get_argument_names()

        dataset_l0 = self.preprocess_l0(dataset_l0,dataset_l0_bla, calibration_data)

        dataset_l1a = self.templ.l1a_template_from_l0_dataset(measurandstring, dataset_l0, swir)

        input_qty = self.prop.find_input_l1a(input_vars, dataset_l0, calibration_data)
        u_random_input_qty = self.prop.find_u_random_input_l1a(input_vars, dataset_l0, calibration_data)
        u_systematic_input_qty_indep,u_systematic_input_qty_corr,\
        corr_systematic_input_qty_indep,corr_systematic_input_qty_corr = self.prop.find_u_systematic_input_l1a(input_vars, dataset_l0, calibration_data)
        dataset_l1a = self.prop.process_measurement_function_l1a(measurandstring,
                                                        dataset_l1a,
                                                        calibrate_function.function,
                                                        input_qty,
                                                        u_random_input_qty,
                                                        u_systematic_input_qty_indep,
                                                        u_systematic_input_qty_corr,
                                                        corr_systematic_input_qty_indep,
                                                        corr_systematic_input_qty_corr)

        if self.context.get_config_value("write_l1a"):
            self.writer.write(dataset_l1a, overwrite=True, remove_vars_strings=self.context.get_config_value("remove_vars_strings"))

        if self.context.get_config_value("plot_l1a"):
            self.plot.plot_scans_in_series(measurandstring,dataset_l1a)

        if self.context.get_config_value("plot_l1a_diff"):
            self.plot.plot_diff_scans(measurandstring,dataset_l1a)

        if self.context.get_config_value("plot_uncertainty"):
            self.plot.plot_relative_uncertainty(measurandstring,dataset_l1a)

        if self.context.get_config_value("plot_correlation"):
            self.plot.plot_correlation(measurandstring,dataset_l1a)

        return dataset_l1a

    def find_nearest_black(self, dataset, acq_time, int_time):
        ids = np.where((abs(dataset['acquisition_time'] - acq_time) ==
                        min(abs(dataset['acquisition_time'] - acq_time))) &
                       (dataset['integration_time'] == int_time))[0]
        #todo check if integration time always has to be same

        dark_mask=self.quality_checks(dataset["digital_number"].values[:,ids])
        if np.sum(dark_mask)>0:
            dark_outlier=1
        else:
            dark_outlier=0
        avg_black_series = np.mean(dataset["digital_number"].values[:,ids[np.where(dark_mask==0)]], axis=1)
        return avg_black_series,dark_outlier


    def preprocess_l0(self, datasetl0, datasetl0_bla, dataset_calib):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """
        wavs=dataset_calib["wavelength"].values
        wavpix=dataset_calib["wavpix"].values

        datasetl0=datasetl0.isel(wavelength=slice(int(wavpix[0]),int(wavpix[-1])+1))
        datasetl0_bla=datasetl0_bla.isel(wavelength=slice(int(wavpix[0]),int(wavpix[-1])+1))
        datasetl0 = datasetl0.assign_coords(wavelength=wavs)
        datasetl0_bla = datasetl0_bla.assign_coords(wavelength=wavs)

        series_ids = np.unique(datasetl0['series_id'])
        dark_signals = np.zeros_like(datasetl0['digital_number'].values)
        dark_outliers= np.zeros_like(datasetl0['quality_flag'].values)
        mask = []
        for i in range(len(series_ids)):
            ids = np.where(datasetl0['series_id'] == series_ids[i])[0]
            for ii,id in enumerate(ids):
                dark_signals[:,id],dark_outliers[id] = self.find_nearest_black(datasetl0_bla,
                datasetl0['acquisition_time'].values[id],
                datasetl0['integration_time'].values[id])
            maski=self.quality_checks((datasetl0["digital_number"].values[:, ids]-
                                 dark_signals[:,ids]))
            mask = np.append(mask, maski)

        datasetl0["quality_flag"][np.where(mask==1)] = DatasetUtil.set_flag(datasetl0["quality_flag"][np.where(mask==1)],"outliers") #for i in range(len(mask))]
        datasetl0["quality_flag"][np.where(dark_outliers==1)] = DatasetUtil.set_flag(datasetl0["quality_flag"][np.where(dark_outliers==1)],"dark_outliers") #for i in range(len(mask))]

        DN_rand = DatasetUtil.create_variable(
            [len(datasetl0["wavelength"]),len(datasetl0["scan"])],
            dim_names=["wavelength","scan"],dtype=np.float32,fill_value=0)

        datasetl0["u_rel_random_digital_number"] = DN_rand

        rand = np.zeros_like(DN_rand.values)
        for i in range(len(series_ids)):
            ids = np.where(datasetl0['series_id'] == series_ids[i])[0]
            ids_masked = np.where((datasetl0['series_id'] == series_ids[i]) & (mask == 0))[0]
            std = np.std((datasetl0['digital_number'].values[:,ids_masked]-dark_signals[:,ids_masked]), axis=1)
            avg = np.mean((datasetl0['digital_number'].values[:,ids_masked]-dark_signals[:,ids_masked]), axis=1)

            for ii,id in enumerate(ids):
                rand[:, id] = std/avg

        datasetl0["u_rel_random_digital_number"].values = rand

        DN_dark = DatasetUtil.create_variable(
            [len(datasetl0["wavelength"]),len(datasetl0["scan"])],
            dim_names=["wavelength","scan"],dtype=np.uint32,fill_value=0)

        datasetl0["dark_signal"] = DN_dark
        datasetl0["dark_signal"].values = dark_signals

        return datasetl0

    def quality_checks(self,data_subset, k_unc=3):
        intsig =np.nanmean(data_subset,axis=0)
        mask = np.zeros_like(intsig)  # mask the columns that have NaN
        if len(intsig)>1:
            noisestd,noiseavg = self.sigma_clip(
                intsig)  # calculate std and avg for non NaN columns
            mask[np.where(np.abs(intsig-noiseavg) >= k_unc*noisestd)] = 1
            mask[np.where(np.abs(intsig-noiseavg) >= 0.25*intsig)] = 1
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


