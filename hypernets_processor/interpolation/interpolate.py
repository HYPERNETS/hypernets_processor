"""
Interpolation class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.interpolation.measurement_functions.interpolation_factory import (
    InterpolationFactory,
)
from hypernets_processor.data_utils.quality_checks import QualityChecks
from obsarray.templater.dataset_util import DatasetUtil
import numpy as np
import punpy

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class Interpolate:
    def __init__(self, context, parallel_cores=1):
        self._measurement_function_factory = InterpolationFactory
        self.qual = QualityChecks(context)
        self.templ = DataTemplates(context=context)
        self.writer = HypernetsWriter(context)
        self.plot = Plotting(context)
        self.context = context

    def interpolate_l1b_w(
        self,
        dataset_l1c_int,
        dataset_l1a_uprad,
        dataset_l1b_downrad,
        dataset_l1b_irr,
        azangle=None,
    ):

        # chek for upwelling radiance
        upscan = [
            i
            for i, e in enumerate(dataset_l1a_uprad["viewing_zenith_angle"].values)
            if e < 90
        ]

        dataset_l1c_int.assign_coords(wavelength=dataset_l1a_uprad["wavelength"].values)
        dataset_l1c_int["upwelling_radiance"].values = (
            dataset_l1a_uprad["radiance"].sel(scan=upscan).values
        )
        dataset_l1c_int["acquisition_time"].values = (
            dataset_l1a_uprad["acquisition_time"].sel(scan=upscan).values
        )
        if self.context.get_config_value("mcsteps") > 0:
            dataset_l1c_int["u_rel_random_upwelling_radiance"].values = (
                dataset_l1a_uprad["u_rel_random_radiance"].sel(scan=upscan).values
            )
            dataset_l1c_int["u_rel_systematic_indep_upwelling_radiance"].values = (
                dataset_l1a_uprad["u_rel_systematic_indep_radiance"]
                .sel(scan=upscan)
                .values
            )
            dataset_l1c_int[
                "u_rel_systematic_corr_rad_irr_upwelling_radiance"
            ].values = (
                dataset_l1a_uprad["u_rel_systematic_corr_rad_irr_radiance"]
                .sel(scan=upscan)
                .values
            )
            dataset_l1c_int[
                "err_corr_systematic_indep_upwelling_radiance"
            ].values = dataset_l1a_uprad["err_corr_systematic_indep_radiance"].values
            dataset_l1c_int[
                "err_corr_systematic_corr_rad_irr_upwelling_radiance"
            ].values = dataset_l1a_uprad[
                "err_corr_systematic_corr_rad_irr_radiance"
            ].values

        if self.context.logger is not None:
            self.context.logger.info("interpolate irradiance")
        else:
            print("interpolate irradiance")
        dataset_l1c_int = self.interpolate_irradiance(
            dataset_l1c_int, dataset_l1b_irr, azangle
        )

        if self.context.logger is not None:
            self.context.logger.info("interpolate sky radiance")
        else:
            print("interpolate sky radiance")

        dataset_l1c_int = self.interpolate_skyradiance(
            dataset_l1c_int, dataset_l1b_downrad
        )
        return dataset_l1c_int

    def interpolate_l1c(
        self, dataset_l1b_rad, dataset_l1b_irr
    ):  # used for land processing

        self.qual.check_valid_sequence_land(dataset_l1b_rad, dataset_l1b_irr)

        dataset_l1c = self.templ.l1c_from_l1b_dataset(dataset_l1b_rad)
        dataset_l1c["acquisition_time"].values = dataset_l1b_rad[
            "acquisition_time"
        ].values

        # dataset_l1b_rad,dataset_l1b_irr=self.qual.perform_quality_check_interpolate(dataset_l1b_rad,dataset_l1b_irr)

        dataset_l1c = self.interpolate_irradiance(dataset_l1c, dataset_l1b_irr)

        if self.context.get_config_value("write_l1c"):
            self.writer.write(
                dataset_l1c,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings"
                ),
            )

        if self.context.get_config_value("plot_l1c"):
            self.plot.plot_series_in_sequence("irradiance", dataset_l1c)

        if self.context.get_config_value("plot_uncertainty"):
            self.plot.plot_relative_uncertainty("irradiance", dataset_l1c)

        if self.context.get_config_value("plot_correlation"):
            self.plot.plot_correlation("irradiance", dataset_l1c)

        return dataset_l1c

    def interpolate_irradiance(self, dataset_l1c, dataset_l1b_irr, razangle=None):

        dataset_l1c=self.qual.check_overcast(dataset_l1c,dataset_l1b_irr)
        flags = [
            "vza_irradiance",
            "not_enough_dark_scans",
            "not_enough_irr_scans",
        ]

        flagged = DatasetUtil.get_flags_mask_or(dataset_l1b_irr["quality_flag"], flags)
        mask_notflagged = np.where(flagged == False)[0]
        if len(mask_notflagged) == 0:
            raise ValueError("one of the quality checks in previous steps has failed, and not correctly picked up that there is no valid irradiance")

        measurement_function_interpolate_wav = self.context.get_config_value(
            "measurement_function_interpolate_wav"
        )
        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32", parallel_cores=1, verbose=False
        )
        if self.context.get_config_value("network") == "w":
            interpolation_function_wav = self._measurement_function_factory(
                prop=prop, corr_dims="wavelength", yvariable="irradiance"
            ).get_measurement_function(measurement_function_interpolate_wav)
        else:
            interpolation_function_wav = self._measurement_function_factory(
                prop=prop, repeat_dims="series", yvariable="irradiance"
            ).get_measurement_function(measurement_function_interpolate_wav)

        interpolation_function_wav.setup(
            np.nanmean(dataset_l1b_irr["solar_zenith_angle"].values),
            self.context.get_config_value("network"),
            dataset_l1b_irr["wavelength"].values,
        )

        dataset_l1c_temp = self.templ.l1ctemp_dataset(
            dataset_l1c, dataset_l1b_irr, razangle
        )
        if self.context.get_config_value("mcsteps") > 0:
            dataset_l1c_temp = interpolation_function_wav.propagate_ds_specific(
                ["random", "systematic_indep", "systematic_corr_rad_irr"],
                dataset_l1c.rename({"wavelength": "radiance_wavelength"}),
                dataset_l1b_irr,
                ds_out_pre=dataset_l1c_temp,
                use_ds_out_pre_unmodified=True,
                store_unc_percent=True,
            )
        else:
            measurandstring = 'irradiance'
            measurand = interpolation_function_wav.run(
                dataset_l1c.rename({"wavelength": "radiance_wavelength"}),
                dataset_l1b_irr)
            dataset_l1c_temp[measurandstring].values = measurand
            dataset_l1c_temp = dataset_l1c_temp.drop(
                [
                    "u_rel_random_" + measurandstring,
                    "u_rel_systematic_indep_" + measurandstring,
                    "u_rel_systematic_corr_rad_irr_" + measurandstring,
                    "err_corr_systematic_indep_" + measurandstring,
                    "err_corr_systematic_corr_rad_irr_" + measurandstring,
                ]
            )

        measurement_function_interpolate_time = self.context.get_config_value(
            "measurement_function_interpolate_time"
        )
        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32", parallel_cores=1
        )
        interpolation_function_time = self._measurement_function_factory(
            prop=prop,
            corr_dims="wavelength",
            yvariable="irradiance",
            use_err_corr_dict=True,
        ).get_measurement_function(measurement_function_interpolate_time)

        # Interpolate in time to radiance times
        acqui_rad = dataset_l1c["acquisition_time"].values
        output_sza = dataset_l1c["solar_zenith_angle"].values
        input_sza = dataset_l1b_irr["solar_zenith_angle"].values

        if self.context.get_config_value("network") == "w":
            dataset_l1c_temp = dataset_l1c_temp.isel(scan=mask_notflagged)
            acqui_irr = dataset_l1b_irr["acquisition_time"].values[mask_notflagged]
        else:
            dataset_l1c_temp = dataset_l1c_temp.isel(series=mask_notflagged)
            acqui_irr = dataset_l1b_irr["acquisition_time"].values[mask_notflagged]

        if self.context.get_config_value("mcsteps") > 0:
            dataset_l1c = interpolation_function_time.propagate_ds_specific(
                ["random", "systematic_indep", "systematic_corr_rad_irr"],
                dataset_l1c_temp,
                {
                    "input_time": acqui_irr,
                    "output_time": acqui_rad,
                    "input_sza": input_sza,
                    "output_sza": output_sza,
                },
                ds_out_pre=dataset_l1c,
                store_unc_percent=True,
            )
        else:
            measurandstring = 'irradiance'
            measurand = interpolation_function_time.run(dataset_l1c_temp, {
                    "input_time": acqui_irr,
                    "output_time": acqui_rad,
                    "input_sza": input_sza,
                    "output_sza": output_sza,
                })
            dataset_l1c[measurandstring].values = measurand
            dataset_l1c = dataset_l1c.drop(
                [
                    "u_rel_random_" + measurandstring,
                    "u_rel_systematic_indep_" + measurandstring,
                    "u_rel_systematic_corr_rad_irr_" + measurandstring,
                    "err_corr_systematic_indep_" + measurandstring,
                    "err_corr_systematic_corr_rad_irr_" + measurandstring,
                ]
            )

        if len(acqui_irr) == 1:
            dataset_l1c["quality_flag"] = DatasetUtil.set_flag(
                dataset_l1c["quality_flag"], "single_irradiance_used"
            )

        return dataset_l1c

    def interpolate_skyradiance(self, dataset_l1c, dataset_l1b_skyrad):
        # print(dataset_l1b_skyrad)
        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), parallel_cores=1, dtype="float32"
        )
        measurement_function_interpolate_time = self.context.get_config_value(
            "measurement_function_interpolate_time_skyradiance"
        )
        interpolation_function_time = self._measurement_function_factory(
            prop=prop,
            corr_dims="wavelength",
            yvariable="downwelling_radiance",
            use_err_corr_dict=True,
        ).get_measurement_function(measurement_function_interpolate_time)

        acqui_skyrad = dataset_l1b_skyrad["acquisition_time"].values
        acqui_rad = dataset_l1c["acquisition_time"].values
        output_sza = dataset_l1c["solar_zenith_angle"].values
        input_sza = dataset_l1b_skyrad["solar_zenith_angle"].values

        if self.context.get_config_value("mcsteps") > 0:
            dataset_l1c = interpolation_function_time.propagate_ds_specific(
                ["random", "systematic_indep", "systematic_corr_rad_irr"],
                dataset_l1b_skyrad,
                {
                    "input_time": acqui_skyrad,
                    "output_time": acqui_rad,
                    "input_sza": input_sza,
                    "output_sza": output_sza,
                },
                ds_out_pre=dataset_l1c,
                store_unc_percent=True,
            )
        else:
            measurandstring='downwelling_radiance'
            measurand = interpolation_function_time.run(dataset_l1b_skyrad, {
                    "input_time": acqui_skyrad,
                    "output_time": acqui_rad,
                    "input_sza": input_sza,
                    "output_sza": output_sza,
                })
            dataset_l1c[measurandstring].values = measurand
            dataset_l1c = dataset_l1c.drop(
                [
                    "u_rel_random_" + measurandstring,
                    "u_rel_systematic_indep_" + measurandstring,
                    "u_rel_systematic_corr_rad_irr_" + measurandstring,
                    "err_corr_systematic_indep_" + measurandstring,
                    "err_corr_systematic_corr_rad_irr_" + measurandstring,
                ]
            )


        if len(acqui_skyrad) == 1:
            dataset_l1c["quality_flag"] = DatasetUtil.set_flag(
                dataset_l1c["quality_flag"], "single_skyradiance_used"
            )

        return dataset_l1c
