"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_utils.quality_checks import QualityChecks
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import (
    MeasurementFunctionFactory,
)

import time
import numpy as np
from obsarray.templater.dataset_util import DatasetUtil
import datetime

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class Average:
    def __init__(self, context):
        self.templ = DataTemplates(context=context)
        self.context = context
        self.qual = QualityChecks(context)
        self.writer = HypernetsWriter(context)
        self._measurement_function_factory = MeasurementFunctionFactory

    def average_l0(self, measurandstring, dataset_l0, dataset_l0_bla, swir=False):
        """

        :param measurandstring:
        :type measurandstring:
        :param dataset_l0:
        :type dataset_l0:
        :param dataset_l0_bla:
        :type dataset_l0_bla:
        :param calibration_data:
        :type calibration_data:
        :return:
        :rtype:
        """

        #first check if the blacks and radiance/irradiance have matching series_id
        if len(np.unique(dataset_l0_bla["series_id"])) != len(
            np.unique(dataset_l0["series_id"])
        ) or not all(
            [
                np.unique(dataset_l0["series_id"])[i] + 1
                == np.unique(dataset_l0_bla["series_id"])[i]
                for i in range(len(np.unique(dataset_l0["series_id"])))
            ]
        ):
            self.context.logger.warning(
                "The dark series_id did not match the expected series_id from (ir)radiance"
            )
            dataset_l0, dataset_l0_bla = self.remove_missing_series(
                dataset_l0, dataset_l0_bla
            )

        #create template dataset
        dataset_l0b = self.templ.l0b_template_from_l0a_dataset(
            measurandstring, dataset_l0, swir=swir
        )

        #first do fast averaging of 1d variables
        flags = ["outliers", "L0_thresholds", "L0_discontinuity", "bad_pointing"]

        flagged = DatasetUtil.get_flags_mask_or(
            dataset_l0["quality_flag"], flags
        )

        flags_ds = DatasetUtil.unpack_flags(dataset_l0["quality_flag"])
        mask_flags = np.array([flags_ds[flag].values for flag in flags_ds.data_vars])

        series_id = np.unique(dataset_l0["series_id"])

        for i in range(len(series_id)):
            ids = np.where(
                dataset_l0["series_id"] == series_id[i]
            )

            ids_flagged = np.where(
                (dataset_l0["series_id"] == series_id[i]) & (flagged == False)
            )

            for variablestring in dataset_l0.keys():
                if variablestring=="series_id":
                    dataset_l0b[variablestring].values[i] = series_id[i]

                elif variablestring=="quality_flag":
                    #set quality flag of series if any of quality flag of scan has been raised
                    dataset_l0b[variablestring].values[i] = sum([2**i for i,n in enumerate(
                        np.logical_or.reduce(mask_flags[:,ids].T)[0]) if n])

                elif (dataset_l0[variablestring].dims == ("scan",)) and (
                        variablestring in dataset_l0b.keys()
                ):
                    dataset_l0b[variablestring].values[i] = np.mean(dataset_l0[variablestring].values[ids_flagged])

        #next 2d variables are averaged
        for variablestring in dataset_l0b.variables:
            if variablestring == "digital_number":
                measurand, measurand_std, n_valid, n_total = self.calc_mean_masked(
                    dataset_l0,
                    "digital_number",
                    flags,
                    return_std=True,
                    return_total=True,
                )
                dataset_l0b["digital_number"].values = measurand
                dataset_l0b["std_digital_number"].values = measurand_std.astype(
                    dataset_l0b["std_digital_number"].values.dtype
                )
                dataset_l0b["n_valid_scans"].values = n_valid.astype(
                    dataset_l0b["n_valid_scans"].values.dtype
                )
                dataset_l0b["n_total_scans"].values = n_total.astype(
                    dataset_l0b["n_total_scans"].values.dtype
                )
                for i in range(len(n_valid)):
                    if n_valid[i] < 0.5 * n_total[i]:
                        dataset_l0b["quality_flag"][i] = DatasetUtil.set_flag(
                            dataset_l0b["quality_flag"][i], "half_of_scans_masked"
                        )
                dataset_l0b = self.qual.check_valid_scans(
                    dataset_l0b, n_valid, n_total, measurandstring
                )

            elif variablestring == "dark_signal":
                measurand, measurand_std, n_valid, n_total = self.calc_mean_masked(
                    dataset_l0_bla,
                    "digital_number",
                    flags,
                    return_std=True,
                    return_total=True,
                )
                dataset_l0b["dark_signal"].values = measurand
                dataset_l0b["std_dark_signal"].values = measurand_std.astype(
                    dataset_l0b["std_dark_signal"].values.dtype
                )
                dataset_l0b = self.qual.check_valid_darks(dataset_l0b, n_valid, n_total)

            elif variablestring == "u_rel_random_dark_signal":
                dataset_l0b["u_rel_random_dark_signal"].values = self.calc_mean_masked(
                    dataset_l0_bla, "u_rel_random_digital_number", flags, rand_unc=True
                )
            elif "u_rel_random" in variablestring:
                dataset_l0b[variablestring].values = self.calc_mean_masked(
                    dataset_l0, variablestring, flags, rand_unc=True
                )
            elif "err_corr_" in variablestring:
                dataset_l0b[variablestring].values = dataset_l0[variablestring].values

        return dataset_l0b

    def average_l1a(self, measurandstring, dataset_l1a):
        dataset_l1b = self.templ.l1b_template_from_l1a_dataset_water(
            measurandstring, dataset_l1a
        )

        # first do fast averaging of 1d variables
        flags = ["outliers", "L0_thresholds", "L0_discontinuity", "bad_pointing"]

        flagged = DatasetUtil.get_flags_mask_or(
            dataset_l1a["quality_flag"], flags
        )

        flags_ds = DatasetUtil.unpack_flags(dataset_l1a["quality_flag"])
        mask_flags = np.array([flags_ds[flag].values for flag in flags_ds.data_vars])

        series_id = np.unique(dataset_l1a["series_id"])

        for i in range(len(series_id)):
            ids = np.where(
                dataset_l1a["series_id"] == series_id[i]
            )

            ids_flagged = np.where(
                (dataset_l1a["series_id"] == series_id[i]) & (flagged == False)
            )

            for variablestring in dataset_l1a.keys():
                if variablestring == "series_id":
                    dataset_l1b[variablestring].values[i] = series_id[i]

                elif variablestring == "quality_flag":
                    # set quality flag of series if any of quality flag of scan has been raised
                    dataset_l1b[variablestring].values[i] = sum(
                        [2 ** i for i, n in enumerate(np.logical_or.reduce(mask_flags[:, ids].T)[0]) if n])

                elif (dataset_l1a[variablestring].dims == ("scan",)) and (
                        variablestring in dataset_l1b.keys()
                ):
                    dataset_l1b[variablestring].values[i] = np.mean(dataset_l1a[variablestring].values[ids_flagged])

        #next 2d variables are averaged
        for var in dataset_l1b.variables:
            if var == measurandstring:
                measurand, measurand_std, n_valid, n_total = self.calc_mean_masked(
                    dataset_l1a,
                    measurandstring,
                    flags,
                    return_std=True,
                    return_total=True,
                )
                dataset_l1b[measurandstring].values = measurand
                dataset_l1b["std_" + measurandstring].values = measurand_std.astype(
                    dataset_l1b["std_" + measurandstring].values.dtype
                )
                dataset_l1b["n_valid_scans"].values = n_valid.astype(
                    dataset_l1b["n_valid_scans"].values.dtype
                )
                dataset_l1b["n_total_scans"].values = n_total.astype(
                    dataset_l1b["n_total_scans"].values.dtype
                )

            elif measurandstring in var:
                if "u_rel_random" in var:
                    if self.context.get_config_value("mcsteps")>0:
                        dataset_l1b[var].values = self.calc_mean_masked(
                            dataset_l1a, var, flags, rand_unc=True
                        )
                elif "u_rel_" in var:
                    if self.context.get_config_value("mcsteps")>0:
                        dataset_l1b[var].values = self.calc_mean_masked(
                            dataset_l1a, var, flags
                        )
                elif "err_corr_" in var:
                    if self.context.get_config_value("mcsteps")>0:
                        dataset_l1b[var].values = dataset_l1a[var].values
                elif (not "std" in var) and (not "n_valid" in var):
                    dataset_l1b[var].values = self.calc_mean_masked(
                        dataset_l1a, var, flags
                    )

        return dataset_l1b

    def average_L2(self, dataset, razangle=None):
        # flags = ["saturation","nonlinearity","bad_pointing","outliers",
        #                  "angles_missing","lu_eq_missing","rhof_angle_missing",
        #                  "rhof_default","temp_variability_irr","temp_variability_rad",
        #                  "min_nbred","min_nbrlu","min_nbrlsky", "simil_fail"]

        flags = [
            "bad_pointing",
            "outliers",
            "L0_thresholds",
            "L0_discontinuity",
            "rhof_angle_missing",
            "temp_variability_irr",
            "temp_variability_rad",
        ]

        dataset_l2a = self.templ.l2_from_l1c_dataset(dataset, razangle)

        # first do fast averaging of 1d variables

        flagged = DatasetUtil.get_flags_mask_or(
            dataset["quality_flag"], flags
        )

        flags_ds = DatasetUtil.unpack_flags(dataset["quality_flag"])
        mask_flags = np.array([flags_ds[flag].values for flag in flags_ds.data_vars])

        series_id = np.unique(dataset["series_id"])

        for i in range(len(series_id)):
            ids = np.where(
                dataset["series_id"] == series_id[i]
            )

            ids_flagged = np.where(
                (dataset["series_id"] == series_id[i]) & (flagged == False)
            )

            for variablestring in dataset.keys():
                if variablestring == "series_id":
                    dataset_l2a[variablestring].values[i] = series_id[i]

                elif variablestring == "quality_flag":
                    # set quality flag of series if any of quality flag of scan has been raised
                    dataset_l2a[variablestring].values[i] = sum(
                        [2 ** i for i, n in enumerate(np.logical_or.reduce(mask_flags[:, ids].T)[0]) if n])

                elif (dataset[variablestring].dims == ("scan",)) and (
                        variablestring in dataset_l2a.keys()
                ):
                    dataset_l2a[variablestring].values[i] = np.mean(dataset[variablestring].values[ids_flagged])

        # next 2d variables are averaged
        measurand, measurand_std, n_valid, n_total = self.calc_mean_masked(
            dataset, "water_leaving_radiance", flags, return_std=True, return_total=True
        )
        dataset_l2a["water_leaving_radiance"].values = measurand
        dataset_l2a["std_water_leaving_radiance"].values = measurand_std.astype(
            dataset_l2a["std_water_leaving_radiance"].values.dtype
        )
        dataset_l2a["n_valid_scans"].values = n_valid.astype(
            dataset_l2a["n_valid_scans"].values.dtype
        )
        dataset_l2a["n_total_scans"].values = n_total.astype(
            dataset_l2a["n_total_scans"].values.dtype
        )
        if self.context.get_config_value("mcsteps") > 0:
            dataset_l2a[
                "u_rel_random_water_leaving_radiance"
            ].values = self.calc_mean_masked(
                dataset, "u_rel_random_water_leaving_radiance", flags, rand_unc=True
            )
            dataset_l2a[
                "u_rel_systematic_indep_water_leaving_radiance"
            ].values = self.calc_mean_masked(
                dataset, "u_rel_systematic_indep_water_leaving_radiance", flags
            )
            dataset_l2a[
                "err_corr_systematic_indep_water_leaving_radiance"
            ].values = dataset["err_corr_systematic_indep_water_leaving_radiance"].values
            dataset_l2a[
                "u_rel_systematic_corr_rad_irr_water_leaving_radiance"
            ].values = self.calc_mean_masked(
                dataset, "u_rel_systematic_corr_rad_irr_water_leaving_radiance", flags
            )
            dataset_l2a[
                "err_corr_systematic_corr_rad_irr_water_leaving_radiance"
            ].values = dataset[
                "err_corr_systematic_corr_rad_irr_water_leaving_radiance"
            ].values

        for measurandstring in ["reflectance_nosc", "reflectance", "epsilon"]:
            measurand, measurand_std, n_valid, n_total = self.calc_mean_masked(
                dataset, measurandstring, flags, return_std=True, return_total=True
            )
            dataset_l2a[measurandstring].values = measurand
            dataset_l2a["std_" + measurandstring].values = measurand_std.astype(
                dataset_l2a["std_" + measurandstring].values.dtype
            )
            dataset_l2a["n_valid_scans"].values = n_valid.astype(
                dataset_l2a["n_valid_scans"].values.dtype
            )
            dataset_l2a["n_total_scans"].values = n_total.astype(
                dataset_l2a["n_total_scans"].values.dtype
            )
            if self.context.get_config_value("mcsteps") > 0:
                dataset_l2a[
                    "u_rel_random_" + measurandstring
                ].values = self.calc_mean_masked(
                    dataset, "u_rel_random_" + measurandstring, flags, rand_unc=True
                )
                dataset_l2a[
                    "u_rel_systematic_" + measurandstring
                ].values = self.calc_mean_masked(
                    dataset, "u_rel_systematic_" + measurandstring, flags
                )
                if not measurandstring == "epsilon":
                    dataset_l2a["err_corr_systematic_" + measurandstring].values = dataset[
                        "err_corr_systematic_" + measurandstring
                    ].values

        return dataset_l2a

    def remove_missing_series(self, dataset, dataset_bla):
        """

        :param dataset:
        :param dataset_bla:
        :return:
        """
        series_id = np.unique(dataset["series_id"])
        series_id_bla = np.unique(dataset_bla["series_id"])
        scan_found = []
        scan_bla_found = []
        for i in range(len(series_id)):
            if series_id[i] + 1 in series_id_bla:
                scan_found.extend(
                    list(np.where(dataset["series_id"] == series_id[i])[0])
                )
        for i in range(len(series_id_bla)):
            if series_id_bla[i] - 1 in series_id:
                scan_bla_found.extend(
                    list(np.where(dataset_bla["series_id"] == series_id_bla[i])[0])
                )
        dataset = dataset.isel(scan=scan_found)
        dataset_bla = dataset_bla.isel(scan=scan_bla_found)
        return dataset, dataset_bla

    def calc_mean_masked(
        self,
        dataset,
        var,
        flags,
        rand_unc=False,
        corr=False,
        return_std=False,
        return_total=False,
    ):
        """

        :param dataset:
        :type dataset:
        :param var:
        :type var:
        :param flags:
        :type flags:
        :param rand_unc:
        :type rand_unc:
        :param corr:
        :type corr:
        :return:
        :rtype:
        """
        series_id = np.unique(dataset["series_id"])
        vals = dataset[var].values
        flagged = DatasetUtil.get_flags_mask_or(dataset["quality_flag"], flags)

        if corr:
            out = np.empty(
                (
                    len(series_id),
                    len(dataset["wavelength"]),
                    len(dataset["wavelength"]),
                ),
                dtype=dataset[var].values.dtype,
            )
            for i in range(len(series_id)):
                ids = np.where(
                    (dataset["series_id"] == series_id[i]) & (flagged == False)
                )
                out[i] = np.mean(vals[:, :, ids], axis=3)[:, :, 0]

            out = np.mean(out, axis=0)

        elif vals.ndim == 1:
            out = np.empty((len(series_id),), dtype=dataset[var].values.dtype)
            if return_std:
                out_std = np.empty((len(series_id),), dtype=np.float32)
                n_valid = np.empty((len(series_id),), dtype=np.uint8)
                n_total = np.empty((len(series_id),), dtype=np.uint8)

            for i in range(len(series_id)):
                ids = np.where(
                    (dataset["series_id"] == series_id[i]) & (flagged == False)
                )
                ids_total = np.where((dataset["series_id"] == series_id[i]))
                out[i] = np.mean(dataset[var].values[ids])
                if return_std:
                    out_std[i] = np.std(dataset[var].values[ids])
                    n_valid[i] = len(ids[0])
                    n_total[i] = len(ids_total[0])
                if rand_unc:
                    out[i] = (np.sum(dataset[var].values[ids] ** 2)) ** 0.5 / len(
                        ids[0]
                    )
        else:
            out = np.empty(
                (len(series_id), len(dataset["wavelength"])),
                dtype=dataset[var].values.dtype,
            )
            if return_std:
                out_std = np.empty(
                    (len(series_id), len(dataset["wavelength"])), dtype=np.float32
                )
                n_valid = np.empty((len(series_id),), dtype=np.uint8)
                n_total = np.empty((len(series_id),), dtype=np.uint8)

            for i in range(len(series_id)):
                ids = np.where(
                    (dataset["series_id"] == series_id[i]) & (flagged == False)
                )
                ids_total = np.where((dataset["series_id"] == series_id[i]))
                out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]
                if return_std:
                    out_std[i] = np.std(dataset[var].values[:, ids], axis=2)[:, 0]
                    n_valid[i] = len(ids[0])
                    n_total[i] = len(ids_total[0])

                if rand_unc:
                    out[i] = (
                        np.sum(dataset[var].values[:, ids] ** 2, axis=2)[:, 0]
                    ) ** 0.5 / len(ids[0])

        if return_std:
            if return_total:
                return out.T, out_std.T, n_valid, n_total
            else:
                return out.T, out_std.T, n_valid
        else:
            return out.T

    def calc_std_masked(self, dataset, var, flags, rand_unc=False, corr=False):
        series_id = np.unique(dataset["series_id"])

        out = np.empty((len(series_id), len(dataset["wavelength"])))

        for i in range(len(series_id)):
            flagged = np.any(
                [DatasetUtil.unpack_flags(dataset["quality_flag"])[x] for x in flags],
                axis=0,
            )
            ids = np.where((dataset["series_id"] == series_id[i]) & (flagged == False))
            out[i] = np.std(dataset[var].values[:, ids], axis=2)[:, 0]

        return out.T
