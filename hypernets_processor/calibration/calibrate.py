"""
Calibration class
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import \
    MeasurementFunctionFactory
import punpy
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.dataset_util import DatasetUtil
import numpy as np

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
        self.hdsb = HypernetsDSBuilder(context=context)
        self.writer = HypernetsWriter(context)
        self.context = context

    def calibrate_l1a(self, measurandstring, dataset_l0, dataset_l0_bla, calibration_data):

        if measurandstring != "radiance" and measurandstring != "irradiance":
            print("the measurandstring needs to be either 'radiance' or 'irradiance")
            exit()

        calibrate_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate"))
        input_vars = calibrate_function.get_argument_names()
        print("the used variables are:", input_vars)

        dataset_l1a = self.l1a_template_from_l0_dataset(measurandstring, dataset_l0)
        dataset_l0, dataset_l1a = self.preprocess_l0(dataset_l0, dataset_l1a)

        input_qty_l1a = self.find_input(input_vars, dataset_l0, dataset_l0_bla, calibration_data)
        u_random_input_qty_l1a = self.find_u_random_input(input_vars, dataset_l0, dataset_l0_bla, calibration_data)
        u_systematic_input_qty_l1a = self.find_u_systematic_input(input_vars, dataset_l0, dataset_l0_bla,
                                                                  calibration_data)
        dataset_l1a = self.process_measurement_function(measurandstring, dataset_l1a, calibrate_function.function,
                                                        input_qty_l1a,
                                                        u_random_input_qty_l1a, u_systematic_input_qty_l1a)
        if self.context.get_config_value("write_l1a"):
            self.writer.write(dataset_l1a, overwrite=True)

        return dataset_l1a

    def average_l1b(self, measurandstring, dataset_l1a):

        dataset_l1b = self.l1b_template_from_l1a_dataset(measurandstring, dataset_l1a)

        dataset_l1b[measurandstring].values = self.calc_mean_masked(dataset_l1a, measurandstring)
        dataset_l1b["u_random_" + measurandstring].values = self.calc_mean_masked(dataset_l1a,
                                                                                  "u_random_" + measurandstring,
                                                                                  rand_unc=True)
        dataset_l1b["u_systematic_" + measurandstring].values = self.calc_mean_masked(dataset_l1a,
                                                                                      "u_systematic_" + measurandstring)
        dataset_l1b["corr_random_" + measurandstring].values = np.eye(
            len(dataset_l1b["u_systematic_" + measurandstring].values))
        dataset_l1b["corr_systematic_" + measurandstring].values = self.calc_mean_masked(dataset_l1a,
                                                                                         "corr_systematic_" + measurandstring,
                                                                                         corr=True)

        self.writer.write(dataset_l1b, overwrite=True)

        return dataset_l1b

    def calc_mean_masked(self, dataset, var, rand_unc=False, corr=False):
        series_id = np.unique(dataset['series_id'])
        if corr:
            out = np.empty((len(series_id), len(dataset['wavelength']), len(dataset['wavelength'])))
        else:
            out = np.empty((len(series_id), len(dataset['wavelength'])))
        for i in range(len(series_id)):
            ids = np.where((dataset['series_id'] == series_id[i]) & (dataset['quality_flag'] == 0))
            out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]
            if rand_unc:
                out[i] = out[i] / len(ids[0])
        if corr:
            out = np.mean(out, axis=0)
        return out.T

    def find_nearest_black(self, dataset, acq_time, int_time):
        ids = np.where(
            (abs(dataset['acquisition_time'] - acq_time) == min(abs(dataset['acquisition_time'] - acq_time))) & (
                        dataset['integration_time'] == int_time))
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
                # if masked_avg:
                #     acqui = np.unique(dataset['acquisition_time'])
                #     for i in range(len(acqui)):
                #         inttime=dataset['integration_time'].values[int(i*len(dataset['acquisition_time'])/len(acqui))]
                #         dark_signals.append(self.find_nearest_black(datasetbla,acqui[i],inttime))
                # else:
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

    def find_u_random_input(self, variables, dataset, datasetbla, ancillary_dataset, masked_avg=False):
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
                inputs.append(ancillary_dataset["u_random_" + var])
        return inputs

    def find_u_systematic_input(self, variables, dataset, datasetbla, ancillary_dataset, masked_avg=False):
        """
        returns a list of the systematic uncertainties on the data for a given list of input variables

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
                if masked_avg:
                    inputs.append(self.calc_mean_input(dataset, "u_systematic_" + var))
                else:
                    inputs.append(dataset["u_systematic_" + var].values)
            except:
                inputs.append(ancillary_dataset["u_systematic_" + var])

        return inputs

    def preprocess_l0(self, datasetl0, datasetl1a):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """
        dim_sizes_dict = {"wavelength": len(datasetl0["wavelength"]), "scan": len(datasetl0["scan"])}
        du = DatasetUtil()

        mask = self.clip_and_mask(datasetl0)
        datasetl0["quality_flag"].values = mask
        datasetl1a["quality_flag"].values = mask

        DN_rand = du.create_variable([len(datasetl0["wavelength"]), len(datasetl0["scan"])],
                                     dim_names=["wavelength", "scan"], dtype=np.uint32, fill_value=0)
        DN_syst = du.create_variable([len(datasetl0["wavelength"]), len(datasetl0["scan"])],
                                     dim_names=["wavelength", "scan"], dtype=np.uint32, fill_value=0)

        datasetl0["u_random_digital_number"] = DN_rand

        std = datasetl0['digital_number'].where(datasetl0.quality_flag == 0).std(dim="scan")
        rand = np.zeros_like(DN_rand.values)
        for i in range(len(datasetl0["scan"])):
            rand[:, i] = std
        datasetl0["u_random_digital_number"].values = rand
        datasetl0["u_systematic_digital_number"] = DN_syst

        return datasetl0, datasetl1a

    def clip_and_mask(self, dataset, k_unc=3):
        mask = []

        # check if zeros, max, fillvalue:

        # check if integrated signal is outlier
        series_ids = np.unique(dataset['series_id'])
        out = np.empty((len(series_ids), len(dataset['wavelength'])))
        for i in range(len(series_ids)):
            ids = np.where(dataset['series_id'] == series_ids[i])
            intsig = np.nansum((dataset["digital_number"].values[:, ids]), axis=0)[0]
            noisestd, noiseavg = self.sigma_clip(intsig)
            maski = np.ones_like(intsig)
            maski[np.where(np.abs(intsig - noiseavg) >= k_unc * noisestd)] = 2
            mask = np.append(mask, maski)
            print("mask",mask)


        # check if 10% of pixels are outiers

        # mask_wvl = np.zeros((len(datasetl0["wavelength"]),len(datasetl0["scan"])))
        # for i in range(len(dataset["wavelength"])):

        return mask

    def sigma_clip(self, values, tolerance=0.01, median=True, sigma_thresh=3.0):
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
            check[np.where(values > (average + (sigma_thresh * sigma_old)))] = 1
            # check[ np.where( values<(average-(sigma_thresh*sigma_old)) ) ] = 1
            values = values[np.where(check < 1)]

            # Re-measure sigma and test for convergence
            sigma_new = np.std(values)
            diff = abs(sigma_old - sigma_new) / sigma_old

        # Perform final mask
        check = np.zeros([len(values)])
        check[np.where(values > (average + (sigma_thresh * sigma_old)))] = 1
        check[np.where(values < (average - (sigma_thresh * sigma_old)))] = 1
        values = values[np.where(check < 1)]

        # Return results
        return sigma_new, average

    def l1a_template_from_l0_dataset(self, measurandstring, dataset_l0):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """

        l1a_dim_sizes_dict = {"wavelength": len(dataset_l0["wavelength"]), "scan": len(dataset_l0["scan"])}
        if measurandstring == "radiance":
            dataset_l1a = self.hdsb.create_ds_template(l1a_dim_sizes_dict, ds_format="L_L1A_RAD",
                                                       propagate_ds=dataset_l0)
        elif measurandstring == "irradiance":
            dataset_l1a = self.hdsb.create_ds_template(l1a_dim_sizes_dict, "L_L1A_IRR", propagate_ds=dataset_l0)

        return dataset_l1a

    def l1b_template_from_l1a_dataset(self, measurandstring, dataset_l1a):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        l1b_dim_sizes_dict = {"wavelength": len(dataset_l1a["wavelength"]),
                              "series": len(np.unique(dataset_l1a['series_id']))}

        if measurandstring == "radiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "L_L1B_RAD", propagate_ds=dataset_l1a)
        elif measurandstring == "irradiance":
            dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict, "L_L1B_IRR", propagate_ds=dataset_l1a)

        series_id = np.unique(dataset_l1a['series_id'])
        dataset_l1b["series_id"].values = series_id

        for variablestring in ["acquisition_time", "viewing_azimuth_angle", "viewing_zenith_angle",
                               "solar_azimuth_angle", "solar_zenith_angle"]:
            temp_arr = np.empty(len(series_id))
            for i in range(len(series_id)):
                ids = np.where((dataset_l1a['series_id'] == series_id[i]) & (dataset_l1a['quality_flag'] == 1))
                temp_arr[i] = np.mean(dataset_l1a[variablestring].values[ids])
            dataset_l1b[variablestring].values = temp_arr

        return dataset_l1b

    def process_measurement_function(self, measurandstring, dataset, measurement_function, input_quantities,
                                     u_random_input_quantities,
                                     u_systematic_input_quantities):
        datashape = input_quantities[0].shape
        for i in range(len(input_quantities)):
            if len(input_quantities[i].shape) < len(datashape):
                input_quantities[i] = np.tile(input_quantities[i], (datashape[1], 1)).T
            if len(u_random_input_quantities[i].shape) < len(datashape):
                u_random_input_quantities[i] = np.tile(u_random_input_quantities[i], (datashape[1], 1)).T
                u_systematic_input_quantities[i] = np.tile(u_systematic_input_quantities[i], (datashape[1], 1)).T
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function, input_quantities,
                                                        u_random_input_quantities)
        u_systematic_measurand, corr_systematic_measurand = self.prop.propagate_systematic(measurement_function,
                                                                                           input_quantities,
                                                                                           u_systematic_input_quantities,
                                                                                           return_corr=True,
                                                                                           corr_axis=0)
        dataset[measurandstring].values = measurand
        dataset["u_random_" + measurandstring].values = u_random_measurand
        dataset["u_systematic_" + measurandstring].values = u_systematic_measurand
        dataset["corr_random_" + measurandstring].values = np.eye(len(u_random_measurand))
        dataset["corr_systematic_" + measurandstring].values = corr_systematic_measurand

        return dataset
