"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.combine_SWIR.measurement_functions.combine_factory import (
    CombineFactory,
)
from hypernets_processor.data_utils.quality_checks import QualityChecks
import punpy

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class CombineSWIR:
    def __init__(self, context, parallel_cores=1):
        self._measurement_function_factory = CombineFactory
        self.qual = QualityChecks(context)
        self.cal = Calibrate(context=context)
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context)
        self.plot = Plotting(context)
        self.context = context

    def combine(
        self,
        measurandstring,
        dataset_l0masked,
        dataset_bla,
        dataset_l0masked_swir,
        dataset_bla_swir,
        calibration_data,
        calibration_data_swir,
    ):
        dataset_l1b = self.cal.calibrate_l1b(
            measurandstring, dataset_l0masked, dataset_bla, calibration_data
        )

        dataset_l1b_swir = self.cal.calibrate_l1b(
            measurandstring,
            dataset_l0masked_swir,
            dataset_bla_swir,
            calibration_data_swir,
        )

        dataset_l1b, dataset_l1b_swir = self.qual.perform_quality_check_comb(
            dataset_l1b, dataset_l1b_swir
        )
        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32", MCdimlast=True
        )
        combine_function = self._measurement_function_factory(
            prop=prop, repeat_dims="series", yvariable=measurandstring
        ).get_measurement_function(
            self.context.get_config_value("measurement_function_combine")
        )

        dataset_l1b_comb = self.templ.l1b_template_from_combine(
            measurandstring, dataset_l1b, dataset_l1b_swir
        )

        dataset_l1b_temp = self.templ.rename_var(
            dataset_l1b,
            measurandstring,
            "measurand_VIS",
            "wavelength",
            "wavelength_VIS",
        )
        dataset_l1b_swir_temp = self.templ.rename_var(
            dataset_l1b_swir,
            measurandstring,
            "measurand_SWIR",
            "wavelength",
            "wavelength_SWIR",
        )

        dataset_l1b_comb = combine_function.propagate_ds_specific(
            ["random", "systematic_indep", "systematic_corr_rad_irr"],
            dataset_l1b_temp,
            dataset_l1b_swir_temp,
            {"wavelength_step": self.context.get_config_value("combine_lim_wav")},
            ds_out_pre=dataset_l1b_comb,
            store_unc_percent=True,
        )

        dataset_l1b_comb[
            "std_" + measurandstring
        ].values = combine_function.meas_function(
            dataset_l1b["wavelength"].values,
            dataset_l1b["std_" + measurandstring].values,
            dataset_l1b_swir["wavelength"].values,
            dataset_l1b_swir["std_" + measurandstring].values,
            1000,
        )
        dataset_l1b_comb["n_valid_scans"].values = dataset_l1b["n_valid_scans"].values
        dataset_l1b_comb["n_valid_scans_SWIR"].values = dataset_l1b_swir[
            "n_valid_scans"
        ].values

        if measurandstring == "irradiance":
            dataset_l1b_comb = self.qual.perform_quality_irradiance(dataset_l1b_comb)

        if self.context.get_config_value("write_l1b"):
            self.writer.write(
                dataset_l1b_comb,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings"
                ),
            )

        if self.context.get_config_value("plot_l1b"):
            self.plot.plot_series_in_sequence(measurandstring, dataset_l1b_comb)
            if measurandstring == "radiance":
                self.plot.plot_series_in_sequence_vaa(
                    measurandstring, dataset_l1b_comb, 98
                )
                self.plot.plot_series_in_sequence_vza(
                    measurandstring, dataset_l1b_comb, 30
                )

        if self.context.get_config_value("plot_uncertainty"):
            self.plot.plot_relative_uncertainty(measurandstring, dataset_l1b_comb)

        if self.context.get_config_value("plot_correlation"):
            self.plot.plot_correlation(measurandstring, dataset_l1b_comb)

        # if self.context.get_config_value("plot_diff"):
        #     self.plot.plot_diff_scans(measurandstring,dataset_l1a,dataset_l1b)

        return dataset_l1b_comb
