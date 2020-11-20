"""
Interpolation class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.interpolation.measurement_functions.interpolation_factory import InterpolationFactory
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

class Interpolate:
    def __init__(self,context,MCsteps=1000,parallel_cores=1):
        self._measurement_function_factory = InterpolationFactory()
        self.prop= punpy.MCPropagation(MCsteps,parallel_cores=parallel_cores)
        self.templ = DataTemplates(context=context)
        self.writer=HypernetsWriter(context)
        self.plot=Plotting(context)
        self.context=context

    def interpolate_l1b_w(self,dataset_l1a_rad,dataset_l1b_uprad, dataset_l1b_irr):
        # chek for upwelling radiance
        upscan = [i for i, e in enumerate(dataset_l1a_rad['viewing_zenith_angle'].values) if e <= 90]

        dataset_l1b=self.templ.l1b_template_from_l1a_dataset_water(dataset_l1a_rad)

        dataset_l1b["wavelength"] = dataset_l1a_rad["wavelength"]
        dataset_l1b["upwelling_radiance"] = dataset_l1a_rad["radiance"].sel(scan=upscan)
        dataset_l1b["acquisition_time"] = dataset_l1a_rad["acquisition_time"].sel(scan=upscan)
        # is this correct????
        dataset_l1b["u_random_upwelling_radiance"] = dataset_l1a_rad["u_random_radiance"].sel(scan=upscan)
        dataset_l1b["u_systematic_indep_upwelling_radiance"] = dataset_l1a_rad["u_systematic_indep_radiance"].sel(scan=upscan)
        dataset_l1b["u_systematic_corr_rad_irr_upwelling_radiance"] = dataset_l1a_rad["u_systematic_corr_rad_irr_radiance"].sel(scan=upscan)
        dataset_l1b["corr_random_upwelling_radiance"] = dataset_l1a_rad["corr_random_radiance"]
        dataset_l1b["corr_systematic_indep_upwelling_radiance"] = dataset_l1a_rad["corr_systematic_indep_radiance"]
        dataset_l1b["corr_systematic_corr_rad_irr_upwelling_radiance"] = dataset_l1a_rad["corr_systematic_corr_rad_irr_radiance"]

        self.context.logger.info("interpolate sky radiance")
        dataset_l1b=self.interpolate_skyradiance(dataset_l1b, dataset_l1b_uprad)
        self.context.logger.info("interpolate irradiances")
        dataset_l1b=self.interpolate_irradiance(dataset_l1b, dataset_l1b_irr)

        if self.context.get_config_value("write_l1b"):
            self.writer.write(dataset_l1b,overwrite=True)
        return dataset_l1b

    def interpolate_l1c(self,dataset_l1b_rad,dataset_l1b_irr):


        dataset_l1c=self.templ.l1c_from_l1b_dataset(dataset_l1b_rad)
        dataset_l1c["acquisition_time"].values = dataset_l1b_rad["acquisition_time"].values

        # dataset_l1c["radiance"].values = dataset_l1b_rad["radiance"].values
        # dataset_l1c["u_random_radiance"].values = dataset_l1b_rad["u_random_radiance"].values
        # dataset_l1c["u_systematic_indep_radiance"].values = dataset_l1b_rad["u_systematic_indep_radiance"].values
        # dataset_l1c["u_systematic_corr_rad_irr_radiance"].values = dataset_l1b_rad["u_systematic_corr_rad_irr_radiance"].values
        # dataset_l1c["corr_random_radiance"].values = dataset_l1b_rad["corr_random_radiance"].values
        # dataset_l1c["corr_systematic_indep_radiance"].values = dataset_l1b_rad["corr_systematic_indep_radiance"].values
        # dataset_l1c["corr_systematic_corr_rad_irr_radiance"].values = dataset_l1b_rad["corr_systematic_corr_rad_irr_radiance"].values

        dataset_l1c=self.interpolate_irradiance(dataset_l1c,dataset_l1b_irr)

        if self.context.get_config_value("write_l1c"):
            self.writer.write(dataset_l1c,overwrite=True)

        if self.context.get_config_value("plot_l1c"):
            self.plot.plot_series_in_sequence("irradiance",dataset_l1c)

        if self.context.get_config_value("plot_uncertainty"):
            self.plot.plot_relative_uncertainty("irradiance",dataset_l1c)

        if self.context.get_config_value("plot_correlation"):
            self.plot.plot_correlation("irradiance",dataset_l1c)

        return dataset_l1c

    def interpolate_irradiance(self,dataset_l1c,dataset_l1b_irr):
        measurement_function_interpolate=self.context.get_config_value('measurement_function_interpolate')
        interpolation_function = self._measurement_function_factory.get_measurement_function(measurement_function_interpolate)

        acqui_irr = dataset_l1b_irr['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values
        print("times",acqui_rad,acqui_irr)
        print(dataset_l1b_irr["u_systematic_indep_irradiance"].values.shape)
        cov_indep = punpy.convert_corr_to_cov(
            dataset_l1b_irr["corr_systematic_indep_irradiance"].values,
            np.mean(dataset_l1b_irr["u_systematic_indep_irradiance"].values,axis=1))
        cov_corr = punpy.convert_corr_to_cov(
            dataset_l1b_irr["corr_systematic_corr_rad_irr_irradiance"].values,
            np.mean(dataset_l1b_irr["u_systematic_corr_rad_irr_irradiance"].values,axis=1))

        dataset_l1c = self.process_measurement_function("irradiance",dataset_l1c,interpolation_function.function,
                                                        [acqui_rad,acqui_irr,dataset_l1b_irr['irradiance'].values],
                                                        [None,None,dataset_l1b_irr['u_random_irradiance'].values],
                                                        [None,None,dataset_l1b_irr['u_systematic_indep_irradiance'].values],
                                                        [None,None,dataset_l1b_irr['u_systematic_corr_rad_irr_irradiance'].values],
                                                        [None,None,cov_indep],
                                                        [None,None,cov_corr])
        return dataset_l1c

    def interpolate_skyradiance(self,dataset_l1c,dataset_l1a_skyrad):
        measurement_function_interpolate=self.context.get_config_value("measurement_function_interpolate")
        interpolation_function = self._measurement_function_factory.get_measurement_function(measurement_function_interpolate)

        acqui_irr = dataset_l1a_skyrad['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values

        cov_indep = punpy.convert_corr_to_cov(
            dataset_l1a_skyrad["corr_systematic_indep_radiance"].values,
            np.mean(dataset_l1a_skyrad["u_systematic_indep_radiance"].values,axis=1))
        cov_corr = punpy.convert_corr_to_cov(
            dataset_l1a_skyrad["corr_systematic_corr_rad_irr_radiance"].values,
            np.mean(dataset_l1a_skyrad["u_systematic_corr_rad_irr_radiance"].values,
                    axis=1))

        dataset_l1c = self.process_measurement_function("downwelling_radiance",dataset_l1c,
                                                        interpolation_function.function,
                                                        [acqui_rad,acqui_irr,
                                                         dataset_l1a_skyrad[
                                                             'radiance'].values],
                                                        [None,None,dataset_l1a_skyrad[
                                                            'u_random_radiance'].values],
                                                        [None,None,dataset_l1a_skyrad[
                                                            'u_systematic_indep_radiance'].values],
                                                        [None,None,dataset_l1a_skyrad[
                                                            'u_systematic_corr_rad_irr_radiance'].values],
                                                        [None,None,cov_indep],
                                                        [None,None,cov_corr])
        return dataset_l1c

    def process_measurement_function(self,measurandstring,dataset,measurement_function,
                                     input_quantities,u_random_input_quantities,
                                     u_systematic_input_quantities_indep,
                                     u_systematic_input_quantities_corr,
                                     cov_systematic_input_quantities_indep,
                                     cov_systematic_input_quantities_corr):

        # datashape = input_quantities[0].shape
        # for i in range(len(input_quantities)):
        #     if len(input_quantities[i].shape) > len(datashape):
        #         datashape = input_quantities[0].shape
        #
        # for i in range(len(input_quantities)):
        #     print(input_quantities[i].shape)
        #     if len(input_quantities[i].shape) < len(datashape):
        #         if input_quantities[i].shape[0]==datashape[1]:
        #             input_quantities[i] = np.tile(input_quantities[i],(datashape[0],1))
        #         else:
        #             input_quantities[i] = np.tile(input_quantities[i],(datashape[1],1)).T
        #     print(input_quantities[i].shape)
        #
        #     if u_random_input_quantities[i] is not None:
        #         if len(u_random_input_quantities[i].shape) < len(datashape):
        #             u_random_input_quantities[i] = np.tile(u_random_input_quantities[i], (datashape[1], 1)).T
        #     if u_systematic_input_quantities_indep[i] is not None:
        #         if len(u_systematic_input_quantities_indep[i].shape) < len(datashape):
        #             u_systematic_input_quantities_indep[i] = np.tile(u_systematic_input_quantities_indep[i], (datashape[1], 1)).T
        #     if u_systematic_input_quantities_corr[i] is not None:
        #         if len(u_systematic_input_quantities_corr[i].shape) < len(datashape):
        #             u_systematic_input_quantities_corr[i] = np.tile(u_systematic_input_quantities_corr[i], (datashape[1], 1)).T
        measurand = measurement_function(*input_quantities)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u_random_measurand = self.prop.propagate_random(measurement_function,
                                                            input_quantities,
                                                            u_random_input_quantities,
                                                        param_fixed=[False,True,True],
                                                        repeat_dims=1)
            u_syst_measurand_indep,corr_syst_measurand_indep = self.prop.propagate_systematic(
                measurement_function,input_quantities,
                u_systematic_input_quantities_indep,
                cov_x=cov_systematic_input_quantities_indep,return_corr=True,
                corr_axis=0,param_fixed=[False,True,True],repeat_dims=1)
            u_syst_measurand_corr,corr_syst_measurand_corr = self.prop.propagate_systematic(
                measurement_function,input_quantities,u_systematic_input_quantities_corr,
                cov_x=cov_systematic_input_quantities_corr,return_corr=True,
                corr_axis=0,param_fixed=[False,True,True],repeat_dims=1)
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
