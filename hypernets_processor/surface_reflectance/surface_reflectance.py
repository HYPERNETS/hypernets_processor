"""
Surface reflectance class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.surface_reflectance.measurement_functions.protocol_factory import ProtocolFactory
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.data_io.dataset_util import DatasetUtil

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


class SurfaceReflectance:
    def __init__(self, context, MCsteps=1000, parallel_cores=1):
        self._measurement_function_factory = ProtocolFactory()
        self.prop = punpy.MCPropagation(MCsteps, parallel_cores=parallel_cores)
        self.templ = DataTemplates(context=context)
        self.writer = HypernetsWriter(context)
        self.calibrate = Calibrate(context)
        self.plot = Plotting(context)
        self.context = context
        self.rh = RhymerHypstar(context)

    def process_l1d(self, dataset_l1c):
        dataset_l1c = self.perform_checks(dataset_l1c)
        l1ctol1d_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_surface_reflectance"))

        if self.context.get_config_value("network").lower() == "w":
            dataset_l1d = self.templ.l1d_from_l1c_dataset(dataset_l1c)

            # add required correction factors here - but better to add them in the function factory???
            epsilon, failSimil = self.rh.get_epsilon(dataset_l1c["reflectance_nosc"].values,
                                                  dataset_l1c["wavelength"].values)
            dataset_l1d["epsilon"].values = epsilon

            dataset_l1d["quality_flag"][np.where(failSimil == 1)] = DatasetUtil.set_flag(
                dataset_l1d["quality_flag"][np.where(failSimil == 1)], "simil_fail")  # for i in range(len(mask))]

            input_vars = l1ctol1d_function.get_argument_names()
            input_qty = self.find_input(input_vars, dataset_l1d)
            u_random_input_qty = self.find_u_random_input(input_vars, dataset_l1d)
            u_systematic_input_qty,cov_systematic_input_qty = \
                self.find_u_systematic_input(input_vars,dataset_l1d)

            print("inp",input_qty[4],u_random_input_qty[4],u_systematic_input_qty[4],cov_systematic_input_qty[4])

            dataset_l1d = self.process_measurement_function(
                ["water_leaving_radiance", "reflectance_nosc", "reflectance"],
                dataset_l1d, l1ctol1d_function.function, input_qty,
                u_random_input_qty,u_systematic_input_qty,cov_systematic_input_qty)

            if self.context.get_config_value("write_l1d"):
                self.writer.write(dataset_l1d, overwrite=True)

            return dataset_l1d

        elif self.context.get_config_value("network").lower() == "l":
            self.context.logger.error("no L1d processing for land network")
        else:
            self.context.logger.error("network is not correctly defined")


    def process_l2(self, dataset):
        dataset = self.perform_checks(dataset)
        l1tol2_function = self._measurement_function_factory.get_measurement_function(
            self.context.get_config_value("measurement_function_surface_reflectance"))
        input_vars = l1tol2_function.get_argument_names()
        input_qty = self.find_input(input_vars, dataset)
        u_random_input_qty = self.find_u_random_input(input_vars, dataset)
        u_systematic_input_qty, cov_systematic_input_qty = self.find_u_systematic_input(input_vars, dataset)


        if self.context.get_config_value("network").lower() == "w":
            dataset_l2a = self.templ.l2_from_l1d_dataset(dataset)
            for measurandstring in ["water_leaving_radiance", "reflectance_nosc", "reflectance"]:
                dataset_l2a[measurandstring].values = self.calc_mean_masked(dataset, measurandstring)
                dataset_l2a["u_random_" + measurandstring].values = self.calc_mean_masked(dataset,
                                                                                                    "u_random_" + measurandstring,
                                                                                                    rand_unc=True)
                dataset_l2a["u_systematic_" + measurandstring].values = self.calc_mean_masked(dataset,
                                                                                                        "u_systematic_" + measurandstring,
                                                                                                        rand_unc=True)
                dataset_l2a["corr_random_" + measurandstring].values = np.eye(
                    len(dataset_l2a["u_systematic_" + measurandstring].values))
                dataset_l2a["corr_systematic_" + measurandstring].values = self.calc_mean_masked(dataset,
                                                                                                           "corr_systematic_" + measurandstring,
                                                                                                           corr=True)
                if self.context.get_config_value("plot_l2a"):
                    self.plot.plot_series_in_sequence(measurandstring,dataset_l2a)

        elif self.context.get_config_value("network").lower() == "l":
            dataset_l2a = self.templ.l2_from_l1c_dataset(dataset)
            dataset_l2a = self.process_measurement_function(["reflectance"], dataset_l2a,
                                                            l1tol2_function.function,
                                                            input_qty, u_random_input_qty,
                                                            u_systematic_input_qty,
                                                            cov_systematic_input_qty)
            if self.context.get_config_value("plot_l2a"):
                self.plot.plot_series_in_sequence("reflectance",dataset_l2a)
                print("plotting")
        if self.context.get_config_value("write_l2a"):
            self.writer.write(dataset_l2a, overwrite=True)



        return dataset_l2a

    def calc_mean_masked(self, dataset, var, rand_unc=False, corr=False):
        series_id = np.unique(dataset['series_id'])
        if corr:
            out = np.empty((len(series_id), len(dataset['wavelength']), len(dataset['wavelength'])))
        else:
            out = np.empty((len(series_id), len(dataset['wavelength'])))
        for i in range(len(series_id)):
            flags = ["saturation","nonlinearity","bad_pointing","outliers",
                     "angles_missing","lu_eq_missing","fresnel_angle_missing",
                     "fresnel_default","temp_variability_ed","temp_variability_lu",
                     "min_nbred","min_nbrlu","min_nbrlsky"]
            flagged = np.any([DatasetUtil.unpack_flags(dataset['quality_flag'])[x] for x in flags],axis=0)
            ids = np.where(
                (dataset['series_id'] == series_id[i]) & (flagged == False))

            out[i] = np.mean(dataset[var].values[:, ids], axis=2)[:, 0]
            if rand_unc:
                out[i] = out[i] / len(ids[0])
        if corr:
            out = np.mean(out, axis=0)
        return out.T

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
        covs_indep = []
        for var in variables:
            try:
                covs_indep.append(punpy.convert_corr_to_cov(dataset["corr_systematic_indep_" + var].values,dataset["u_systematic_indep_" + var].values))
                inputs.append(dataset["u_systematic_indep_" + var].values)
            except:
                inputs.append(None)
                covs_indep.append(None)
        return inputs, covs_indep

    def perform_checks(self, dataset_l1):
        """
        Identifies and removes faulty measurements (e.g. due to cloud cover).

        :param dataset_l0:
        :type dataset_l0:
        :return:
        :rtype:
        """

        return dataset_l1


    def process_measurement_function(self, measurandstrings, dataset, measurement_function, input_quantities,
                                     u_random_input_quantities,
                                     u_systematic_input_quantities,
                                     cov_systematic_input_quantities):
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
                                                   cov_x=cov_systematic_input_quantities,
                                                   return_corr=True, repeat_dims=1,
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
                    self.prop.propagate_systematic(measurement_function,input_quantities,
                                                   u_systematic_input_quantities,
                                                   cov_x=cov_systematic_input_quantities,
                                                   return_corr=True,repeat_dims=1,
                                                   corr_axis=0,
                                                   output_vars=len(measurandstrings))
                measurandstring = measurandstrings[0]
                dataset[measurandstring].values = measurand
                dataset["u_random_" + measurandstring].values = u_random_measurand
                dataset["u_systematic_" + measurandstring].values = u_systematic_measurand
                dataset["corr_random_" + measurandstring].values = np.eye(len(u_random_measurand))
                dataset["corr_systematic_" + measurandstring].values = corr_systematic_measurand

        return dataset
