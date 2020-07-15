"""
Calibration class
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.measurement_function_factory import MeasurementFunctionFactory
import punpy
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.dataset_util import DatasetUtil
import numpy as np

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

class Calibrate:
    def __init__(self,MCsteps=1000):
        self._measurement_function_factory = MeasurementFunctionFactory()
        self.prop= punpy.MCPropagation(MCsteps,parallel_cores=3)

    def calibrate(self,dataset_l0,calibration_data,measurement_function='StandardMeasurementFunction'):
        dataset_l0 = self.preprocess_l0(dataset_l0)
        calibrate_function = self._measurement_function_factory.get_measurement_function(measurement_function)
        input_vars=calibrate_function.get_argument_names()
        print(input_vars)
        input_qty=self.find_input(input_vars,dataset_l0,calibration_data)
        u_random_input_qty=self.find_u_random_input(input_vars,dataset_l0,calibration_data)
        u_systematic_input_qty=self.find_u_systematic_input(input_vars,dataset_l0,calibration_data)
        dataset_l1 = self.l1_from_l0_dataset(dataset_l0)
        dataset_l1 = self.process_measurement_function(dataset_l1,calibrate_function.function,input_qty,u_random_input_qty,u_systematic_input_qty)
        return dataset_l1

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
        for var in variables:
            try:
                inputs.append(dataset[var].values)
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
        for var in variables:
            try:
                inputs.append(dataset["u_random_"+var].values)
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
        for var in variables:
            try:
                inputs.append(dataset["u_systematic_"+var].values)
            except:
                inputs.append(ancillary_dataset["u_systematic_"+var])

        return inputs


    def preprocess_l0(self,datasetl0):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """
        dim_sizes_dict = {"wavelength": len(datasetl0["wavelength"]), "scan": len(datasetl0["scan"])}
        du = DatasetUtil()

        DN_rand = du.create_variable([len(datasetl0["wavelength"]),len(datasetl0["scan"])],dim_names=["wavelength","scan"],dtype=np.uint32)
        DN_syst = du.create_variable([len(datasetl0["wavelength"]),len(datasetl0["scan"])],dim_names=["wavelength","scan"],dtype=np.uint32)
        datasetl0["u_random_digital_number"]=DN_rand
        datasetl0["u_systematic_digital_number"]=DN_syst
        return datasetl0

    def l1_from_l0_dataset(self,datasetl0):
        """
        Makes a L1 template of the data, and propagates the appropriate keywords from L0.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        dim_sizes_dict = {"wavelength": len(datasetl0["wavelength"]), "scan": len(datasetl0["scan"])}
        ds = HypernetsDSBuilder.create_ds_template(dim_sizes_dict, "L_L1A_RAD")
        ds["wavelength"] = datasetl0["wavelength"]
        # ds["bandwidth"]=wvl
        #ds["scan"] = len(datasetl0["scan"])

        return ds

    def process_measurement_function(self,dataset_l1,measurement_function,input_quantities,u_random_input_quantities,u_systematic_input_quantities):
        print("here:",input_quantities)
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities)
        u_systematic_measurand = self.prop.propagate_systematic(measurement_function,input_quantities,u_systematic_input_quantities)
        #        u_systematic_measurand,corr_systematic_radiance = self.prop.propagate_systematic(measurement_function,input_quantities,u_systematic_input_quantities,return_corr=True)
        #u_tot_measurand, cov_measurand = self.prop.propagate_both(measurement_function,input_quantities,u_random_input_quantities,u_systematic_input_quantities)
        #print(corr_systematic_radiance.shape,len(u_random_measurand))
        dataset_l1["radiance"].values=measurand
        dataset_l1["u_random_radiance"].values=u_random_measurand
        dataset_l1["u_systematic_radiance"].values=u_systematic_measurand
        dataset_l1["corr_random_radiance"].values=np.eye(len(u_random_measurand))
        #dataset_l1["corr_systematic_radiance"].values=corr_systematic_radiance

        return dataset_l1












