"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_utils.average import Average
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.combine_SWIR.measurement_functions.combine_factory import CombineFactory
import punpy
import numpy as np

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
        self.context = context

    def combine(self,measurandstring,dataset_l1a,dataset_l1a_swir):
        dataset_l1a = self.perform_checks(dataset_l1a)
        combine_function = self._measurement_function_factory.get_measurement_function(self.context.get_config_value("measurement_function_combine"))
        input_vars = combine_function.get_argument_names()
        # input_qty = self.find_input(input_vars,dataset_l1a)
        # u_random_input_qty = self.find_u_random_input(input_vars,dataset_l1a)
        # u_systematic_input_qty = self.find_u_systematic_input(input_vars,dataset_l1a)
        dataset_l1b = self.avg.average_l1b(measurandstring,dataset_l1a)
        dataset_l1b_swir = self.avg.average_l1b(measurandstring,dataset_l1a_swir)

        dataset_l1b_comb = self.templ.l1b_template_from_combine(measurandstring,dataset_l1b,dataset_l1b_swir)
        dataset_l1b_comb[measurandstring].values = measurand
        dataset_l1b_comb["u_random_"+measurandstring].values = u_random_measurand
        dataset_l1b_comb["u_systematic_"+measurandstring].values = u_systematic_measurand
        dataset_l1b_comb["corr_random_"+measurandstring].values = np.eye(len(u_random_measurand))
        dataset_l1b_comb["corr_systematic_"+measurandstring].values = corr_systematic_measurand

        self.process_measurement_function(["radiance"],dataset_l1b,
                                          combine_function.function,input_qty,
                                          u_random_input_qty,u_systematic_input_qty)


        if self.context.get_config_value("write_l1b"):
            self.writer.write(dataset_l1b, overwrite=True)

        if self.context.get_config_value("plot_l1b"):
            self.plot.plot_series_in_sequence(measurandstring,dataset_l1b)

        # if self.context.get_config_value("plot_diff"):
        #     self.plot.plot_diff_scans(measurandstring,dataset_l1a,dataset_l1b)

        return dataset_l1b

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

    def process_measurement_function(self,measurandstrings,dataset,measurement_function,input_quantities,u_random_input_quantities,
                                     u_systematic_input_quantities):
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities,repeat_dims=1,output_vars=len(measurandstrings))

        u_systematic_measurand,corr_systematic_measurand = self.prop.propagate_systematic(
            measurement_function,input_quantities,u_systematic_input_quantities,
            return_corr=True,corr_axis=0,output_vars=len(measurandstrings))
        measurandstring=measurandstrings[0]
        dataset[measurandstring].values = measurand
        dataset["u_random_"+measurandstring].values = u_random_measurand
        dataset["u_systematic_"+measurandstring].values = u_systematic_measurand
        dataset["corr_random_"+measurandstring].values = np.eye(len(u_random_measurand))
        dataset["corr_systematic_"+measurandstring].values = corr_systematic_measurand


        return dataset







