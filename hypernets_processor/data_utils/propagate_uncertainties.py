"""
Averaging class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil
from hypernets_processor.data_io.data_templates import DataTemplates
import punpy
import numpy as np
import warnings

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

class PropagateUnc:
    def __init__(self,context,MCsteps,parallel_cores):
        self.prop = punpy.MCPropagation(MCsteps, parallel_cores=parallel_cores)
        self.context=context

    def find_input_l1a(self, variables, dataset, ancillary_dataset):
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
            try:
                inputs.append(dataset[var].values)
            except:
                inputs.append(ancillary_dataset[var])
        return inputs

    def find_u_random_input_l1a(self, variables, dataset, ancillary_dataset):
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
                inputs.append(dataset["u_random_" + var].values)
            except:
                try:
                    inputs.append(ancillary_dataset["u_random_" + var])
                except:
                    inputs.append(None)
        return inputs

    def find_u_systematic_input_l1a(self, variables, dataset, ancillary_dataset):
        """
        returns a list of the systematic uncertainties on the data for a given list of input variables

        :param variables:
        :type variables:
        :param dataset:
        :type dataset:
        :return:
        :rtype:
        """
        inputs_indep = []
        corr_indep = []
        inputs_corr = []
        corr_corr = []
        for var in variables:
            try:
                inputs_indep.append(dataset["u_systematic_" + var].values)
                corr_indep.append(dataset["corr_systematic_" + var].values)
            except:
                try:
                    inputs_indep.append(ancillary_dataset["u_systematic_indep_"+var])
                    corr_indep.append(punpy.convert_cov_to_corr(
                        ancillary_dataset["cov_systematic_indep_"+var],
                        ancillary_dataset["u_systematic_indep_"+var]))
                except:
                    inputs_indep.append(None)
                    corr_indep.append(None)
                try:
                    inputs_corr.append(ancillary_dataset["u_systematic_corr_rad_irr_"+var])
                    corr_corr.append(punpy.convert_cov_to_corr(
                        ancillary_dataset["cov_systematic_corr_rad_irr_"+var],
                        ancillary_dataset["u_systematic_corr_rad_irr_"+var]))
                except:
                    inputs_corr.append(None)
                    corr_corr.append(None)

        return inputs_indep,inputs_corr,corr_indep,corr_corr


    def find_input(self, variables, dataset):
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

    def find_u_random_input(self, variables, dataset):
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
                inputs.append(dataset["u_random_" + var].values)
            except:
                inputs.append(None)
        return inputs

    def find_u_systematic_input(self, variables, dataset):
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
        corr_indep = []
        for var in variables:
            try:
                corr_indep.append(dataset["corr_systematic_indep_" + var].values)
                inputs.append(dataset["u_systematic_indep_" + var].values)
            except:
                inputs.append(None)
                corr_indep.append(None)
        return inputs, corr_indep

    def process_measurement_function_l1a(self, measurandstring, dataset,
                                     measurement_function, input_quantities,
                                     u_random_input_quantities,
                                     u_systematic_input_quantities_indep,
                                     u_systematic_input_quantities_corr,
                                     corr_systematic_input_quantities_indep,
                                     corr_systematic_input_quantities_corr):

        datashape = input_quantities[0].shape
        for i in range(len(input_quantities)):
            if len(input_quantities[i].shape) < len(datashape):
                if input_quantities[i].shape[0]==datashape[1]:
                    input_quantities[i] = np.tile(input_quantities[i],(datashape[0],1))
                else:
                    input_quantities[i] = np.tile(input_quantities[i],(datashape[1],1)).T

            if u_random_input_quantities[i] is not None:
                if len(u_random_input_quantities[i].shape) < len(datashape):
                    u_random_input_quantities[i] = np.tile(u_random_input_quantities[i], (datashape[1], 1)).T
            if u_systematic_input_quantities_indep[i] is not None:
                if len(u_systematic_input_quantities_indep[i].shape) < len(datashape):
                    u_systematic_input_quantities_indep[i] = np.tile(u_systematic_input_quantities_indep[i], (datashape[1], 1)).T
            if u_systematic_input_quantities_corr[i] is not None:
                if len(u_systematic_input_quantities_corr[i].shape) < len(datashape):
                    u_systematic_input_quantities_corr[i] = np.tile(u_systematic_input_quantities_corr[i], (datashape[1], 1)).T

        measurand = measurement_function(*input_quantities)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u_random_measurand = self.prop.propagate_random(measurement_function, input_quantities,
                                                            u_random_input_quantities,repeat_dims=1)
            u_syst_measurand_indep,corr_syst_measurand_indep = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_indep,
                corr_x=corr_systematic_input_quantities_indep,return_corr=True,
                repeat_dims=1,corr_axis=0,fixed_corr_var=True)
            u_syst_measurand_corr,corr_syst_measurand_corr = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_corr,
                corr_x=corr_systematic_input_quantities_corr,return_corr=True,
                repeat_dims=1,corr_axis=0,fixed_corr_var=True)

        dataset[measurandstring].values = measurand
        dataset["u_random_" + measurandstring].values = u_random_measurand
        dataset["u_systematic_indep_" + measurandstring].values = u_syst_measurand_indep
        dataset["u_systematic_corr_rad_irr_" + measurandstring].values = u_syst_measurand_corr
        dataset["corr_random_" + measurandstring].values = np.eye(len(u_random_measurand))
        dataset["corr_systematic_indep_" + measurandstring].values = corr_syst_measurand_indep
        dataset["corr_systematic_corr_rad_irr_" + measurandstring].values = corr_syst_measurand_corr

        return dataset

    def process_measurement_function_l1(self,measurandstring,dataset,measurement_function,
                                     input_quantities,u_random_input_quantities,
                                     u_systematic_input_quantities_indep,
                                     u_systematic_input_quantities_corr,
                                     corr_systematic_input_quantities_indep,
                                     corr_systematic_input_quantities_corr,
                                     param_fixed=None):

        measurand = measurement_function(*input_quantities)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u_random_measurand = self.prop.propagate_random(measurement_function,
                                                            input_quantities,
                                                            u_random_input_quantities,
                                                        param_fixed=param_fixed,
                                                        repeat_dims=1)
            u_syst_measurand_indep,corr_syst_measurand_indep = self.prop.propagate_systematic(
                measurement_function,input_quantities,
                u_systematic_input_quantities_indep,
                corr_x=corr_systematic_input_quantities_indep,return_corr=True,
                corr_axis=0,param_fixed=param_fixed,repeat_dims=1)
            u_syst_measurand_corr,corr_syst_measurand_corr = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_corr,
                corr_x=corr_systematic_input_quantities_corr,return_corr=True,
                corr_axis=0,param_fixed=param_fixed,repeat_dims=1)
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

    def process_measurement_function_l2(self, measurandstrings,
                                        dataset,
                                        measurement_function,
                                        input_quantities,
                                        u_random_input_quantities,
                                        u_systematic_input_quantities,
                                        corr_systematic_input_quantities):
        measurand = measurement_function(*input_quantities)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u_random_measurand = self.prop.propagate_random(measurement_function, input_quantities,
                                                            u_random_input_quantities, repeat_dims=1,
                                                            output_vars=len(measurandstrings))

            if len(measurandstrings) > 1:
                u_systematic_measurand, corr_systematic_measurand, corr_between = \
                    self.prop.propagate_systematic(measurement_function,
                                                   input_quantities,
                                                   u_systematic_input_quantities,
                                                   corr_x=corr_systematic_input_quantities,
                                                   return_corr=True,
                                                   repeat_dims=1,
                                                   corr_axis=0,
                                                   output_vars=len(measurandstrings))
                for im, measurandstring in enumerate(measurandstrings):
                    dataset[measurandstring].values = measurand[im]
                    dataset["u_random_" + measurandstring].values = u_random_measurand[im]
                    dataset["u_systematic_" + measurandstring].values = u_systematic_measurand[im]
                    dataset["corr_random_" + measurandstring].values = np.eye(len(u_random_measurand[im]))
                    dataset["corr_systematic_" + measurandstring].values = corr_systematic_measurand[im]

            else:
                u_systematic_measurand,corr_systematic_measurand=\
                    self.prop.propagate_systematic(measurement_function,
                                                   input_quantities,
                                                   u_systematic_input_quantities,
                                                   corr_x=corr_systematic_input_quantities,
                                                   return_corr=True,
                                                   repeat_dims=1,
                                                   corr_axis=0,
                                                   output_vars=len(measurandstrings))
                measurandstring = measurandstrings[0]
                dataset[measurandstring].values = measurand
                dataset["u_random_" + measurandstring].values = u_random_measurand
                dataset["u_systematic_" + measurandstring].values = u_systematic_measurand
                dataset["corr_random_" + measurandstring].values = np.eye(len(u_random_measurand))
                dataset["corr_systematic_" + measurandstring].values = corr_systematic_measurand

        return dataset
