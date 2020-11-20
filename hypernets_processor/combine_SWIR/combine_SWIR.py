"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_utils.average import Average
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.combine_SWIR.measurement_functions.combine_factory import CombineFactory

import punpy
import numpy as np
import warnings

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class CombineSWIR:
    def __init__(self,context,MCsteps=1000,parallel_cores=1):
        self._measurement_function_factory = CombineFactory()
        self.prop= punpy.MCPropagation(MCsteps,parallel_cores=parallel_cores)
        self.avg = Average(context=context)
        self.templ = DataTemplates(context)
        self.writer=HypernetsWriter(context)
        self.plot=Plotting(context)
        self.context = context

    def combine(self,measurandstring,dataset_l1a,dataset_l1a_swir):
        dataset_l1a = self.perform_checks(dataset_l1a)
        dataset_l1b = self.avg.average_l1b(measurandstring,dataset_l1a)
        dataset_l1b_swir = self.avg.average_l1b(measurandstring,dataset_l1a_swir)

        combine_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_combine"))
        input_vars = combine_function.get_argument_names()
        input_qty = [dataset_l1b["wavelength"].values,
                     dataset_l1b[measurandstring].values,
                     dataset_l1b_swir["wavelength"].values,
                     dataset_l1b_swir[measurandstring].values,
                     self.context.get_config_value("combine_lim_wav")]
        u_random_input_qty = [None,
                     dataset_l1b["u_random_"+measurandstring].values,
                     None,
                     dataset_l1b_swir["u_random_"+measurandstring].values,
                     None]
        u_systematic_input_qty_indep =  [None,
                     dataset_l1b["u_systematic_indep_"+measurandstring].values,
                     None,
                     dataset_l1b_swir["u_systematic_indep_"+measurandstring].values,
                     None]
        u_systematic_input_qty_corr =  [None,
                     dataset_l1b["u_systematic_corr_rad_irr_"+measurandstring].values,
                     None,
                     dataset_l1b_swir["u_systematic_corr_rad_irr_"+measurandstring].values,
                     None]
        cov_systematic_input_qty_indep =  [None,
                     punpy.convert_corr_to_cov(dataset_l1b["corr_systematic_indep_" + measurandstring].values,
                            np.mean(dataset_l1b["u_systematic_indep_"+measurandstring].values,axis=1)),
                     None,
                     punpy.convert_corr_to_cov(dataset_l1b_swir["corr_systematic_indep_"+measurandstring].values,
                            np.mean(dataset_l1b_swir["u_systematic_indep_"+measurandstring].values,axis=1)),
                     None]
        cov_systematic_input_qty_corr = [None,
                     punpy.convert_corr_to_cov(dataset_l1b["corr_systematic_corr_rad_irr_" + measurandstring].values,
                            np.mean(dataset_l1b["u_systematic_corr_rad_irr_"+measurandstring].values,axis=1)),
                     None,
                     punpy.convert_corr_to_cov(dataset_l1b_swir["corr_systematic_corr_rad_irr_"+measurandstring].values,
                            np.mean(dataset_l1b_swir["u_systematic_corr_rad_irr_"+measurandstring].values,axis=1)),
                     None]
        #todo do this more consistently with other modules, and do a direct copy for ranges that don't overlap
        dataset_l1b_comb = self.templ.l1b_template_from_combine(measurandstring,dataset_l1b,dataset_l1b_swir)

        self.process_measurement_function(measurandstring,dataset_l1b_comb,
                                          combine_function.function,input_qty,
                                          u_random_input_qty,
                                          u_systematic_input_qty_indep,
                                          u_systematic_input_qty_corr,
                                          cov_systematic_input_qty_indep,
                                          cov_systematic_input_qty_corr)

        if self.context.get_config_value("write_l1b"):
            self.writer.write(dataset_l1b_comb, overwrite=True)

        if self.context.get_config_value("plot_l1b"):
            self.plot.plot_series_in_sequence(measurandstring,dataset_l1b_comb)

        if self.context.get_config_value("plot_uncertainty"):
            self.plot.plot_relative_uncertainty(measurandstring,dataset_l1b_comb)

        if self.context.get_config_value("plot_correlation"):
            self.plot.plot_correlation(measurandstring,dataset_l1b_comb)

        # if self.context.get_config_value("plot_diff"):
        #     self.plot.plot_diff_scans(measurandstring,dataset_l1a,dataset_l1b)

        return dataset_l1b_comb

    def find_input(self,variables,dataset):
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
            inputs.append(dataset[var].values)
        return inputs

    def find_u_random_input(self,variables,dataset):
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
                inputs.append(dataset["u_random_"+var].values)
            except:
                inputs.append(None)
        return inputs

    def find_u_systematic_input(self,variables,dataset):
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
                inputs.append(dataset["u_systematic_"+var].values)
            except:
                inputs.append(None)
        return inputs

    def perform_checks(self,dataset_l1):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """

        return dataset_l1

    def l2_from_l1c_dataset(self,datasetl1c):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        if self.context.get_config_value("network") == "L":
            l2a_dim_sizes_dict = {"wavelength":len(datasetl1c["wavelength"]),
                                  "series":len(datasetl1c['series'])}
            l2a = self.hdsb.create_ds_template(l2a_dim_sizes_dict, "L_L2A")

        elif self.context.get_config_value("network") == "W":
            l2a_dim_sizes_dict = {"wavelength": len(datasetl1c["wavelength"]),
                                  "scan": len(datasetl1c['scan'])}
            l2a = self.hdsb.create_ds_template(l2a_dim_sizes_dict, "W_L2A")

        return l2a

    def process_measurement_function(self,measurandstring,dataset,measurement_function,input_quantities,
                                     u_random_input_quantities,
                                     u_systematic_input_quantities_indep,
                                     u_systematic_input_quantities_corr,
                                     cov_systematic_input_quantities_indep,
                                     cov_systematic_input_quantities_corr):
        measurand = measurement_function(*input_quantities)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u_random_measurand = self.prop.propagate_random(measurement_function,
                                                            input_quantities,
                                                            u_random_input_quantities,param_fixed=[False,False,False,False,True],
                                                            repeat_dims=1)
            u_syst_measurand_indep,corr_syst_measurand_indep = self.prop.propagate_systematic(
                measurement_function,input_quantities,
                u_systematic_input_quantities_indep,
                cov_x=cov_systematic_input_quantities_indep,return_corr=True,param_fixed=[False,False,False,False,True],
                repeat_dims=1,corr_axis=0)
            u_syst_measurand_corr,corr_syst_measurand_corr = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_corr,
                cov_x=cov_systematic_input_quantities_corr,return_corr=True,param_fixed=[False,False,False,False,True],
                repeat_dims=1,corr_axis=0)
        dataset[measurandstring].values = measurand
        dataset["u_random_"+measurandstring].values = u_random_measurand
        dataset["u_systematic_indep_"+measurandstring].values = u_syst_measurand_indep
        dataset[
            "u_systematic_corr_rad_irr_"+measurandstring].values = u_syst_measurand_corr
        dataset["corr_random_"+measurandstring].values = np.eye(len(u_random_measurand))
        dataset[
            "corr_systematic_indep_"+measurandstring].values = corr_syst_measurand_indep
        dataset[
            "corr_systematic_corr_rad_irr_"+measurandstring].values = corr_syst_measurand_corr

        return dataset







