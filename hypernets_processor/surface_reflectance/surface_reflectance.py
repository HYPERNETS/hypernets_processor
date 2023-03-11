"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.surface_reflectance.measurement_functions.protocol_factory import (
    ProtocolFactory,
)
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.rhymer.rhymer.processing.rhymer_processing import (
    RhymerProcessing,
)
from hypernets_processor.rhymer.rhymer.shared.rhymer_shared import RhymerShared
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_utils.average import Average
from hypernets_processor.data_utils.quality_checks import QualityChecks

import punpy
import numpy as np
import obsarray
from obsarray.templater.dataset_util import DatasetUtil

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class SurfaceReflectance:
    def __init__(self, context, parallel_cores=1):
        self._measurement_function_factory = ProtocolFactory
        self.qual = QualityChecks(context)
        self.templ = DataTemplates(context=context)
        self.writer = HypernetsWriter(context)
        self.avg = Average(context)
        self.calibrate = Calibrate(context)
        self.plot = Plotting(context)
        self.context = context
        self.rh = RhymerHypstar(context)
        self.rhp = RhymerProcessing(context)
        self.rhs = RhymerShared(context)

    def process_l1c(self, dataset):
        dataset_l1c = self.templ.l1c_from_l1b_dataset(dataset)
        dataset_l1c = self.rh.get_wind(dataset_l1c)
        dataset_l1c = self.rh.get_fresnelrefl(dataset_l1c)

        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32", parallel_cores=1
        )
        l1ctol1b_function = self._measurement_function_factory(
            prop=prop,
            yvariable=[
                "water_leaving_radiance",
                "reflectance_nosc",
                "reflectance",
                "epsilon",
            ],
            repeat_dims=["scan"],
            param_fixed=[False, False, False, False, True],
        ).get_measurement_function(
            self.context.get_config_value("measurement_function_surface_reflectance")
        )

        l1ctol1b_function.setup(self.context)

        L1c = l1ctol1b_function.propagate_ds_specific(
            ["random", "systematic_indep"],
            dataset_l1c,
            comp_list_out=["random", "systematic"],
            ds_out_pre=dataset_l1c,
            use_ds_out_pre_unmodified=True,
            store_unc_percent=True,
            simple_systematic=False,
        )

        # input_vars = l1ctol1b_function.get_argument_names()
        # input_qty = self.prop.find_input(input_vars, dataset_l1c)
        # u_random_input_qty = self.prop.find_u_random_input(input_vars, dataset_l1c)
        # u_systematic_input_qty, corr_systematic_input_qty = \
        #     self.prop.find_u_systematic_input(input_vars, dataset_l1c)
        #
        # L1c = self.prop.process_measurement_function_l2(
        #     ["water_leaving_radiance", "reflectance_nosc", "reflectance", "epsilon"],
        #     dataset_l1c, l1ctol1b_function.meas_function, input_qty,
        #     u_random_input_qty, u_systematic_input_qty, corr_systematic_input_qty,param_fixed=[False,False,False,False,True])

        failSimil = self.rh.qc_similarity(L1c)
        L1c["quality_flag"][np.where(failSimil == 1)] = DatasetUtil.set_flag(
            L1c["quality_flag"][np.where(failSimil == 1)], "simil_fail"
        )  # for i in range(len(mask))]

        if self.context.get_config_value("write_l1c"):
            self.writer.write(
                L1c,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings_L2"
                ),
            )

        for measurandstring in [
            "water_leaving_radiance",
            "reflectance_nosc",
            "reflectance",
        ]:
            try:
                if self.context.get_config_value("plot_l1c"):
                    self.plot.plot_series_in_sequence(measurandstring, L1c)

                if self.context.get_config_value("plot_uncertainty"):
                    self.plot.plot_relative_uncertainty(measurandstring, L1c, L2=True)
            except:
                print("not plotting ", measurandstring)
        return L1c

    def process_l2(self, dataset):
        dataset = self.qual.perform_quality_check_L2a(dataset)
        prop = punpy.MCPropagation(
            self.context.get_config_value("mcsteps"), dtype="float32"
        )
        l1tol2_function = self._measurement_function_factory(
            prop=prop, repeat_dims="series", yvariable="reflectance"
        ).get_measurement_function(
            self.context.get_config_value("measurement_function_surface_reflectance")
        )

        if self.context.get_config_value("network").lower() == "w":
            dataset_l2a = self.avg.average_L2(
                dataset
            )  # template and propagation is in average_L2

            # propagate flags
            for flag_i in ["single_irradiance_used"]:
                if any(dataset.flag["quality_flag"][flag_i].value.values):
                    dataset_l2a["quality_flag"].values = DatasetUtil.set_flag(
                        dataset_l2a["quality_flag"].values, flag_i
                    )

            for measurandstring in [
                "water_leaving_radiance",
                "reflectance_nosc",
                "reflectance",
            ]:
                try:
                    if self.context.get_config_value("plot_l2a"):
                        self.plot.plot_series_in_sequence(
                            measurandstring, dataset_l2a, ylim=[0, 0.05]
                        )

                    if self.context.get_config_value("plot_uncertainty"):
                        self.plot.plot_relative_uncertainty(
                            measurandstring, dataset_l2a, L2=True
                        )

                    if self.context.get_config_value("plot_correlation"):
                        self.plot.plot_correlation(
                            measurandstring, dataset_l2a, L2=True
                        )
                except:
                    print("not plotting ", measurandstring)

        elif self.context.get_config_value("network").lower() == "l":
            dataset_l2a = self.templ.l2_from_l1c_dataset(
                dataset, ["outliers", "dark_outliers"]
            )

            dataset_l2a = l1tol2_function.propagate_ds_specific(
                ["random", "systematic_indep"],
                dataset,
                comp_list_out=["random", "systematic"],
                ds_out_pre=dataset_l2a,
                store_unc_percent=True,
                simple_systematic=False,
            )
            dataset_l2a["std_reflectance"].values = (
                dataset["std_radiance"].values
                / dataset["radiance"].values
                * dataset_l2a["reflectance"].values
            )

            if self.context.get_config_value("plot_l2a"):
                self.plot.plot_series_in_sequence("reflectance", dataset_l2a)
                self.plot.plot_series_in_sequence_vaa("reflectance", dataset_l2a, 98)
                self.plot.plot_series_in_sequence_vza("reflectance", dataset_l2a, 30)
            if self.context.get_config_value("plot_uncertainty"):
                self.plot.plot_relative_uncertainty("reflectance", dataset_l2a, L2=True)

            if self.context.get_config_value("plot_correlation"):
                self.plot.plot_correlation("reflectance", dataset_l2a, L2=True)
        else:
            self.context.logger.error("network is not correctly defined")

        if self.context.get_config_value("write_l2a"):
            self.writer.write(
                dataset_l2a,
                overwrite=True,
                remove_vars_strings=self.context.get_config_value(
                    "remove_vars_strings_L2"
                ),
            )

        return dataset_l2a
