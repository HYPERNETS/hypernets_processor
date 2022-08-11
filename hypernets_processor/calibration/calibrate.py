"""
Calibration class
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import \
    MeasurementFunctionFactory
from hypernets_processor.data_utils.propagate_uncertainties import PropagateUnc
from hypernets_processor.data_utils.quality_checks import QualityChecks
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.plotting.plotting import Plotting

import numpy as np
import matplotlib.pyplot as plt
from obsarray.templater.dataset_util import DatasetUtil

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
        self.qual = QualityChecks(context)
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context)
        self.plot = Plotting(context)
        self.context = context

    def calibrate_l1a_water(self, measurandstring, dataset_l0, dataset_l0_bla, calibration_data, swir=False):
        if measurandstring != "radiance" and measurandstring != "irradiance":
            self.context.logger.error("the measurandstring needs to be either 'radiance' or 'irradiance")
            exit()

        if self.context.get_config_value("plot_l0"):
            self.plot.plot_scans_in_series("digital_number",dataset_l0)

        calibrate_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate"))
        input_vars = calibrate_function.get_argument_names()

        dataset_l0 = self.preprocess_l0(dataset_l0,dataset_l0_bla, calibration_data)
        self.context.logger.info("preprocessing done")
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

    def calibrate_l1a(
            self, measurandstring, dataset_l0, dataset_l0_bla, calibration_data, swir=False
    ):
        if measurandstring != "radiance" and measurandstring != "irradiance":
            self.context.logger.error(
                "the measurandstring needs to be either 'radiance' or 'irradiance"
            )
            exit()

        if self.context.get_config_value("plot_l0"):
            self.plot.plot_scans_in_series("digital_number", dataset_l0)

        calibrate_function = (
            self._measurement_function_factory.get_measurement_function(
                self.context.get_config_value("measurement_function_calibrate")
            )
        )
        input_vars = calibrate_function.get_argument_names()

        dataset_l0_masked, dataset_l0_bla_masked = self.preprocess_l0(
            dataset_l0, dataset_l0_bla, calibration_data
        )

        self.context.logger.debug("preprocessing done")

        dataset_l1a = self.templ.l1a_template_from_l0_dataset(
            measurandstring, dataset_l0_masked, swir
        )

        input_qty = self.prop.find_input_l1a(
            input_vars, dataset_l0_masked, calibration_data
        )

        if self.context.get_config_value("uncertainty_l1a"):
            u_random_input_qty = self.prop.find_u_random_input_l1a(
                input_vars, dataset_l0_masked, calibration_data
            )
            (
                u_systematic_input_qty_indep,
                u_systematic_input_qty_corr,
                corr_systematic_input_qty_indep,
                corr_systematic_input_qty_corr,
            ) = self.prop.find_u_systematic_input_l1a(
                input_vars, dataset_l0_masked, calibration_data
            )
            dataset_l1a = self.prop.process_measurement_function_l1a(
                measurandstring,
                dataset_l1a,
                calibrate_function.function,
                input_qty,
                u_random_input_qty,
                u_systematic_input_qty_indep,
                u_systematic_input_qty_corr,
                corr_systematic_input_qty_indep,
                corr_systematic_input_qty_corr,
            )

        else:
            datashape = input_qty[0].shape
            for i in range(len(input_qty)):
                if len(input_qty[i].shape) < len(datashape):
                    if input_qty[i].shape[0] == datashape[1]:
                        input_qty[i] = np.tile(input_qty[i], (datashape[0], 1))
                    elif input_qty[i].shape[0] == datashape[0]:
                        input_qty[i] = np.tile(input_qty[i], (datashape[1], 1)).T
            measurand = calibrate_function.function(*input_qty)
            dataset_l1a[measurandstring].values = measurand
            dataset_l1a.drop(
                [
                    "u_rel_random_" + measurandstring,
                    "u_rel_systematic_indep_" + measurandstring,
                    "u_rel_systematic_corr_rad_irr_" + measurandstring,
                    "corr_systematic_indep_" + measurandstring,
                    "corr_systematic_corr_rad_irr_" + measurandstring,
                    ]
            )

        if self.context.get_config_value("write_l1a"):
            self.writer.write(
                dataset_l1a,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings"
                ),
            )

        if self.context.get_config_value("plot_l1a"):
            self.plot.plot_scans_in_series(measurandstring, dataset_l1a)

        if self.context.get_config_value("plot_l1a_diff"):
            self.plot.plot_diff_scans(measurandstring, dataset_l1a)

        return dataset_l1a, dataset_l0_masked, dataset_l0_bla_masked

    def find_nearest_black(self, dataset, acq_time, int_time):
        ids = np.where(
            (
                    abs(dataset["acquisition_time"] - acq_time)
                    == min(abs(dataset["acquisition_time"] - acq_time))
            )
            & (dataset["integration_time"] == int_time)
        )[0]
        # todo check if integration time always has to be same
        dark_mask = self.qual.outlier_checks(dataset["digital_number"].values[:, ids])
        if np.sum(dark_mask) > 0:
            dark_outlier = 1
        else:
            dark_outlier = 0
        avg_black_series = np.mean(
            dataset["digital_number"].values[:, ids[np.where(dark_mask == 0)]], axis=1
        )
        return avg_black_series, dark_outlier

    def preprocess_l0(self, datasetl0, datasetl0_bla, dataset_calib):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """
        wavs = dataset_calib["wavelength"].values
        wavpix = dataset_calib["wavpix"].values

        # set up datasets for storing the masked L0 data, with wavelengths corresponding to the ones present in calib files
        datasetl0masked = datasetl0.isel(
            wavelength=slice(int(wavpix[0]), int(wavpix[-1]) + 1)
        )
        datasetl0masked_bla = datasetl0_bla.isel(
            wavelength=slice(int(wavpix[0]), int(wavpix[-1]) + 1)
        )
        datasetl0masked = datasetl0masked.assign_coords(wavelength=wavs)
        datasetl0masked_bla = datasetl0masked_bla.assign_coords(wavelength=wavs)

        series_ids = np.unique(datasetl0masked["series_id"])
        series_ids_bla = np.unique(datasetl0masked["series_id"] + 1)
        scanids = np.concatenate(
            [
                np.where(datasetl0masked_bla["series_id"].values == sid)[0]
                for sid in series_ids_bla
            ]
        )
        datasetl0masked_bla = datasetl0masked_bla.isel(scan=scanids)

        # set up arrays for storing the best dark for each scan of the radiance/irradiance
        dark_signals_radscans = np.zeros_like(datasetl0masked["digital_number"].values)
        dark_outliers_radscans = np.zeros_like(datasetl0masked["quality_flag"].values)

        for i in range(len(series_ids)):
            ids = np.where(datasetl0masked["series_id"] == series_ids[i])[0]
            dark_signal_rad, dark_outlier_rad = self.find_nearest_black(
                datasetl0masked_bla,
                datasetl0masked["acquisition_time"].values[ids[0]],
                datasetl0masked["integration_time"].values[ids[0]],
            )
            # plt.plot(dark_signal)
            # plt.savefig("plot_dark_test.png")
            for id in ids:
                dark_signals_radscans[:, id], dark_outliers_radscans[id] = (
                    dark_signal_rad,
                    dark_outlier_rad,
                )

        datasetl0masked, mask = self.qual.perform_quality_check_L0(
            datasetl0masked, series_ids
        )
        datasetl0masked["quality_flag"][
            np.where(dark_outlier_rad == 1)
        ] = DatasetUtil.set_flag(
            datasetl0masked["quality_flag"][np.where(dark_outlier_rad == 1)],
            "dark_outliers",
        )  # for i in range(len(mask))]

        DN_rand = DatasetUtil.create_variable(
            [len(datasetl0masked["wavelength"]), len(datasetl0masked["scan"])],
            dim_names=["wavelength", "scan"],
            dtype=np.float32,
            fill_value=0,
            attributes={
                     "standard_name": "random relative uncertainty on digital number",
                     "long_name": "random relative uncertainty on digital number",
                     "units": "%",
                     "err_corr": [
                         {"dim": "scan", "form": "random", "params": [], "units": []},
                         {"dim": "wavelength", "form": "random", "params": [], "units": []},
                     ],
                 },
        )

        datasetl0masked["u_rel_random_digital_number"] = DN_rand
        datasetl0masked["digital_number"].attrs["unc_comps"] = ["u_rel_random_digital_number",]

        # calculate and store random uncertainties on radiance/irradiance
        rand = np.zeros_like(DN_rand.values)
        for i in range(len(series_ids)):
            ids = np.where(datasetl0masked["series_id"] == series_ids[i])[0]
            ids_masked = np.where(
                (datasetl0masked["series_id"] == series_ids[i]) & (mask == 0)
            )[0]
            if len(ids_masked) > 0:
                std = np.std(
                    (
                            datasetl0masked["digital_number"].values[:, ids_masked]
                            - dark_signals_radscans[:, ids_masked]
                    ),
                    axis=1,
                )
                avg = np.mean(
                    (
                            datasetl0masked["digital_number"].values[:, ids_masked]
                            - dark_signals_radscans[:, ids_masked]
                    ),
                    axis=1,
                )
                for ii, id in enumerate(ids):
                    rand[:, id] = std / avg *100
            else:
                for ii, id in enumerate(ids):
                    rand[:, id] = np.nan

            datasetl0masked["u_rel_random_digital_number"].values = rand

            DN_dark = DatasetUtil.create_variable(
                [len(datasetl0masked["wavelength"]), len(datasetl0masked["scan"])],
                dim_names=["wavelength", "scan"],
                dtype=np.uint16,
                fill_value=0,
                attributes= {"standard_name": "digital number for dark signal",
                               "long_name": "Digital number, raw data, dark signal",
                               "units": "-",
                               "unc_comps": [
                                   "u_rel_random_dark_signal",
                               ],}
            )

            datasetl0masked["dark_signal"] = DN_dark
            datasetl0masked["dark_signal"].values = dark_signals_radscans

        datasetl0masked_bla, mask = self.qual.perform_quality_check_L0(
            datasetl0masked_bla, series_ids_bla
        )

        DN_rand_bla = DatasetUtil.create_variable(
            [len(datasetl0masked_bla["wavelength"]), len(datasetl0masked_bla["scan"])],
            dim_names=["wavelength", "scan"],
            dtype=np.float32,
            fill_value=0,
            attributes={
                "standard_name": "random relative uncertainty on black digital number",
                "long_name": "random relative uncertainty on black digital number",
                "units": "%",
                "err_corr": [
                    {"dim": "scan", "form": "random", "params": [], "units": []},
                    {"dim": "wavelength", "form": "random", "params": [], "units": []},
                ],
            },
        )

        datasetl0masked_bla["u_rel_random_digital_number"] = DN_rand_bla

        # now calculate random uncertainties for blacks
        rand = np.zeros_like(DN_rand_bla.values)
        for i in range(len(series_ids_bla)):
            ids = np.where(datasetl0masked_bla["series_id"] == series_ids_bla[i])[0]
            ids_masked = np.where(
                (datasetl0masked_bla["series_id"] == series_ids_bla[i]) & (mask == 0)
            )[0]
            if len(ids_masked) > 0:
                std = np.std(
                    (datasetl0masked_bla["digital_number"].values[:, ids_masked]),
                    axis=1,
                )
                avg = np.mean(
                    (datasetl0masked_bla["digital_number"].values[:, ids_masked]),
                    axis=1,
                )
                for ii, id in enumerate(ids):
                    rand[:, id] = std / avg*100
            else:
                for ii, id in enumerate(ids):
                    rand[:, id] = np.nan

            datasetl0masked_bla["u_rel_random_digital_number"].values = rand

        return datasetl0masked, datasetl0masked_bla
