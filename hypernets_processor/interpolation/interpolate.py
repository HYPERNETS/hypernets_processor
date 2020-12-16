"""
Interpolation class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.interpolation.measurement_functions.interpolation_factory import InterpolationFactory
from hypernets_processor.data_utils.propagate_uncertainties import PropagateUnc

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
        self.prop = PropagateUnc(context, MCsteps, parallel_cores=parallel_cores)
        self.templ = DataTemplates(context=context)
        self.writer=HypernetsWriter(context)
        self.plot=Plotting(context)
        self.context=context

    def interpolate_l1b_w(self, dataset_l1b, dataset_l1a_uprad,dataset_l1b_downrad, dataset_l1b_irr):

        # chek for upwelling radiance
        upscan = [i for i, e in enumerate(dataset_l1a_uprad['viewing_zenith_angle'].values) if e < 90]

        dataset_l1b=self.templ.l1b_template_from_l1a_dataset_water(dataset_l1a_uprad)

        dataset_l1b["wavelength"] = dataset_l1a_uprad["wavelength"]
        dataset_l1b["upwelling_radiance"] = dataset_l1a_uprad["radiance"].sel(scan=upscan)
        dataset_l1b["acquisition_time"] = dataset_l1a_uprad["acquisition_time"].sel(scan=upscan)
        # is this correct????
        dataset_l1b["u_random_upwelling_radiance"] = dataset_l1a_uprad["u_random_radiance"].sel(scan=upscan)
        dataset_l1b["u_systematic_indep_upwelling_radiance"] = dataset_l1a_uprad["u_systematic_indep_radiance"].sel(scan=upscan)
        dataset_l1b["u_systematic_corr_rad_irr_upwelling_radiance"] = dataset_l1a_uprad["u_systematic_corr_rad_irr_radiance"].sel(scan=upscan)
        dataset_l1b["corr_random_upwelling_radiance"] = dataset_l1a_uprad["corr_random_radiance"]
        dataset_l1b["corr_systematic_indep_upwelling_radiance"] = dataset_l1a_uprad["corr_systematic_indep_radiance"]
        dataset_l1b["corr_systematic_corr_rad_irr_upwelling_radiance"] = dataset_l1a_uprad["corr_systematic_corr_rad_irr_radiance"]

        self.context.logger.info("interpolate sky radiance")
        dataset_l1b=self.interpolate_skyradiance(dataset_l1b, dataset_l1b_downrad)
        self.context.logger.info("interpolate irradiances")
        dataset_l1b=self.interpolate_irradiance(dataset_l1b, dataset_l1b_irr)

        if self.context.get_config_value("write_l1b"):
            self.writer.write(dataset_l1b,overwrite=True)
        return dataset_l1b

    def interpolate_l1c(self,dataset_l1b_rad,dataset_l1b_irr):


        dataset_l1c=self.templ.l1c_from_l1b_dataset(dataset_l1b_rad)
        dataset_l1c["acquisition_time"].values = dataset_l1b_rad["acquisition_time"].values

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
        measurement_function_interpolate_wav = self.context.get_config_value(
            'measurement_function_interpolate_wav')
        interpolation_function_wav = self._measurement_function_factory\
            .get_measurement_function(measurement_function_interpolate_wav)

        measurement_function_interpolate_time = self.context.get_config_value(
            'measurement_function_interpolate_time')
        interpolation_function_time = self._measurement_function_factory\
            .get_measurement_function(measurement_function_interpolate_time)

        # Interpolate in wavelength to radiance wavelengths
        wavs_rad=dataset_l1c["wavelength"].values
        wavs_irr=dataset_l1b_irr["wavelength"].values

        dataset_l1c_temp = self.templ.l1ctemp_dataset(dataset_l1c,dataset_l1b_irr)

        dataset_l1c_temp = self.prop.process_measurement_function_l1("irradiance",
            dataset_l1c_temp,interpolation_function_wav.function,
            [wavs_rad,wavs_irr,dataset_l1b_irr['irradiance'].values],
            [None,None,dataset_l1b_irr['u_random_irradiance'].values],
            [None,None,dataset_l1b_irr['u_systematic_indep_irradiance'].values],
            [None,None,dataset_l1b_irr['u_systematic_corr_rad_irr_irradiance'].values],
            [None,None,dataset_l1b_irr["corr_systematic_indep_irradiance"].values],
            [None,None,dataset_l1b_irr["corr_systematic_corr_rad_irr_irradiance"].values],
            )

        # Interpolate in time to radiance times
        acqui_irr = dataset_l1b_irr['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values

        dataset_l1c = self.prop.process_measurement_function_l1("irradiance",
            dataset_l1c,interpolation_function_time.function,
            [acqui_rad,acqui_irr,dataset_l1c_temp['irradiance'].values],
            [None,None,dataset_l1c_temp['u_random_irradiance'].values],
            [None,None,dataset_l1c_temp['u_systematic_indep_irradiance'].values],
            [None,None,dataset_l1c_temp['u_systematic_corr_rad_irr_irradiance'].values],
            [None,None,dataset_l1c_temp["corr_systematic_indep_irradiance"].values],
            [None,None,dataset_l1c_temp["corr_systematic_corr_rad_irr_irradiance"].values],
            param_fixed=[False,True,True])
        return dataset_l1c

    def interpolate_skyradiance(self,dataset_l1c,dataset_l1a_skyrad):
        measurement_function_interpolate_time = self.context.get_config_value(
            'measurement_function_interpolate_time')
        interpolation_function_time = self._measurement_function_factory\
            .get_measurement_function(measurement_function_interpolate_time)

        acqui_irr = dataset_l1a_skyrad['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values

        dataset_l1c = self.prop.process_measurement_function_l1("downwelling_radiance",dataset_l1c,
                                                        interpolation_function_time.function,
                                                        [acqui_rad,acqui_irr,
                                                         dataset_l1a_skyrad[
                                                             'radiance'].values],
                                                        [None,None,dataset_l1a_skyrad[
                                                            'u_random_radiance'].values],
                                                        [None,None,dataset_l1a_skyrad[
                                                            'u_systematic_indep_radiance'].values],
                                                        [None,None,dataset_l1a_skyrad[
                                                            'u_systematic_corr_rad_irr_radiance'].values],
                                                        [None,None,dataset_l1a_skyrad["corr_systematic_indep_radiance"].values],
                                                        [None,None,dataset_l1a_skyrad["corr_systematic_corr_rad_irr_radiance"].values],
                                                        param_fixed=[False,True,True])
        return dataset_l1c

