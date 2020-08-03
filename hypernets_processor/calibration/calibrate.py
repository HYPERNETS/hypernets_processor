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

    def calibrate(self,measurandstring,dataset_l0,calibration_data,measurement_function='StandardMeasurementFunction'):

        if measurandstring!="radiance" and measurandstring!="irradiance":
            print("the measurandstring needs to be either 'radiance' or 'irradiance")
            exit()

        calibrate_function = self._measurement_function_factory.get_measurement_function(measurement_function)
        input_vars=calibrate_function.get_argument_names()
        print(input_vars)

        dataset_l1a,dataset_l1b = self.l1_templates_from_l0_dataset(measurandstring,dataset_l0)
        dataset_l0=self.preprocess_l0(dataset_l0)

        input_qty_l1a = self.find_input(input_vars,dataset_l0,calibration_data)
        u_random_input_qty_l1a = self.find_u_random_input(input_vars,dataset_l0,calibration_data)
        u_systematic_input_qty_l1a = self.find_u_systematic_input(input_vars,dataset_l0,calibration_data)

        dataset_l1a = self.process_measurement_function(measurandstring,dataset_l1a,calibrate_function.function,input_qty_l1a,
                                                            u_random_input_qty_l1a,u_systematic_input_qty_l1a)

        input_qty_l1b = self.find_input(input_vars,dataset_l0,calibration_data,masked_avg=True)
        u_random_input_qty_l1b = self.find_u_random_input(input_vars,dataset_l0,calibration_data,masked_avg=True)
        u_systematic_input_qty_l1b = self.find_u_systematic_input(input_vars,dataset_l0,calibration_data,masked_avg=True)

        dataset_l1b = self.process_measurement_function(measurandstring,dataset_l1b,calibrate_function.function,input_qty_l1b,
                                                            u_random_input_qty_l1b,u_systematic_input_qty_l1b)

        return dataset_l1a,dataset_l1b

    def find_input(self,variables,dataset,ancillary_dataset,masked_avg=False):
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
                if masked_avg:
                    inputs.append(np.mean(dataset[var].values,axis=1))
                else:
                    inputs.append(dataset[var].values)
            except:
                inputs.append(ancillary_dataset[var])
        return inputs

    def find_u_random_input(self,variables,dataset,ancillary_dataset,masked_avg=False):
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
                if masked_avg:
                    inputs.append(np.mean(dataset["u_random_"+var].values,axis=1))
                else:
                    inputs.append(dataset["u_random_"+var].values)
            except:
                inputs.append(ancillary_dataset["u_random_"+var])
        return inputs

    def find_u_systematic_input(self,variables,dataset,ancillary_dataset,masked_avg=False):
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
                if masked_avg:
                    #print(dataset["u_systematic_"+var]["mask" == 0].values.shape)
                    inputs.append(np.mean(dataset["u_systematic_"+var].values,axis=1))
                else:
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

        scan_mask = du.create_variable([len(datasetl0["scan"])],dim_names=["scan"],dtype=np.uint8,fill_value=0)
        datasetl0["mask"] = scan_mask
        datasetl0["mask"].values = self.clip_and_mask(datasetl0)

        DN_rand = du.create_variable([len(datasetl0["wavelength"]),len(datasetl0["scan"])],dim_names=["wavelength","scan"],dtype=np.uint32,fill_value=0)
        DN_syst = du.create_variable([len(datasetl0["wavelength"]),len(datasetl0["scan"])],dim_names=["wavelength","scan"],dtype=np.uint32,fill_value=0)

        datasetl0["u_random_digital_number"]=DN_rand

        std=datasetl0['digital_number'].where(datasetl0.mask==0).std(dim="scan")
        rand=np.zeros_like(DN_rand.values)
        for i in range(len(datasetl0["scan"])):
            rand[:,i]=std

        datasetl0["u_random_digital_number"].values=rand
        datasetl0["u_systematic_digital_number"]=DN_syst



        return datasetl0

    def clip_and_mask(self,dataset,k_unc=3):
        mask = np.zeros(len(dataset["scan"]))

        #check if zeros, max, fillvalue:

        #check if integrated signal is outlier
        intsig=np.sum(dataset["digital_number"],axis=0)
        noiseavg,noisestd,values = self.sigma_clip(intsig)
        mask[np.where(np.abs(intsig-noiseavg)>=k_unc*noisestd)]=1
        mask[0]=1

        #check if 10% of pixels are outiers

        # mask_wvl = np.zeros((len(datasetl0["wavelength"]),len(datasetl0["scan"])))
        # for i in range(len(dataset["wavelength"])):


        return mask

    def sigma_clip(self,values,tolerance=0.001,median=True,sigma_thresh=3.0):
        # Remove NaNs from input values
        values = np.array(values)
        values = values[np.where(np.isnan(values) == False)]
        values_original = np.copy(values)

        # Continue loop until result converges
        diff = 10E10
        while diff > tolerance:
            # Assess current input iteration
            if median == False:
                average = np.mean(values)
            elif median == True:
                average = np.median(values)
            sigma_old = np.std(values)

            # Mask those pixels that lie more than 3 stdev away from mean
            check = np.zeros([len(values)])
            check[np.where(values > (average+(sigma_thresh*sigma_old)))] = 1
            #check[ np.where( values<(average-(sigma_thresh*sigma_old)) ) ] = 1
            values = values[np.where(check < 1)]

            # Re-measure sigma and test for convergence
            sigma_new = np.std(values)
            diff = abs(sigma_old-sigma_new)/sigma_old

        # Perform final mask
        check = np.zeros([len(values)])
        check[np.where(values > (average+(sigma_thresh*sigma_old)))] = 1
        check[np.where(values < (average-(sigma_thresh*sigma_old)))] = 1
        values = values[np.where(check < 1)]

        # Return results
        return sigma_new,average,values


    def l1_templates_from_l0_dataset(self,measurandstring,datasetl0):
        """
        Makes all L1 templates for the data, and propagates the appropriate keywords from the L0 datasets.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """

        l1a_dim_sizes_dict = {"wavelength":len(datasetl0["wavelength"]),"scan":len(datasetl0["scan"])}
        if measurandstring=="radiance":
            l1a = HypernetsDSBuilder.create_ds_template(l1a_dim_sizes_dict,"L_L1A_RAD")
            l1a["wavelength"] = datasetl0["wavelength"]
        elif measurandstring=="irradiance":
            l1a = HypernetsDSBuilder.create_ds_template(l1a_dim_sizes_dict,"L_L1A_IRR")
            l1a["wavelength"] = datasetl0["wavelength"]

        l1b_dim_sizes_dict = {"wavelength":len(datasetl0["wavelength"]),"series":1}
        if measurandstring=="radiance":
            l1b = HypernetsDSBuilder.create_ds_template(l1b_dim_sizes_dict,"L_L1B_RAD")
            l1b["wavelength"] = datasetl0["wavelength"]
        elif measurandstring=="irradiance":
            l1b = HypernetsDSBuilder.create_ds_template(l1b_dim_sizes_dict,"L_L1B_IRR")
            l1b["wavelength"] = datasetl0["wavelength"]

        return l1a,l1b

    def process_measurement_function(self,measurandstring,dataset_l1,measurement_function,input_quantities,u_random_input_quantities,u_systematic_input_quantities):
        #print("here:",input_quantities)
        L0shape=input_quantities[0].shape
        for i in range(len(input_quantities)):
            if len(input_quantities[i].shape) < len(L0shape):
                input_quantities[i] = np.tile(input_quantities[i],(L0shape[1],1)).T
                u_random_input_quantities[i] = np.tile(u_random_input_quantities[i],(L0shape[1],1)).T
                u_systematic_input_quantities[i] = np.tile(u_systematic_input_quantities[i],(L0shape[1],1)).T
        print(L0shape)
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities)
        #u_systematic_measurand = self.prop.propagate_systematic(measurement_function,input_quantities,u_systematic_input_quantities)
        u_systematic_measurand,corr_systematic_measurand = self.prop.propagate_systematic(measurement_function,input_quantities,u_systematic_input_quantities,return_corr=True,corr_axis=0)
        #u_tot_measurand, cov_measurand = self.prop.propagate_both(measurement_function,input_quantities,u_random_input_quantities,u_systematic_input_quantities)
        #print(corr_systematic_radiance.shape,len(u_random_measurand))
        print(measurand.shape,input_quantities[0].shape)
        dataset_l1[measurandstring].values=measurand
        dataset_l1["u_random_"+measurandstring].values=u_random_measurand
        dataset_l1["u_systematic_"+measurandstring].values=u_systematic_measurand
        dataset_l1["corr_random_"+measurandstring].values=np.eye(len(u_random_measurand))
        print(corr_systematic_measurand.shape)
        dataset_l1["corr_systematic_"+measurandstring].values=corr_systematic_measurand

        return dataset_l1












