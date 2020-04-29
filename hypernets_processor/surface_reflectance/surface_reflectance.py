"""
Surface reflectance class
"""

from hypernets_processor.version import __version__

from hypernets_processor.surface_reflectance.measurement_functions.protocol_factory import ProtocolFactory
import punpy

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class SurfaceReflectance:
    def __init__(self,MCsteps=10000):
        self._measurement_function_factory = ProtocolFactory()
        self.prop = punpy.MCPropagation(MCsteps)

    def Process(self,dataset_l1,protocol_data,measurement_function):
        dataset_l1 = self.perform_checks(dataset_l1)
        l1tol2_function = self._measurement_function_factory.get_measurement_function(measurement_function)
        input_vars = l1tol2_function.get_argument_names()
        input_qty = self.find_input(input_vars,dataset_l1,protocol_data)
        u_random_input_qty = self.find_u_random_input(input_vars,dataset_l1,protocol_data)
        u_systematic_input_qty = self.find_u_systematic_input(input_vars,dataset_l1,protocol_data)
        dataset_l2 = self.l2_from_l1_dataset(dataset_l1)
        dataset_l2 = self.process_measurement_function(dataset_l2,l1tol2_function.function(),input_qty,
                                                       u_random_input_qty,u_systematic_input_qty)
        return dataset_l2

    def find_input(self,variables,dataset,ancillary_dataset):
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
        for var in range(variables):
            try:
                inputs.append(dataset[var])
            except:
                inputs.append(ancillary_dataset[var])
        return inputs

    def find_u_random_input(self,variables,dataset,ancillary_dataset):
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
        for var in range(variables):
            try:
                inputs.append(dataset["u_random_"+var])
            except:
                inputs.append(ancillary_dataset["u_random_"+var])
        return inputs

    def find_u_systematic_input(self,variables,dataset,ancillary_dataset):
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
        for var in range(variables):
            try:
                inputs.append(dataset["u_systematic_"+var])
            except:
                inputs.append(ancillary_dataset["u_systematic_"+var])

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

    def l2_from_l1_dataset(self,datasetl0):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        hw = HypernetsWriter()
        dataset = hw.create_template_dataset_l2a()

        return dataset

    def process_measurement_function(self,dataset_l2,measurement_function,input_quantities,u_random_input_quantities,
                                     u_systematic_input_quantities):
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities)
        u_systematic_measurand = self.prop.propagate_systematic(measurement_function,input_quantities,
                                                                u_systematic_input_quantities)
        u_tot_measurand,cov_measurand = self.prop.propagate_both(measurement_function,input_quantities,
                                                                 u_random_input_quantities,
                                                                 u_systematic_input_quantities)

        dataset_l2["reflectance"] = measurand
        dataset_l2["u_random_reflectance"] = u_random_measurand
        dataset_l2["u_systematic_reflectance"] = u_systematic_measurand
        dataset_l2["cov_reflectance"] = cov_measurand

        return dataset_l2












