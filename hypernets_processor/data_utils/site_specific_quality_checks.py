"""
Class to perform site-specific quality checks (i.e. produce L2B data)"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.utils.utils import convert_datetime
from hypernets_processor.data_io.product_name_util import ProductNameUtil

import numpy as np
import warnings
import os
import xarray as xr
import datetime
import math
from scipy.optimize import curve_fit
from scipy.interpolate import LinearNDInterpolator

import scipy
import ast

import punpy
from obsarray.templater.dataset_util import DatasetUtil
import matheo.band_integration as bi

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "18/12/2024"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
postprocessing_path = os.path.join(dir_path, "data", "postprocessing")
irradiance_path = os.path.join(dir_path, "data", "postprocessing", "irradiance_data")
reflectance_bounds_path = os.path.join(
    dir_path, "data", "postprocessing", "qc_reflectance_bounds"
)


class SiteSpecificQualityChecks:
    def __init__(self, context):
        self.context = context
        self.plot = Plotting(context)
        self.writer = HypernetsWriter(context)
        self.pu = ProductNameUtil(context=self.context)
        self.prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"),
            dtype="float32",  # , MCdimlast=True
        )

    def apply_site_specific_QC(self, dataset_l2a, dataset_l1b_rad, dataset_l1b_irr):
        """

        :param dataset_l2a:
        :param dataset_l1b_rad:
        :param dataset_l1b_irr:
        :return:
        """

        # first, we extract all the relevant config values
        deploy_periods = ast.literal_eval(
            self.context.get_config_value("deployment_periods")
        )
        bad_sequences_period = ast.literal_eval(
            self.context.get_config_value("bad_sequences_period")
        )
        limit_tod_period = ast.literal_eval(
            self.context.get_config_value("limit_tod_period")
        )
        max_sza_period = ast.literal_eval(
            self.context.get_config_value("max_sza_period")
        )
        bad_viewing_angles_period = ast.literal_eval(
            self.context.get_config_value("bad_viewing_angles_period")
        )
        bad_solar_angles_period = ast.literal_eval(
            self.context.get_config_value("bad_solar_angles_period")
        )
        bad_relative_angles_period = ast.literal_eval(
            self.context.get_config_value("bad_viewing_angles_period")
        )
        bad_wavelengths_period = ast.literal_eval(
            self.context.get_config_value("bad_wavelengths_period")
        )
        postprocessing_qc_file_period = ast.literal_eval(
            self.context.get_config_value("postprocessing_qc_file_period")
        )

        misalignment_vza = ast.literal_eval(
            self.context.get_config_value("misalignment_vza")
        )
        misalignment_vaa = ast.literal_eval(
            self.context.get_config_value("misalignment_vaa")
        )

        misalignment_vza_unc = ast.literal_eval(
            self.context.get_config_value("misalignment_vza_unc")
        )
        misalignment_vaa_unc = ast.literal_eval(
            self.context.get_config_value("misalignment_vaa_unc")
        )

        misalignment_corr = ast.literal_eval(
            self.context.get_config_value("misalignment_corr")
        )
        misalignment_corr_unc = ast.literal_eval(
            self.context.get_config_value("misalignment_corr_unc")
        )

        # we loop through each of the different deployment periods and identify the applicable one for this sequence
        seq_within_period = False
        i_dep_save = None
        for i_dep in range(len(deploy_periods)):
            # first, we check if this data is within the deployment ranges:
            if convert_datetime(
                dataset_l2a.acquisition_time.values.min()
            ) > convert_datetime(
                deploy_periods[i_dep]["start_date"]
            ) and convert_datetime(
                dataset_l2a.acquisition_time.values.max()
            ) < convert_datetime(
                deploy_periods[i_dep]["stop_date"]
            ):
                seq_within_period = True
                i_dep_save = i_dep

        # anomaly is raised if data has not been found within deployment periods
        if not seq_within_period:
            self.context.anomaly_handler.add_anomaly("per")

        # anomaly is raised if data is within deployment period that is not valid for satellite validation
        if not deploy_periods[i_dep_save]["valid"]:
            self.context.anomaly_handler.add_anomaly("val")

        # anomaly is raised if data is outside time of day limits
        if limit_tod_period[i_dep_save] is not None and (
            (
                convert_datetime(dataset_l2a.acquisition_time.values.max()).time()
                < datetime.time.fromisoformat(limit_tod_period[i_dep_save][0])
            )
            or (
                convert_datetime(dataset_l2a.acquisition_time.values.min()).time()
                > datetime.time.fromisoformat(limit_tod_period[i_dep_save][1])
            )
        ):
            self.context.anomaly_handler.add_anomaly("tod")

        # anomaly is raised if system id does not match hypstar SN in deployment period
        if not dataset_l2a.attrs["system_id"] == "HYPSTAR_" + str(
            deploy_periods[i_dep_save]["HYPSTAR_SN"]
        ):
            self.context.anomaly_handler.add_anomaly("hsn")

        # bad sequences that were manually specified are removed
        if dataset_l2a.attrs["sequence_id"] in bad_sequences_period[i_dep_save]:
            self.context.anomaly_handler.add_anomaly("man")

        if len(dataset_l2a.series)!=len(dataset_l1b_rad.series):
            self.context.anomaly_handler.add_anomaly("wns")

        # Next, remove data for which any of the bad flags was set in previous QC
        bad_flags = [
            "pt_ref_invalid",
            "half_of_scans_masked",
            "not_enough_dark_scans",
            "not_enough_rad_scans",
            "not_enough_irr_scans",
            "no_clear_sky_irradiance",
            "variable_irradiance",
            "half_of_uncertainties_too_big",
            "discontinuity_VNIR_SWIR",
            "single_irradiance_used",
        ]
        flagged = DatasetUtil.get_flags_mask_or(
            dataset_l2a["quality_flag"], bad_flags
        )  # bools for each series if any bad flag is set
        id_series_valid = np.where(~flagged)[
            0
        ]  # select indexes for which no bad flags are set
        dataset_l2b = dataset_l2a.isel(series=id_series_valid)
        dataset_l2b.attrs["product_name"] = self.pu.create_product_name("L_L2B")
        dataset_l2b.attrs["product_level"] = "L_L2B"

        dataset_l1d_rad = dataset_l1b_rad.isel(series=id_series_valid)
        dataset_l1d_rad.attrs["product_name"] = self.pu.create_product_name("L_L1D_RAD")
        dataset_l1d_rad.attrs["product_level"] = "L_L1D_RAD"

        flagged_l1b_irr = DatasetUtil.get_flags_mask_or(
            dataset_l1b_irr["quality_flag"], bad_flags
        )  # bools for each series if any bad flag is set
        id_series_valid_l1b_irr = np.where(~flagged_l1b_irr)[
            0
        ]  # select indexes for which no bad flags are set
        dataset_l1d_irr = dataset_l1b_irr.isel(series=id_series_valid_l1b_irr)
        dataset_l1d_irr.attrs["product_name"] = self.pu.create_product_name("L_L1D_IRR")
        dataset_l1d_irr.attrs["product_level"] = "L_L1D_IRR"

        # next, remove angles for which we know the data is not reliable
        id_series_valid = np.where(
            dataset_l2b.solar_zenith_angle.values < max_sza_period[i_dep_save]
        )[0]
        dataset_l2b = dataset_l2b.isel(series=id_series_valid)
        dataset_l1d_rad = dataset_l1d_rad.isel(series=id_series_valid)

        ang_tol = self.context.get_config_value("angle_tolerance")
        for angle_tup in bad_viewing_angles_period[i_dep_save]:
            bad_vza, bad_vaa = angle_tup
            if bad_vza == "all" or bad_vza == "*":
                cond_vza = np.zeros_like(
                    dataset_l2b.viewing_zenith_angle.values, dtype=bool
                )
            elif isinstance(bad_vza, str) and bad_vza[0] == "<":
                cond_vza = dataset_l2b.viewing_zenith_angle.values >= float(bad_vza[1:])
            elif isinstance(bad_vza, str) and bad_vza[0] == ">":
                cond_vza = dataset_l2b.viewing_zenith_angle.values <= float(bad_vza[1:])
            else:
                cond_vza = (
                    np.abs(dataset_l2b.viewing_zenith_angle.values - bad_vza) > ang_tol
                )

            if bad_vaa == "all" or bad_vaa == "*":
                cond_vaa = np.zeros_like(
                    dataset_l2b.viewing_azimuth_angle.values, dtype=bool
                )
            elif isinstance(bad_vaa, str) and bad_vaa[0] == "<":
                cond_vaa = dataset_l2b.viewing_azimuth_angle.values >= float(
                    bad_vaa[1:]
                )
            elif isinstance(bad_vaa, str) and bad_vaa[0] == ">":
                cond_vaa = dataset_l2b.viewing_azimuth_angle.values <= float(
                    bad_vaa[1:]
                )
            else:
                cond_vaa = (
                    np.abs(dataset_l2b.viewing_azimuth_angle.values - bad_vaa) > ang_tol
                )

            # we only keep data where one of the two conditions is met (the vza or the vaa is good)
            id_series_valid = np.where(cond_vza | cond_vaa)[0]
            dataset_l2b = dataset_l2b.isel(series=id_series_valid)
            dataset_l1d_rad = dataset_l1d_rad.isel(series=id_series_valid)

        for angle_tup in bad_solar_angles_period[i_dep_save]:
            bad_sza, bad_saa = angle_tup
            if bad_sza == "all" or bad_sza == "*":
                cond_sza = np.zeros_like(
                    dataset_l2b.solar_zenith_angle.values, dtype=bool
                )
            elif isinstance(bad_sza, str) and bad_sza[0] == "<":
                cond_sza = dataset_l2b.solar_zenith_angle.values >= float(bad_sza[1:])
            elif isinstance(bad_sza, str) and bad_sza[0] == ">":
                cond_sza = dataset_l2b.solar_zenith_angle.values <= float(bad_sza[1:])
            else:
                cond_sza = (
                    np.abs(dataset_l2b.solar_zenith_angle.values - bad_sza) > ang_tol
                )

            if bad_saa == "all" or bad_saa == "*":
                cond_saa = np.zeros_like(
                    dataset_l2b.solar_azimuth_angle.values, dtype=bool
                )
            elif isinstance(bad_saa, str) and bad_saa[0] == "<":
                cond_saa = dataset_l2b.solar_azimuth_angle.values >= float(bad_vaa[1:])
            elif isinstance(bad_saa, str) and bad_saa[0] == ">":
                cond_saa = dataset_l2b.solar_azimuth_angle.values <= float(bad_vaa[1:])
            else:
                cond_saa = (
                    np.abs(dataset_l2b.solar_azimuth_angle.values - bad_saa) > ang_tol
                )

            # we only keep data where one of the two conditions is met (the sza or the saa is good)
            id_series_valid = np.where(cond_sza | cond_saa)[0]
            dataset_l2b = dataset_l2b.isel(series=id_series_valid)
            dataset_l1d_rad = dataset_l1d_rad.isel(series=id_series_valid)

        raa_ang_tol = self.context.get_config_value("raa_angle_tolerance")
        for angle_tup in bad_relative_angles_period[i_dep_save]:
            bad_vza, bad_raa = angle_tup
            raa = (
                dataset_l2b.viewing_azimuth_angle.values
                - dataset_l2b.solar_azimuth_angle.values
            ) % 360

            if bad_vza == "all" or bad_vza == "*":
                cond_vza = np.zeros_like(
                    dataset_l2b.viewing_zenith_angle.values, dtype=bool
                )
            elif bad_vza == "sza":
                cond_vza = dataset_l2b.viewing_zenith_angle.values > (
                    dataset_l2b.solar_zenith_angle.values + ang_tol
                )
            elif isinstance(bad_vza, str) and bad_vza[0] == "<":
                cond_vza = dataset_l2b.viewing_zenith_angle.values >= float(bad_vza[1:])
            elif isinstance(bad_vza, str) and bad_vza[0] == ">":
                cond_vza = dataset_l2b.viewing_zenith_angle.values <= float(bad_vza[1:])
            else:
                cond_vza = (
                    np.abs(dataset_l2b.viewing_zenith_angle.values - bad_vza) > ang_tol
                )

            if bad_raa == "all" or bad_raa == "*":
                cond_raa = np.zeros_like(raa, dtype=bool)
            elif isinstance(bad_raa, str) and bad_raa[0] == "<":
                cond_raa = raa >= float(bad_raa[1:])
            elif isinstance(bad_raa, str) and bad_raa[0] == ">":
                cond_raa = raa <= float(bad_raa[1:])
            else:
                cond_raa = np.abs(raa - bad_raa) % 360 > raa_ang_tol

            # we only keep data where one of the two conditions is met (the vza or the raa is good)
            id_series_valid = np.where(cond_vza | cond_raa)[0]
            dataset_l2b = dataset_l2b.isel(series=id_series_valid)
            dataset_l1d_rad = dataset_l1d_rad.isel(series=id_series_valid)

        if len(dataset_l2b.series.values) == 0:
            self.context.anomaly_handler.add_anomaly("nos")

        # Then, bad wavelength ranges are omited
        for bad_wav in bad_wavelengths_period[i_dep_save]:
            id_wav_valid = np.where(
                (dataset_l2b.wavelength.values < bad_wav[0])
                | (dataset_l2b.wavelength.values > bad_wav[1])
            )[0]
            dataset_l2b = dataset_l2b.isel(wavelength=id_wav_valid)
            dataset_l1d_rad = dataset_l1d_rad.isel(wavelength=id_wav_valid)

        # Next, the site-specific clear sky check is applied
        irr_model_irrwav = xr.open_dataset(
            os.path.join(
                irradiance_path,
                "%s_clear_sky_medianaod_irrwav.nc"
                % (self.context.get_config_value("site_id")),
            )
        )

        irr_model_irrwav_noaer = xr.open_dataset(
            os.path.join(
                irradiance_path,
                "%s_clear_sky_aod0.0_irrwav.nc"
                % (self.context.get_config_value("site_id")),
            )
        )

        i_wav_550_data = np.argmin(np.abs(dataset_l1b_irr.wavelength.values - 550))
        i_wav_550_model = np.argmin(np.abs(irr_model_irrwav.wavelength.values - 550))
        i_wav_550_model_noaer = np.argmin(
            np.abs(irr_model_irrwav_noaer.wavelength.values - 550)
        )

        for i_series in range(len(dataset_l1b_irr.series.values)):
            sza = dataset_l1b_irr.solar_zenith_angle.values[i_series]
            saa = dataset_l1b_irr.solar_azimuth_angle.values[i_series]
            irradiance, dir_dif_ratio = self.interpolate_irradiance_sza(
                sza, irr_model_irrwav
            )
            irradiance_noaer, _ = self.interpolate_irradiance_sza(
                sza, irr_model_irrwav_noaer
            )
            dir_dif_intfunc = scipy.interpolate.interp1d(
                irr_model_irrwav.wavelength.values,
                dir_dif_ratio,
                fill_value="extrapolate",
            )
            dir_dif_ratio = dir_dif_intfunc(dataset_l1b_irr.wavelength.values)
            # before performing the clear sky check, we perform correction for misalignment
            ratio = self.misalignment_ratio_calculator(
                misalignment_vza[i_dep_save],
                misalignment_vaa[i_dep_save],
                0,
                sza,
                saa,
                misalignment_corr[i_dep_save],
                dir_dif_ratio,
            )
            ratio_unc = self.prop.propagate_systematic(
                self.misalignment_ratio_calculator,
                [
                    misalignment_vza[i_dep_save],
                    misalignment_vaa[i_dep_save],
                    0,
                    sza,
                    saa,
                    misalignment_corr[i_dep_save],
                    dir_dif_ratio,
                ],
                [
                    misalignment_vza_unc[i_dep_save],
                    misalignment_vaa_unc[i_dep_save],
                    None,
                    None,
                    None,
                    misalignment_corr_unc[i_dep_save],
                    None,
                ],
            )
            dataset_l1b_irr.irradiance.values[:, i_series] *= ratio
            dataset_l1b_irr.u_rel_systematic_indep_irradiance.values[:, i_series] = (
                dataset_l1b_irr.u_rel_systematic_indep_irradiance.values[:, i_series]
                ** 2
                + (ratio_unc / ratio / 100) ** 2
            ) ** 0.5

            # clear sky check is performed
            if (
                dataset_l1b_irr.irradiance.values[i_wav_550_data, i_series]
                < 0.9 * irradiance[i_wav_550_model]
            ) or (
                dataset_l1b_irr.irradiance.values[i_wav_550_data, i_series]
                > 1.1 * irradiance_noaer[i_wav_550_model_noaer]
            ):
                self.context.anomaly_handler.add_anomaly("scl")

        # performn correction for reflectance (to account for change in irradiance)
        for i_series in range(len(dataset_l2b.series.values)):
            sza = dataset_l2b.solar_zenith_angle.values[i_series]
            saa = dataset_l2b.solar_azimuth_angle.values[i_series]
            irradiance, dir_dif_ratio = self.interpolate_irradiance_sza(
                sza, irr_model_irrwav
            )
            dir_dif_intfunc = scipy.interpolate.interp1d(
                irr_model_irrwav.wavelength.values,
                dir_dif_ratio,
                fill_value="extrapolate",
            )
            dir_dif_ratio = dir_dif_intfunc(dataset_l2b.wavelength.values)

            # Perform correction for misalignment
            ratio = self.misalignment_ratio_calculator(
                misalignment_vza[i_dep_save],
                misalignment_vaa[i_dep_save],
                0,
                sza,
                saa,
                misalignment_corr[i_dep_save],
                dir_dif_ratio,
            )
            ratio_unc = self.prop.propagate_systematic(
                self.misalignment_ratio_calculator,
                [
                    misalignment_vza[i_dep_save],
                    misalignment_vaa[i_dep_save],
                    0,
                    sza,
                    saa,
                    misalignment_corr[i_dep_save],
                    dir_dif_ratio,
                ],
                [
                    misalignment_vza_unc[i_dep_save],
                    misalignment_vaa_unc[i_dep_save],
                    None,
                    None,
                    None,
                    misalignment_corr_unc[i_dep_save],
                    None,
                ],
            )
            dataset_l2b.reflectance.values[:, i_series] /= ratio
            dataset_l2b.u_rel_systematic_reflectance.values[:, i_series] = (
                dataset_l2b.u_rel_systematic_reflectance.values[:, i_series] ** 2
                + (ratio_unc / ratio / 100) ** 2
            ) ** 0.5

        # next, we check if the reflectances are within the bounds
        if postprocessing_qc_file_period[i_dep_save] is None:
            ds_bounds = None
        else:
            ds_bounds = xr.open_dataset(
                os.path.join(
                    reflectance_bounds_path, postprocessing_qc_file_period[i_dep_save]
                )
            )
            raas = [
                np.array(string.split("_")).astype(float).mean()
                for string in ds_bounds.raa.values
            ]
            raas[-1] = 360
            ds_bounds = ds_bounds.assign_coords(raa=raas)
        i_550 = np.argmin(np.abs(dataset_l2b.wavelength.values - 550))

        sza = dataset_l2b.solar_zenith_angle.values
        saa = dataset_l2b.solar_azimuth_angle.values
        vza = dataset_l2b.viewing_zenith_angle.values
        vaa = dataset_l2b.viewing_azimuth_angle.values

        bounds_down, bounds_up = self.calculate_bounds(ds_bounds, sza, saa, vza, vaa)
        id_series_valid = np.where(
            (dataset_l2b.reflectance.values[i_550, :] < bounds_up)
            & (dataset_l2b.reflectance.values[i_550, :] > bounds_down)
        )[0]
        dataset_l2b = dataset_l2b.isel(series=id_series_valid)
        dataset_l1d_rad = dataset_l1d_rad.isel(series=id_series_valid)

        if len(dataset_l2b.series.values) == 0:
            self.context.anomaly_handler.add_anomaly("nos")

        if len(dataset_l2b.series.values) < 1 / 2 * len(dataset_l2a.series.values):
            self.context.anomaly_handler.add_anomaly("hos")

        # finally, make plots and write file
        if self.context.get_config_value("write_l2b"):
            self.writer.write(
                dataset_l2b,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings_L2"
                ),
            )

        if self.context.get_config_value("write_l1d"):
            self.writer.write(
                dataset_l1d_rad,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings"
                ),
            )
            self.writer.write(
                dataset_l1d_irr,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings"
                ),
            )

        if self.context.get_config_value("plot_l2b"):
            self.plot.plot_series_in_sequence("reflectance", dataset_l2b)
            self.plot.plot_series_in_sequence_vaa("reflectance", dataset_l2b, 98)
            self.plot.plot_series_in_sequence_vza("reflectance", dataset_l2b, 30)
            if self.context.get_config_value("plot_polar_wav") is not None:
                self.plot.plot_polar_reflectance(
                    dataset_l2b, self.context.get_config_value("plot_polar_wav")
                )
            if self.context.get_config_value("plot_polar_ndvi"):
                self.plot.plot_polar_reflectance(dataset_l2b, "ndvi")
            if self.context.get_config_value("plot_uncertainty"):
                self.plot.plot_relative_uncertainty(
                    "reflectance", dataset_l2b, refl=True
                )

            if self.context.get_config_value("plot_correlation"):
                self.plot.plot_correlation("reflectance", dataset_l2b, refl=True)

        if self.context.get_config_value("plot_l1d"):
            self.plot.plot_series_in_sequence("radiance", dataset_l1d_rad)
            self.plot.plot_series_in_sequence("irradiance", dataset_l1d_irr)
            self.plot.plot_series_in_sequence_vaa("radiance", dataset_l1d_rad, 98)
            self.plot.plot_series_in_sequence_vza("radiance", dataset_l1d_rad, 30)

            if self.context.get_config_value("plot_uncertainty"):
                self.plot.plot_relative_uncertainty("radiance", dataset_l1d_rad)
                self.plot.plot_relative_uncertainty("irradiance", dataset_l1d_irr)

            if self.context.get_config_value("plot_correlation"):
                self.plot.plot_correlation("radiance", dataset_l1d_rad)
                self.plot.plot_correlation("irradiance", dataset_l1d_irr)

        return dataset_l2b, dataset_l1d_rad, dataset_l1d_irr

    def interpolate_irradiance_sza(self, sza, ds_irr):
        ds_irr_temp = ds_irr.copy()
        ds_irr_temp["solar_irradiance_BOA"].values = (
            ds_irr_temp["solar_irradiance_BOA"].values
            / np.cos(ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
        )
        ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values = (
            ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values
            / np.cos(ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
        )
        ds_irr_temp = ds_irr_temp.interp(sza=sza, method="linear")
        ds_irr_temp["solar_irradiance_BOA"].values = ds_irr_temp[
            "solar_irradiance_BOA"
        ].values * np.cos(ds_irr_temp["sza"].values / 180 * np.pi)
        ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values = ds_irr_temp[
            "direct_to_diffuse_irradiance_ratio"
        ].values * np.cos(ds_irr_temp["sza"].values / 180 * np.pi)
        return (
            ds_irr_temp["solar_irradiance_BOA"].values,
            ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values,
        )

    def perform_quality_check_angles(
        self, datasetl0, scan_number, vza_abs, vza_ref, paa_abs, paa_ref
    ):
        self.context.logger.debug(
            "vza_ref:{}, vza_abs:{}, paa_ref:{}, paa_abs:{}".format(
                vza_ref, vza_abs, paa_ref, paa_abs
            )
        )

        if (vza_ref == -1 and paa_ref == -1) or (vza_ref <= -999 and paa_ref <= -999):
            self.context.logger.debug(
                "vza_ref and paa_ref are both invalid, using pt_abs instead"
            )
            paa_ref, vza_ref = paa_abs, vza_abs
            datasetl0["quality_flag"].values[scan_number] = DatasetUtil.set_flag(
                datasetl0["quality_flag"][scan_number], "pt_ref_invalid"
            )

        angacc_vza = abs(vza_abs - vza_ref)
        angacc_vaa = abs(paa_abs - paa_ref)

        if angacc_vza > 180:
            angacc_vza = 360 - angacc_vza

        if angacc_vaa > 180:
            angacc_vaa = 360 - angacc_vaa

        self.context.logger.debug(
            "Angle accuracy vza {:.4f} ={:.4f}-{:.4f}".format(
                angacc_vza, vza_abs, vza_ref
            )
        )
        self.context.logger.debug(
            "Angle accuracy vaa {:.4f} ={:.4f}-{:.4f}".format(
                angacc_vaa, paa_abs, paa_ref
            )
        )

        if angacc_vza > self.context.get_config_value("bad_pointing_threshold_zenith"):
            datasetl0["quality_flag"].values[scan_number] = DatasetUtil.set_flag(
                datasetl0["quality_flag"][scan_number], "bad_pointing"
            )
            self.context.logger.warning(
                "Error in Accuracy of tilt is above %s° (vza_abs=%s; vza_ref=%s). Check your system and/or data before processing."
                % (
                    self.context.get_config_value("bad_pointing_threshold_zenith"),
                    vza_abs,
                    vza_ref,
                )
            )
            self.context.anomaly_handler.add_anomaly("a")

        if angacc_vaa > self.context.get_config_value("bad_pointing_threshold_azimuth"):
            datasetl0["quality_flag"].values[scan_number] = DatasetUtil.set_flag(
                datasetl0["quality_flag"][scan_number], "bad_pointing"
            )
            self.context.logger.warning(
                "Error in Accuracy of pan is above %s° (vaa_abs=%s; vaa_ref=%s). Check your system and/or data before processing."
                % (
                    self.context.get_config_value("bad_pointing_threshold_azimuth"),
                    paa_abs,
                    paa_ref,
                )
            )
            self.context.anomaly_handler.add_anomaly("a")

        return datasetl0

    def perform_quality_check_L0A(self, datasetl0, series_ids):
        mask = []
        mask_threshold = []
        mask_outliers = []
        mask_discontinuity = []
        raise_mask_anomaly = False
        for i in range(len(series_ids)):
            ids = np.where(datasetl0["series_id"] == series_ids[i])[0]
            data_subset = datasetl0["digital_number"].values[:, ids]
            intsig = np.nanmean(data_subset, axis=0)
            mask_all_i = np.zeros_like(intsig)  # mask the columns that have NaN
            mask_threshold_i = self.threshold_checks(data_subset)
            mask_outliers_i = self.outlier_checks(data_subset)
            mask_discontinuity_i = self.discontinuity_checks(data_subset)
            mask_all_i[np.where(mask_threshold_i == 1)] = 1
            mask_all_i[np.where(mask_outliers_i == 1)] = 1
            mask_all_i[np.where(mask_discontinuity_i == 1)] = 1

            if all(mask_all_i == 1):
                self.context.logger.warning(
                    "None of the scans for series passed the quality control criteria"
                )
                raise_mask_anomaly = True

            mask = np.append(mask, mask_all_i)
            mask_threshold = np.append(mask_threshold, mask_threshold_i)
            mask_outliers = np.append(mask_outliers, mask_outliers_i)
            mask_discontinuity = np.append(mask_discontinuity, mask_discontinuity_i)
        datasetl0["quality_flag"][np.where(mask_outliers == 1)] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask_outliers == 1)], "outliers"
        )  # for i in range(len(mask))]
        datasetl0["quality_flag"][np.where(mask_threshold == 1)] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask_threshold == 1)], "L0_threshold"
        )  # for i in range(len(mask))]
        datasetl0["quality_flag"][np.where(mask_discontinuity == 1)] = (
            DatasetUtil.set_flag(
                datasetl0["quality_flag"][np.where(mask_discontinuity == 1)],
                "L0_discontinuity",
            )
        )  # for i in range(len(mask))]

        return datasetl0, mask

    def perform_quality_check_black(self, datasetl0, series_ids):
        mask = []
        mask_outliers = []
        mask_threshold = []
        mask_discontinuity = []
        raise_mask_anomaly = False
        for i in range(len(series_ids)):
            ids = np.where(datasetl0["series_id"] == series_ids[i])[0]

            data_subset = datasetl0["digital_number"].values[:, ids]
            intsig = np.nanmean(data_subset, axis=0)
            mask_all_i = np.zeros_like(intsig)  # mask the columns that have NaN
            mask_threshold_i = self.threshold_checks(data_subset)
            mask_outliers_i = self.outlier_checks(data_subset)
            mask_discontinuity_i = self.discontinuity_checks(data_subset)
            mask_all_i[np.where(mask_threshold_i == 1)] = 1
            mask_all_i[np.where(mask_outliers_i == 1)] = 1
            # mask_all_i[np.where(mask_discontinuity_i==1)] = 1

            if all(mask_all_i == 1):
                self.context.logger.warning(
                    "None of the dark scans for series passed the quality control criteria"
                )
                raise_mask_anomaly = True

            mask = np.append(mask, mask_all_i)
            mask_threshold = np.append(mask_threshold, mask_threshold_i)
            mask_outliers = np.append(mask_outliers, mask_outliers_i)
        datasetl0["quality_flag"][np.where(mask == 1)] = DatasetUtil.set_flag(
            datasetl0["quality_flag"][np.where(mask == 1)], "dark_masked"
        )
        # datasetl0["quality_flag"][np.where(mask_threshold == 1)] = DatasetUtil.set_flag(
        #     datasetl0["quality_flag"][np.where(mask_threshold == 1)], "L0_threshold"
        # )  # for i in range(len(mask))]

        return datasetl0, mask

    def perform_quality_check_rand_unc(self, dataset, measurandstring):

        if np.count_nonzero(dataset["u_rel_random_" + measurandstring].values < 0) > 0:
            self.context.anomaly_handler.add_anomaly("u")  # , dataset)

        if (
            np.count_nonzero(dataset["u_rel_random_" + measurandstring].values > 100)
            > 0.5 * dataset["u_rel_random_" + measurandstring].values.size
        ):
            dataset["quality_flag"][:] = DatasetUtil.set_flag(
                dataset["quality_flag"][:], "half_of_uncertainties_too_big"
            )
            self.context.anomaly_handler.add_anomaly("o")  # , dataset)

    def perform_quality_check_comb(
        self, dataset_l1b, dataset_l1b_swir, measurandstring
    ):
        wav_range = 20

        if len(dataset_l1b["series_id"]) != len(dataset_l1b_swir["series_id"]):

            id_series_swir = np.concatenate(
                [
                    np.where(
                        dataset_l1b_swir["series_id"].values
                        == dataset_l1b["series_id"].values[i]
                    )[0]
                    for i in range(len(dataset_l1b["series_id"]))
                ]
            )

            id_series = np.concatenate(
                [
                    np.where(
                        dataset_l1b["series_id"].values
                        == dataset_l1b_swir["series_id"].values[i]
                    )[0]
                    for i in range(len(dataset_l1b_swir["series_id"]))
                ]
            )

            dataset_l1b_swir = dataset_l1b_swir.isel(series=id_series_swir)
            dataset_l1b = dataset_l1b.isel(series=id_series)

        for i in range(len(dataset_l1b["series_id"])):
            if dataset_l1b["series_id"][i] != dataset_l1b_swir["series_id"][i]:
                raise ValueError("Series ID of VNIR and SWIR should be the same!")

            idwav = np.where(
                (dataset_l1b["wavelength"].values < 1000)
                & (dataset_l1b["wavelength"].values > (1000 - wav_range))
            )[0]
            refl_VNIR_edge = np.mean(dataset_l1b[measurandstring][idwav, i])
            idwav_swir = np.where(
                (dataset_l1b_swir["wavelength"].values > 1000)
                & (dataset_l1b_swir["wavelength"].values < (1000 + wav_range))
            )[0]
            refl_SRIW_edge = np.mean(dataset_l1b_swir[measurandstring][idwav_swir, i])
            if (
                2
                * np.abs(refl_VNIR_edge - refl_SRIW_edge)
                / (refl_VNIR_edge + refl_SRIW_edge)
                > self.context.get_config_value("vnir_swir_discontinuity_percent") / 100
            ):
                dataset_l1b["quality_flag"][i] = DatasetUtil.set_flag(
                    dataset_l1b["quality_flag"][i], "discontinuity_VNIR_SWIR"
                )
                dataset_l1b_swir["quality_flag"][i] = DatasetUtil.set_flag(
                    dataset_l1b_swir["quality_flag"][i], "discontinuity_VNIR_SWIR"
                )
        return dataset_l1b, dataset_l1b_swir

    def outlier_checks(self, data_subset, k_unc=3):
        intsig = np.nanmean(data_subset, axis=0)
        mask = np.zeros_like(intsig)  # mask the columns that have NaN
        if len(intsig) > 1:
            noisestd, noiseavg = self.sigma_clip(intsig)
            mask[np.where(np.abs(intsig - noiseavg) >= k_unc * noisestd)] = 1
            mask[np.where(np.abs(intsig - noiseavg) >= 0.25 * intsig)] = 1
        return mask

    def threshold_checks(self, data_subset):
        mask = np.zeros_like(data_subset[0])  # mask the columns that have NaN
        for i in range(len(data_subset[0])):
            if (
                self.context.get_config_value("l0_threshold")
                and np.any(
                    data_subset[:, i] > self.context.get_config_value("l0_threshold")
                )
            ) or np.any(data_subset[:, i] < 0):
                mask[i] = 1
        return mask

    def discontinuity_checks(self, data_subset):
        diff = abs(data_subset[1:, :].astype(int) - data_subset[:-1, :].astype(int))
        mask = np.zeros_like(diff[0])  # mask the columns that have NaN
        for i in range(len(diff[0])):
            if self.context.get_config_value("l0_discontinuity") and np.any(
                diff[:, i] > self.context.get_config_value("l0_discontinuity")
            ):
                mask[i] = 1
        return mask

    def sigma_clip(self, values, tolerance=0.01, median=True, sigma_thresh=3.0):
        # Remove NaNs from input values
        values = np.array(values)
        values = values[np.where(np.isnan(values) == False)]
        values_original = np.copy(values)

        # Continue loop until result converges
        diff = 10e10
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

    # Water based quality checks includes:
    # 1. qc_similarity
    # 2. qc_birds
    # 3. qc_scan: difference at 550 nm (wavelength ref) < 25% (diff_threshold) with neighbours -> if triggered 'temporal variability in Lu, Ed or Ld"
    def qc_similarity(self, L1c):

        wave = L1c["wavelength"]
        wr = L1c.attrs["similarity_waveref"]
        wp = L1c.attrs["similarity_wavethres"]

        epsilon = L1c["epsilon"]
        ## get pixel index for wavelength
        irefr, wrefr = self.rhymershared.closest_idx(wave, wr)

        failSimil = []
        scans = L1c["scan"]
        for i in range(len(scans)):
            data = L1c["reflectance_nosc"].sel(scan=i).values
            if abs(epsilon[i]) > wp * data[irefr]:
                failSimil.append(1)
            else:
                failSimil.append(0)
        return failSimil

    def fitcurve(self, wv, ld, ed):
        def func(x, a, b):
            return a + b * (x / 100) ** (-4)

        if ld.ndim > 1:
            y = np.mean(ld / ed, axis=1)
        else:
            y = ld / ed
        popt, pcov = curve_fit(func, wv, y)
        residuals = y - func(wv, *popt)
        ss_res = np.sum(residuals**2)
        return (popt, pcov, ss_res)

    def qc_bird(self, l1c):
        ld = np.nanmean(l1c.downwelling_radiance.values, axis=1)
        ed = np.mean(l1c.irradiance.values, axis=1)
        wv = l1c.wavelength.values
        popt, pcov, ss_res = self.fitcurve(wv, ld, ed)
        # print("this is ss_res:{}".format(ss_res))
        # popt[0]+popt[1]*(x/100)**(-4)
        # plt.plot(wv, popt[0] + popt[1] * (wv / 100) ** (-4), label="Fitted Curve")

        # sum of squares regression
        # sum of the differences between the predicted value by the model and the mean of the dependent variable
        l1c.attrs["ss_res"] = str(ss_res)
        return l1c

    def qc_scan(self, dataset, measurandstring, dataset_l1b):
        ## no inclination
        ## difference at 550 nm < 25% with neighbours
        ##
        ## QV July 2018
        ## Last modifications: 2019-07-10 (QV) renamed from PANTR, integrated in rhymer
        # Modified 10/09/2020 by CG for the PANTHYR
        verbosity = self.context.get_config_value("verbosity")
        series_id = np.unique(dataset["series_id"])
        wave = dataset["wavelength"].values
        flags = np.zeros(shape=len(dataset["scan"]))
        id = 0
        for s in series_id:

            scans = dataset["scan"][dataset["series_id"] == s]

            ##
            n = len(scans)
            ## get pixel index for wavelength
            iref, wref = self.rhymershared.closest_idx(
                wave, self.context.get_config_value("diff_wave")
            )

            cos_sza = []
            for i in dataset["solar_zenith_angle"].sel(scan=scans).values:
                cos_sza.append(math.cos(math.radians(i)))

            ## go through the current set of scans
            for i in range(n):
                ## test inclination
                ## not done

                if measurandstring == "irradiance":
                    data = dataset["irradiance"].sel(scan=scans).T.values
                    ## test variability at 550 nm
                    if i == 0:
                        v = abs(
                            1
                            - (
                                (data[i][iref] / cos_sza[i])
                                / (data[i + 1][iref] / cos_sza[i + 1])
                            )
                        )
                    elif i < n - 1:
                        v = max(
                            abs(
                                1
                                - (
                                    (data[i][iref] / cos_sza[i])
                                    / (data[i + 1][iref] / cos_sza[i + 1])
                                )
                            ),
                            abs(
                                1
                                - (
                                    (data[i][iref] / cos_sza[i])
                                    / (data[i - 1][iref] / cos_sza[i - 1])
                                )
                            ),
                        )
                    else:
                        v = abs(
                            1
                            - (
                                (data[i][iref] / cos_sza[i])
                                / (data[i - 1][iref] / cos_sza[i - 1])
                            )
                        )
                else:
                    data = dataset["radiance"].sel(scan=scans).T.values
                    ## test variability at 550 nm
                    if i == 0:
                        v = abs(1 - (data[i][iref] / data[i + 1][iref]))
                    elif i < n - 1:
                        v = max(
                            abs(1 - (data[i][iref] / data[i + 1][iref])),
                            abs(1 - (data[i][iref] / data[i - 1][iref])),
                        )
                    else:
                        v = abs(1 - (data[i][iref] / data[i - 1][iref]))

                ## continue if value exceeds the cv threshold
                if v > self.context.get_config_value("diff_threshold"):
                    if measurandstring == "irradiance":
                        flags[id] = 1
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = (
                            DatasetUtil.set_flag(
                                dataset_l1b["quality_flag"][
                                    np.where(dataset_l1b["scan"] == i)
                                ],
                                "temp_variability_irr",
                            )
                        )

                    else:
                        flags[id] = 1
                        dataset_l1b["quality_flag"][dataset_l1b["scan"] == i] = (
                            DatasetUtil.set_flag(
                                dataset_l1b["quality_flag"][
                                    np.where(dataset_l1b["scan"] == i)
                                ],
                                "temp_variability_rad",
                            )
                        )

                    seq = dataset.attrs["sequence_id"]
                    ts = datetime.datetime.utcfromtimestamp(
                        dataset["acquisition_time"][i]
                    )

                    if verbosity > 2:
                        self.context.logger.info(
                            "Temporal jump: in {}:  Aquisition time {}:, {}".format(
                                seq,
                                ts,
                                ", ".join(
                                    [
                                        "{}:{}:{}".format(
                                            k,
                                            dataset[k][scans[i]].values,
                                            dataset[k][scans[i]].values,
                                            dataset[k][scans[i]].values,
                                        )
                                        for k in [
                                            "scan",
                                            "series_id",
                                            "viewing_zenith_angle",
                                            "quality_flag",
                                        ]
                                    ]
                                ),
                            )
                        )
                id += 1

            return dataset_l1b, flags

    def misalignment_ratio_calculator(
        self, vza, vaa, offset, sza, saa, corr, direct_to_diffuse=1000
    ):
        if isinstance(vza, np.ndarray):
            vaa[vza < 0] += -180
            vza[vza < 0] = -vza[vza < 0]

        elif vza < 0:
            vza = -vza
            vaa += -180

        sza = np.radians(sza)
        saa = np.radians(saa)
        vza = np.radians(vza)
        vaa = np.radians(vaa)
        new_sza = np.arccos(
            np.cos(sza) * np.cos(vza) + np.sin(sza) * np.sin(vza) * np.cos((saa - vaa))
        )
        new_direct_to_diffuse = direct_to_diffuse * np.cos(new_sza) / np.cos(sza)
        return ((new_direct_to_diffuse + 1) / (direct_to_diffuse + 1) + offset) / corr

    def calculate_bounds(self, refl_bounds_ds, sza, saa, vza, vaa):
        if refl_bounds_ds is not None:
            raa = (vaa - saa) % 360
            sza_bounds = refl_bounds_ds.sza.values.flatten()
            vza_bounds = refl_bounds_ds.vza.values.flatten()
            raa_bounds = np.repeat(
                refl_bounds_ds.raa.values, refl_bounds_ds.sza.values.shape[1]
            )
            lower_bounds = refl_bounds_ds.lower_bound.values.flatten()
            upper_bounds = refl_bounds_ds.upper_bound.values.flatten()
            id_360 = np.where(raa_bounds == 360)[0]
            sza_bounds = np.concatenate([sza_bounds[id_360], sza_bounds])
            vza_bounds = np.concatenate([vza_bounds[id_360], vza_bounds])
            raa_bounds = np.concatenate([np.zeros_like(raa_bounds[id_360]), raa_bounds])
            lower_bounds = np.concatenate([lower_bounds[id_360], lower_bounds])
            upper_bounds = np.concatenate([upper_bounds[id_360], upper_bounds])
            id_valid = np.where(np.isfinite(lower_bounds))[0]
            # id_valid = np.where((np.isfinite(lower_bounds)) & (sza_bounds < 30) & (vza_bounds < 15))[0]

            lower_interp = LinearNDInterpolator(
                list(
                    zip(
                        sza_bounds[id_valid], vza_bounds[id_valid], raa_bounds[id_valid]
                    )
                ),
                lower_bounds[id_valid],
            )
            upper_interp = LinearNDInterpolator(
                list(
                    zip(
                        sza_bounds[id_valid], vza_bounds[id_valid], raa_bounds[id_valid]
                    )
                ),
                upper_bounds[id_valid],
            )
            # print(sza[20],vza[20],raa[20], lower_interp(sza[20],vza[20],raa[20]), lower_bounds[id_valid])

            return lower_interp(sza, vza, raa), upper_interp(sza, vza, raa)
        else:
            return 0.0, 1.1
