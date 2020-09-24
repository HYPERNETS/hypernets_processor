"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.surface_reflectance.measurement_functions.protocol_factory import ProtocolFactory
import punpy
import numpy as np

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class SurfaceReflectance:
    def __init__(self,context,MCsteps=1000,parallel_cores=1):
        self._measurement_function_factory = ProtocolFactory()
        self.prop= punpy.MCPropagation(MCsteps,parallel_cores=parallel_cores)
        self.hdsb = HypernetsDSBuilder(context=context)
        self.writer=HypernetsWriter(context)
        self.context = context

    def process(self,dataset_l1c):
        dataset_l1c = self.perform_checks(dataset_l1c)
        l1tol2_function = self._measurement_function_factory.get_measurement_function(self.context.get_config_value("measurement_function_surface_reflectance"))
        input_vars = l1tol2_function.get_argument_names()
        input_qty = self.find_input(input_vars,dataset_l1c)
        u_random_input_qty = self.find_u_random_input(input_vars,dataset_l1c)
        u_systematic_input_qty = self.find_u_systematic_input(input_vars,dataset_l1c)
        dataset_l2 = self.l2_from_l1c_dataset(dataset_l1c)

        if self.context.get_config_value("network")=="W":
            dataset_l2 = self.process_measurement_function(["nlw","rhow_nosc","rhow"],
                dataset_l2,l1tol2_function.function,input_qty,u_random_input_qty,
                u_systematic_input_qty)

        elif self.context.get_config_value("network")=="L":
            dataset_l2 = self.process_measurement_function("reflectance",dataset_l2,
                                                           l1tol2_function.function,
                                                           input_qty,u_random_input_qty,
                                                           u_systematic_input_qty)

        self.writer.write(dataset_l2,overwrite=True)
        return dataset_l2

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
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities,output_vars=len(measurandstrings))
        u_systematic_measurand,corr_systematic_measurand,corr_between = self.prop.propagate_systematic(measurement_function,
                                                                                          input_quantities,
                                                                                          u_systematic_input_quantities,
                                                                                          return_corr=True,corr_axis=0,output_vars=len(measurandstrings))
        for im, measurandstring in enumerate(measurandstrings):
            dataset[measurandstring].values = measurand[im]
            dataset["u_random_"+measurandstring].values = u_random_measurand[im]
            dataset["u_systematic_"+measurandstring].values = u_systematic_measurand[im]
            dataset["corr_random_"+measurandstring].values = np.eye(len(u_random_measurand[im]))
            dataset["corr_systematic_"+measurandstring].values = corr_systematic_measurand[im]

        return dataset







