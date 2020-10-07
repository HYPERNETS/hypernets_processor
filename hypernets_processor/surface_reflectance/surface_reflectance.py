"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.surface_reflectance.measurement_functions.protocol_factory import ProtocolFactory
from hypernets_processor.calibration.calibrate import Calibrate

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
        self.calibrate=Calibrate(context)
        self.context = context

    def process(self,dataset_l1c):
        dataset_l1c = self.perform_checks(dataset_l1c)
        l1tol2_function = self._measurement_function_factory.get_measurement_function(self.context.get_config_value("measurement_function_surface_reflectance"))
        input_vars = l1tol2_function.get_argument_names()
        input_qty = self.find_input(input_vars,dataset_l1c)
        u_random_input_qty = self.find_u_random_input(input_vars,dataset_l1c)
        u_systematic_input_qty = self.find_u_systematic_input(input_vars,dataset_l1c)

        if self.context.get_config_value("network")=="W":
            dataset_l1d = self.l1d_from_l1c_dataset(dataset_l1c)
            dataset_l2a = self.l2_from_l1d_dataset(dataset_l1d)

            dataset_l1d = self.process_measurement_function(["nlw","rhow_nosc","rhow"],
                dataset_l1d,l1tol2_function.function,input_qty,u_random_input_qty,
                u_systematic_input_qty)
            for measurandstring in ["nlw","rhow_nosc","rhow"]:
                dataset_l2a[measurandstring].values = self.calibrate.calc_mean_masked(dataset_l1d, measurandstring)
                dataset_l2a["u_random_" + measurandstring].values = self.calibrate.calc_mean_masked(dataset_l1d,
                                                                                          "u_random_" + measurandstring,
                                                                                          rand_unc=True)
                dataset_l2a["u_systematic_" + measurandstring].values = self.calibrate.calc_mean_masked(dataset_l1d,
                                                                                              "u_systematic_" + measurandstring)
                dataset_l2a["corr_random_" + measurandstring].values = np.eye(
                    len(dataset_l2a["u_systematic_" + measurandstring].values))
                dataset_l2a["corr_systematic_" + measurandstring].values = self.calibrate.calc_mean_masked(dataset_l1d,
                                                                                                 "corr_systematic_" + measurandstring,
                                                                                                 corr=True)
            self.writer.write(dataset_l2a,overwrite=True)
            self.writer.write(dataset_l1d,overwrite=True)
            return dataset_l2a, dataset_l1d

        elif self.context.get_config_value("network")=="L":
            dataset_l2a = self.l2_from_l1c_dataset(dataset_l1c)
            dataset_l2a = self.process_measurement_function(["reflectance"],dataset_l2a,
                                                           l1tol2_function.function,
                                                           input_qty,u_random_input_qty,
                                                           u_systematic_input_qty)

            self.writer.write(dataset_l2a,overwrite=True)
            return dataset_l2a

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

    def l1d_from_l1c_dataset(self,datasetl1c):
        """
        Makes a L2 template of the data, and propagates the appropriate keywords from L1.

        :param datasetl0:
        :type datasetl0:
        :return:
        :rtype:
        """
        if self.context.get_config_value("network") == "L":
            print("No L1D level for land")

        elif self.context.get_config_value("network") == "W":
            l1d_dim_sizes_dict = {"wavelength": len(datasetl1c["wavelength"]),
                                  "scan": len(datasetl1c["scan"])}
            dataset_l1d = self.hdsb.create_ds_template(l1d_dim_sizes_dict, "W_L1D", propagate_ds=datasetl1c)

        return dataset_l1d

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
                                  "series":len(datasetl1c['series_id'])}
            dataset_l2a = self.hdsb.create_ds_template(l2a_dim_sizes_dict, "L_L2A", propagate_ds=datasetl1c)

        return dataset_l2a

    def l2_from_l1d_dataset(self,datasetl1d):

        if self.context.get_config_value("network") == "W":
            l2a_dim_sizes_dict = {"wavelength": len(datasetl1d["wavelength"]),
                                  "series": len(np.unique(datasetl1d['series_id']))}
            dataset_l2a = self.hdsb.create_ds_template(l2a_dim_sizes_dict, "W_L2A", propagate_ds=datasetl1d)

            series_id = np.unique(datasetl1d['series_id'])
            dataset_l2a["series_id"].values = series_id

            for variablestring in ["acquisition_time","viewing_azimuth_angle",
                                   "viewing_zenith_angle","solar_azimuth_angle",
                                   "solar_zenith_angle"]:
                temp_arr = np.empty(len(series_id))
                for i in range(len(series_id)):
                    ids = np.where((datasetl1d['series_id'] == series_id[i]) & (
                            datasetl1d['quality_flag'] == 1))
                    temp_arr[i] = np.mean(datasetl1d[variablestring].values[ids])
                dataset_l2a[variablestring].values = temp_arr

        return dataset_l2a

    def process_measurement_function(self,measurandstrings,dataset,measurement_function,input_quantities,u_random_input_quantities,
                                     u_systematic_input_quantities):
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities,repeat_dims=1,output_vars=len(measurandstrings))

        if len(measurandstrings)>1:
            u_systematic_measurand,corr_systematic_measurand,corr_between = self.prop.propagate_systematic(measurement_function,
                                                                                          input_quantities,
                                                                                          u_systematic_input_quantities,cov_x=['rand']*len(u_systematic_input_quantities),
                                                                                          return_corr=True,repeat_dims=1,corr_axis=0,output_vars=len(measurandstrings))
            for im, measurandstring in enumerate(measurandstrings):
                print(np.array(measurand[im]).shape,np.array(u_random_measurand).shape)
                dataset[measurandstring].values = measurand[im]
                dataset["u_random_"+measurandstring].values = u_random_measurand[im]
                dataset["u_systematic_"+measurandstring].values = u_systematic_measurand[im]
                dataset["corr_random_"+measurandstring].values = np.eye(len(u_random_measurand[im]))
                dataset["corr_systematic_"+measurandstring].values = corr_systematic_measurand[im]

        else:
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







