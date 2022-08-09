"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_utils.average import Average
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.combine_SWIR.measurement_functions.combine_factory import CombineFactory
from hypernets_processor.data_utils.propagate_uncertainties import PropagateUnc
from hypernets_processor.data_utils.quality_checks import QualityChecks

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class CombineSWIR:
    def __init__(self,context,parallel_cores=1):
        self._measurement_function_factory = CombineFactory()
        self.prop = PropagateUnc(context, parallel_cores=parallel_cores)
        self.qual = QualityChecks(context)
        self.avg = Average(context=context)
        self.templ = DataTemplates(context)
        self.writer=HypernetsWriter(context)
        self.plot=Plotting(context)
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
        dataset_l1b = self.avg.average_l1b(
            measurandstring, dataset_l0masked, dataset_bla, calibration_data
        )
        dataset_l1b_swir = self.avg.average_l1b(
            measurandstring,
            dataset_l0masked_swir,
            dataset_bla_swir,
            calibration_data_swir,
        )
        dataset_l1b, dataset_l1b_swir = self.qual.perform_quality_check_comb(
            dataset_l1b, dataset_l1b_swir
        )
        combine_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_combine")
        )
        input_vars = combine_function.get_argument_names()
        input_qty = [
            dataset_l1b["wavelength"].values,
            dataset_l1b[measurandstring].values,
            dataset_l1b_swir["wavelength"].values,
            dataset_l1b_swir[measurandstring].values,
            self.context.get_config_value("combine_lim_wav"),
        ]
        u_random_input_qty = [
            None,
            dataset_l1b["u_rel_random_" + measurandstring].values
            * dataset_l1b[measurandstring].values,
            None,
            dataset_l1b_swir["u_rel_random_" + measurandstring].values
            * dataset_l1b_swir[measurandstring].values,
            None,
            ]
        u_systematic_input_qty_indep = [
            None,
            dataset_l1b["u_rel_systematic_indep_" + measurandstring].values
            * dataset_l1b[measurandstring].values,
            None,
            dataset_l1b_swir["u_rel_systematic_indep_" + measurandstring].values
            * dataset_l1b_swir[measurandstring].values,
            None,
            ]
        u_systematic_input_qty_corr = [
            None,
            dataset_l1b["u_rel_systematic_corr_rad_irr_" + measurandstring].values
            * dataset_l1b[measurandstring].values,
            None,
            dataset_l1b_swir["u_rel_systematic_corr_rad_irr_" + measurandstring].values
            * dataset_l1b_swir[measurandstring].values,
            None,
            ]
        corr_systematic_input_qty_indep = [
            None,
            dataset_l1b["corr_systematic_indep_" + measurandstring].values,
            None,
            dataset_l1b_swir["corr_systematic_indep_" + measurandstring].values,
            None,
        ]
        corr_systematic_input_qty_corr = [
            None,
            dataset_l1b["corr_systematic_corr_rad_irr_" + measurandstring].values,
            None,
            dataset_l1b_swir["corr_systematic_corr_rad_irr_" + measurandstring].values,
            None,
        ]
        # todo do this more consistently with other modules, and do a direct copy for ranges that don't overlap
        dataset_l1b_comb = self.templ.l1b_template_from_combine(
            measurandstring, dataset_l1b, dataset_l1b_swir
        )

        self.prop.process_measurement_function_l1(
            measurandstring,
            dataset_l1b_comb,
            combine_function.function,
            input_qty,
            u_random_input_qty,
            u_systematic_input_qty_indep,
            u_systematic_input_qty_corr,
            corr_systematic_input_qty_indep,
            corr_systematic_input_qty_corr,
            param_fixed=[True, False, True, False, True],
        )

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
            if measurandstring=="radiance":
                self.plot.plot_series_in_sequence_vaa(measurandstring, dataset_l1b_comb, 98)
                self.plot.plot_series_in_sequence_vza(measurandstring, dataset_l1b_comb, 30)

        if self.context.get_config_value("plot_uncertainty"):
            self.plot.plot_relative_uncertainty(measurandstring, dataset_l1b_comb)

        if self.context.get_config_value("plot_correlation"):
            self.plot.plot_correlation(measurandstring, dataset_l1b_comb)

        # if self.context.get_config_value("plot_diff"):
        #     self.plot.plot_diff_scans(measurandstring,dataset_l1a,dataset_l1b)

        return dataset_l1b_comb