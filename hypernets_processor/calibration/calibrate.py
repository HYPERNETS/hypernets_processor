"""
Calibration class
"""
import datetime

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import (
    MeasurementFunctionFactory,
)
from hypernets_processor.data_utils.quality_checks import QualityChecks
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_utils.average import Average

import punpy

import numpy as np
import matplotlib.pyplot as plt
from obsarray.templater.dataset_util import DatasetUtil

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class Calibrate:
    def __init__(self, context, parallel_cores=0):
        self._measurement_function_factory = MeasurementFunctionFactory
        self.qual = QualityChecks(context)
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context)
        self.plot = Plotting(context)
        self.avg = Average(context)
        self.context = context

    def calibrate_l1a(
        self,
        measurandstring,
        dataset_l0,
        dataset_l0_bla,
        calibration_data,
        swir=False,
        preprocessing=True,
    ):
        if measurandstring != "radiance" and measurandstring != "irradiance":
            self.context.logger.error(
                "the measurandstring needs to be either 'radiance' or 'irradiance"
            )
            exit()

        if self.context.get_config_value("plot_l0"):
            self.plot.plot_scans_in_series("digital_number", dataset_l0)

        if preprocessing:
            dataset_l0_masked, dataset_l0_bla_masked = self.preprocess_l0(
                dataset_l0, dataset_l0_bla, calibration_data
            )

            self.context.logger.debug("preprocessing done")
        else:
            dataset_l0_masked = dataset_l0
            dataset_l0_bla_masked = dataset_l0_bla

        dataset_l1a = self.templ.l1a_template_from_l0a_dataset(
            measurandstring, dataset_l0_masked, swir
        )

        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32", MCdimlast=True
        )

        calibrate_function = self._measurement_function_factory(
            prop=prop, repeat_dims="scan", yvariable=measurandstring
        ).get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate")
        )

        if self.context.get_config_value("uncertainty_l1a") and self.context.get_config_value("mcsteps")>0:
            dataset_l1a = calibrate_function.propagate_ds_specific(
                ["random", "systematic_indep", "systematic_corr_rad_irr"],
                dataset_l0_masked,
                calibration_data,
                ds_out_pre=dataset_l1a,
                store_unc_percent=True,
            )

            if self.context.get_config_value("bad_wavelenth_ranges"):
                for maskrange in self.context.get_config_value(
                    "bad_wavelenth_ranges"
                ).split(","):
                    start_mask = float(maskrange.split("-")[0])
                    end_mask = float(maskrange.split("-")[1])
                    dataset_l1a["u_rel_systematic_indep_" + measurandstring].values[
                        np.where(
                            (dataset_l1a.wavelength > start_mask)
                            & (dataset_l1a.wavelength < end_mask)
                        )[0],
                        :,
                    ] += 50

        else:
            measurand = calibrate_function.run(dataset_l0_masked, calibration_data)
            dataset_l1a[measurandstring].values = measurand
            dataset_l1a = dataset_l1a.drop(
                [
                    "u_rel_random_" + measurandstring,
                    "u_rel_systematic_indep_" + measurandstring,
                    "u_rel_systematic_corr_rad_irr_" + measurandstring,
                    "err_corr_systematic_indep_" + measurandstring,
                    "err_corr_systematic_corr_rad_irr_" + measurandstring,
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

    def calibrate_l1b(
        self, measurandstring, dataset_l0, dataset_l0_bla, calibration_data, swir=False
    ):

        dataset_l0b = self.avg.average_l0(
            measurandstring, dataset_l0, dataset_l0_bla, swir=swir
        )

        dataset_l1b = self.templ.l1b_template_from_l0b_dataset(
            measurandstring, dataset_l0b
        )

        if self.context.get_config_value("write_l0b"):
            self.writer.write(
                dataset_l0b,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings"
                ),
            )

        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32", MCdimlast=True
        )
        calibrate_function = self._measurement_function_factory(
            prop=prop, repeat_dims="series", yvariable=measurandstring
        ).get_measurement_function(
            self.context.get_config_value("measurement_function_calibrate")
        )

        dataset_l1b = calibrate_function.propagate_ds_specific(
            ["random", "systematic_indep", "systematic_corr_rad_irr"],
            dataset_l0b,
            calibration_data,
            ds_out_pre=dataset_l1b,
            store_unc_percent=True,
        )

        if self.context.get_config_value("mcsteps")>0:
            self.qual.perform_quality_check_rand_unc(dataset_l1b, measurandstring)

            if self.context.get_config_value("bad_wavelenth_ranges"):
                for maskrange in self.context.get_config_value(
                    "bad_wavelenth_ranges"
                ).split(","):
                    start_mask = float(maskrange.split("-")[0])
                    end_mask = float(maskrange.split("-")[1])
                    for i in np.where(
                        (dataset_l1b.wavelength > start_mask)
                        & (dataset_l1b.wavelength < end_mask)
                    )[0]:
                        dataset_l1b["u_rel_systematic_indep_" + measurandstring].values[
                            i,
                            :,
                        ] += 50
                        dataset_l1b["err_corr_systematic_indep_" + measurandstring].values[
                            i, :
                        ] = (3 / 50) ** 2
                        dataset_l1b["err_corr_systematic_indep_" + measurandstring].values[
                            :, i
                        ] = (3 / 50) ** 2
                        dataset_l1b["err_corr_systematic_indep_" + measurandstring].values[
                            i, i
                        ] = 1

        dataset_l1b["std_" + measurandstring].values = (
            dataset_l1b[measurandstring].values
            * dataset_l0b["std_digital_number"].values
            / dataset_l0b["digital_number"].values
        )

        if self.context.get_config_value("network") == "w":
            dataset_l1b = dataset_l1b.drop("n_valid_scans_SWIR")
            if measurandstring == "irradiance":
                dataset_l1b = self.qual.perform_quality_irradiance(dataset_l1b)

            self.qual.check_standard_sequence_L1B(dataset_l1b, measurandstring, "water")

            if self.context.get_config_value("write_l1b"):
                self.writer.write(
                    dataset_l1b,
                    overwrite=True,
                    remove_vars_strings=self.context.get_config_value(
                        "remove_vars_strings"
                    ),
                )

            if self.context.get_config_value("plot_l1b"):
                self.plot.plot_series_in_sequence(measurandstring, dataset_l1b)

            if self.context.get_config_value("plot_uncertainty"):
                self.plot.plot_relative_uncertainty(measurandstring, dataset_l1b)

            if self.context.get_config_value("plot_correlation"):
                self.plot.plot_correlation(measurandstring, dataset_l1b)

        return dataset_l1b

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
        std_black_series = np.std(
            dataset["digital_number"].values[:, ids[np.where(dark_mask == 0)]], axis=1
        )
        return avg_black_series, std_black_series, dark_outlier

    def preprocess_l0(self, datasetl0, datasetl0_bla, dataset_calib):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """
        wavs = dataset_calib["wavelength"].values
        wavpix = np.squeeze(dataset_calib["wavpix"].values)
        # set up datasets for storing the masked L0 data, with wavelengths corresponding to the ones present in calib files
        datasetl0masked = datasetl0.isel(
            wavelength=slice(int(wavpix[0]), int(wavpix[-1]) + 1)
        )
        datasetl0masked_bla = datasetl0_bla.isel(
            wavelength=slice(int(wavpix[0]), int(wavpix[-1]) + 1)
        )
        #       Wavelength already exist as coordinate...?
        #        datasetl0masked = datasetl0masked.assign_coords(wavelength=wavs)
        #        datasetl0masked_bla = datasetl0masked_bla.assign_coords(wavelength=wavs)

        series_ids = np.unique(datasetl0masked["series_id"])
        series_ids_bla = np.unique(datasetl0masked["series_id"] + 1)
        scanids = np.concatenate(
            [
                np.where(datasetl0masked_bla["series_id"].values == sid)[0]
                for sid in series_ids_bla
            ]
        )
        datasetl0masked_bla = datasetl0masked_bla.isel(scan=scanids)

        # add variables for dark and uncertainties
        DN_rand = DatasetUtil.create_unc_variable(
            [len(datasetl0masked["wavelength"]), len(datasetl0masked["scan"])],
            dim_names=["wavelength", "scan"],
            dtype=np.float32,
            attributes={
                "standard_name": "random relative uncertainty on digital number",
                "long_name": "random relative uncertainty on digital number",
                "units": "%",
            },
            err_corr=[
                {"dim": "scan", "form": "random", "params": [], "units": []},
                {"dim": "wavelength", "form": "random", "params": [], "units": []},
            ],
        )

        datasetl0masked["u_rel_random_digital_number"] = DN_rand
        datasetl0masked["digital_number"].attrs["unc_comps"] = [
            "u_rel_random_digital_number",
        ]

        DN_dark = DatasetUtil.create_variable(
            [len(datasetl0masked["wavelength"]), len(datasetl0masked["scan"])],
            dim_names=["wavelength", "scan"],
            dtype=np.uint16,
            fill_value=0,
            attributes={
                "standard_name": "digital number for dark signal",
                "long_name": "Digital number, raw data, dark signal",
                "units": "-",
                "unc_comps": [
                    "u_rel_random_dark_signal",
                ],
            },
        )

        datasetl0masked["dark_signal"] = DN_dark

        DN_dark_rand = DatasetUtil.create_unc_variable(
            [len(datasetl0masked["wavelength"]), len(datasetl0masked["scan"])],
            dim_names=["wavelength", "scan"],
            dtype=np.float32,
            attributes={
                "standard_name": "random relative uncertainty on black digital number",
                "long_name": "random relative uncertainty on black digital number",
                "units": "%",
            },
            err_corr=[
                {"dim": "scan", "form": "random", "params": [], "units": []},
                {"dim": "wavelength", "form": "random", "params": [], "units": []},
            ],
        )

        datasetl0masked["u_rel_random_dark_signal"] = DN_dark_rand
        datasetl0masked["dark_signal"].attrs["unc_comps"] = [
            "u_rel_random_dark_signal",
        ]

        # set up arrays for storing the best dark for each scan of the radiance/irradiance
        dark_signals_radscans = np.zeros_like(datasetl0masked["digital_number"].values)
        urand_dark_signals_radscans = np.zeros_like(
            datasetl0masked["digital_number"].values, dtype=np.float32
        )
        dark_outliers_radscans = np.zeros_like(datasetl0masked["quality_flag"].values)

        for i in range(len(series_ids)):
            ids = np.where(datasetl0masked["series_id"] == series_ids[i])[0]
            (
                dark_signal_rad,
                std_dark_signal_rad,
                dark_outlier_rad,
            ) = self.find_nearest_black(
                datasetl0masked_bla,
                datasetl0masked["acquisition_time"].values[ids[0]],
                datasetl0masked["integration_time"].values[ids[0]],
            )
            # plt.plot(dark_signal)
            # plt.savefig("plot_dark_test.png")
            for id in ids:
                (
                    dark_signals_radscans[:, id],
                    urand_dark_signals_radscans[:, id],
                    dark_outliers_radscans[id],
                ) = (
                    dark_signal_rad,
                    np.abs(std_dark_signal_rad / dark_signal_rad * 100),
                    dark_outlier_rad,
                )

        datasetl0masked, mask = self.qual.perform_quality_check_L0A(
            datasetl0masked, series_ids
        )
        datasetl0masked["quality_flag"][
            np.where(dark_outlier_rad == 1)
        ] = DatasetUtil.set_flag(
            datasetl0masked["quality_flag"][np.where(dark_outlier_rad == 1)],
            "dark_masked",
        )  # for i in range(len(mask))]

        # calculate and store random uncertainties on radiance/irradiance
        rand = np.zeros_like(datasetl0masked["digital_number"].values, dtype=np.float32)
        for i in range(len(series_ids)):
            ids = np.where(datasetl0masked["series_id"] == series_ids[i])[0]
            ids_notmasked = np.where(
                (datasetl0masked["series_id"] == series_ids[i]) & (mask == 0)
            )[0]
            if len(ids_notmasked) > 0:
                std = np.std(
                    (
                        datasetl0masked["digital_number"].values[:, ids_notmasked]
                        - dark_signals_radscans[:, ids_notmasked]
                    ),
                    axis=1,
                    dtype=np.float32,
                )
                avg = np.mean(
                    (
                        datasetl0masked["digital_number"].values[:, ids_notmasked]
                        - dark_signals_radscans[:, ids_notmasked]
                    ),
                    axis=1,
                    dtype=np.float32,
                )
                for ii, id in enumerate(ids):
                    rand[:, id] = np.abs(std / avg * 100)
            else:
                for ii, id in enumerate(ids):
                    rand[:, id] = np.nan

        datasetl0masked["u_rel_random_digital_number"].values = rand
        datasetl0masked["dark_signal"].values = dark_signals_radscans
        datasetl0masked["u_rel_random_dark_signal"].values = urand_dark_signals_radscans

        datasetl0masked_bla, mask = self.qual.perform_quality_check_black(
            datasetl0masked_bla, series_ids_bla
        )

        DN_rand_bla = DatasetUtil.create_unc_variable(
            [len(datasetl0masked_bla["wavelength"]), len(datasetl0masked_bla["scan"])],
            dim_names=["wavelength", "scan"],
            dtype=np.float32,
            attributes={
                "standard_name": "random relative uncertainty on black digital number",
                "long_name": "random relative uncertainty on black digital number",
                "units": "%",
            },
            err_corr=[
                {"dim": "scan", "form": "random", "params": [], "units": []},
                {"dim": "wavelength", "form": "random", "params": [], "units": []},
            ],
        )

        datasetl0masked_bla["u_rel_random_digital_number"] = DN_rand_bla

        # now calculate random uncertainties for blacks
        rand = np.zeros_like(datasetl0masked_bla["u_rel_random_digital_number"].values)
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
                    rand[:, id] = np.abs(std / avg * 100)
            else:
                for ii, id in enumerate(ids):
                    rand[:, id] = np.nan

            datasetl0masked_bla["u_rel_random_digital_number"].values = rand

        return datasetl0masked, datasetl0masked_bla
