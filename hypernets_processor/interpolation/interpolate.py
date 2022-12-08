"""
Interpolation class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.interpolation.measurement_functions.interpolation_factory import InterpolationFactory
from hypernets_processor.data_utils.quality_checks import QualityChecks
from obsarray.templater.dataset_util import DatasetUtil
import numpy as np
import punpy

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

class Interpolate:
    def __init__(self,context,parallel_cores=1):
        self._measurement_function_factory = InterpolationFactory
        self.qual = QualityChecks(context)
        self.templ = DataTemplates(context=context)
        self.writer=HypernetsWriter(context)
        self.plot=Plotting(context)
        self.context=context

    def interpolate_l1b_w(self, dataset_l1b, dataset_l1a_uprad,dataset_l1b_downrad, dataset_l1b_irr):

        # chek for upwelling radiance
        upscan = [i for i, e in enumerate(dataset_l1a_uprad['viewing_zenith_angle'].values) if e < 90]
        dataset_l1b["wavelength"] = dataset_l1a_uprad["wavelength"]
        dataset_l1b["upwelling_radiance"] = dataset_l1a_uprad["radiance"].sel(scan=upscan)
        dataset_l1b["acquisition_time"] = dataset_l1a_uprad["acquisition_time"].sel(scan=upscan)
        # is this correct????
        dataset_l1b["u_rel_random_upwelling_radiance"] = dataset_l1a_uprad["u_rel_random_radiance"].sel(scan=upscan)
        dataset_l1b["u_rel_systematic_indep_upwelling_radiance"] = dataset_l1a_uprad["u_rel_systematic_indep_radiance"].sel(scan=upscan)
        dataset_l1b["u_rel_systematic_corr_rad_irr_upwelling_radiance"] = dataset_l1a_uprad["u_rel_systematic_corr_rad_irr_radiance"].sel(scan=upscan)
        dataset_l1b["err_corr_systematic_indep_upwelling_radiance"] = dataset_l1a_uprad["err_corr_systematic_indep_radiance"]
        dataset_l1b["err_corr_systematic_corr_rad_irr_upwelling_radiance"] = dataset_l1a_uprad["err_corr_systematic_corr_rad_irr_radiance"]

        self.context.logger.info("interpolate sky radiance")
        dataset_l1b=self.interpolate_skyradiance(dataset_l1b, dataset_l1b_downrad)
        self.context.logger.info("interpolate irradiances")
        dataset_l1b=self.interpolate_irradiance(dataset_l1b, dataset_l1b_irr)
        return dataset_l1b

    def interpolate_l1c(self,dataset_l1b_rad,dataset_l1b_irr):

        dataset_l1c=self.templ.l1c_from_l1b_dataset(dataset_l1b_rad)
        dataset_l1c["acquisition_time"].values = dataset_l1b_rad["acquisition_time"].values

        #dataset_l1b_rad,dataset_l1b_irr=self.qual.perform_quality_check_interpolate(dataset_l1b_rad,dataset_l1b_irr)

        dataset_l1c=self.interpolate_irradiance(dataset_l1c,dataset_l1b_irr)

        if self.context.get_config_value("write_l1c"):
            self.writer.write(dataset_l1c,overwrite=True, remove_vars_strings=self.context.get_config_value("remove_vars_strings"))

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
        prop = punpy.MCPropagation(self.context.get_config_value("mcsteps"),dtype="float32")
        interpolation_function_wav = self._measurement_function_factory(prop=prop,repeat_dims=1,yvariable="irradiance").get_measurement_function(measurement_function_interpolate_wav)

        measurement_function_interpolate_time = self.context.get_config_value(
            'measurement_function_interpolate_time')
        prop = punpy.MCPropagation(self.context.get_config_value("mcsteps"),parallel_cores=1,dtype="float32")
        interpolation_function_time = self._measurement_function_factory(prop=prop,corr_dims="wavelength",yvariable="irradiance",param_fixed=[False,True,True]).get_measurement_function(measurement_function_interpolate_time)

        dataset_l1c_temp = self.templ.l1ctemp_dataset(dataset_l1c,dataset_l1b_irr)

        dataset_l1c_temp=interpolation_function_wav.propagate_ds_specific(
            ["random","systematic_indep","systematic_corr_rad_irr"],
            dataset_l1c.rename({"wavelength":"radiance_wavelength"}),
            dataset_l1b_irr.rename({"wavelength":"irradiance_wavelength"}),
            ds_out_pre=dataset_l1c_temp,
            store_unc_percent=True)

        # Interpolate in time to radiance times
        acqui_rad = dataset_l1c['acquisition_time'].values

        flagged = DatasetUtil.get_flags_mask_or(dataset_l1b_irr['quality_flag'])
        mask_notflagged=np.where(flagged == False)[0]
        if len(mask_notflagged)==0:
            self.context.anomaly_handler.add_anomaly("i")
            acqui_irr = dataset_l1b_irr['acquisition_time'].values
        else:
            dataset_l1c_temp=dataset_l1c_temp.isel(series=mask_notflagged)
            acqui_irr = dataset_l1b_irr['acquisition_time'].values[mask_notflagged]

        dataset_l1c=interpolation_function_time.propagate_ds_specific(
            ["random","systematic_indep","systematic_corr_rad_irr"],
            dataset_l1c_temp,
            {"input_time": acqui_irr, "output_time": acqui_rad},
            ds_out_pre=dataset_l1c,
            store_unc_percent=True)

        if len(acqui_irr)==1:
            dataset_l1c["quality_flag"] = DatasetUtil.set_flag(
                dataset_l1c["quality_flag"], "single_irradiance_used"
            )

        return dataset_l1c

    def interpolate_skyradiance(self,dataset_l1c,dataset_l1a_skyrad):
        measurement_function_interpolate_time = self.context.get_config_value(
            'measurement_function_interpolate_time')
        prop = punpy.MCPropagation(self.context.get_config_value("mcsteps"),parallel_cores=1,dtype="float32")
        interpolation_function_time = self._measurement_function_factory(prop=prop,corr_dims="wavelength",yvariable="downwelling_radiance",param_fixed=[False,True,True]).get_measurement_function("WaterNetworkInterpolationSkyRadianceLinear")

        acqui_irr = dataset_l1a_skyrad['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values

        print(acqui_rad.shape,dataset_l1c.wavelength,dataset_l1a_skyrad.wavelength)

        dataset_l1c=interpolation_function_time.propagate_ds_specific(
            ["random","systematic_indep","systematic_corr_rad_irr"],
            dataset_l1a_skyrad,
            {"input_time": acqui_irr, "output_time": acqui_rad},
            ds_out_pre=dataset_l1c,
            store_unc_percent=True)

        if len(acqui_irr)==1:
            dataset_l1c["quality_flag"] = DatasetUtil.set_flag(
                dataset_l1c["quality_flag"], "single_irradiance_used"
            )

        # dataset_l1c = self.prop.process_measurement_function_l1("downwelling_radiance",dataset_l1c,
        #                                                 interpolation_function_time.meas_function,
        #                                                 [acqui_rad,acqui_irr,
        #                                                  dataset_l1a_skyrad[
        #                                                      'radiance'].values],
        #                                                 [None,None,dataset_l1a_skyrad[
        #                                                     'u_rel_random_radiance'].values*dataset_l1a_skyrad[
        #                                                      'radiance'].values/100],
        #                                                 [None,None,dataset_l1a_skyrad[
        #                                                     'u_rel_systematic_indep_radiance'].values*dataset_l1a_skyrad[
        #                                                      'radiance'].values/100],
        #                                                 [None,None,dataset_l1a_skyrad[
        #                                                     'u_rel_systematic_corr_rad_irr_radiance'].values*dataset_l1a_skyrad[
        #                                                      'radiance'].values/100],
        #                                                 [None,None,dataset_l1a_skyrad["err_corr_systematic_indep_radiance"].values],
        #                                                 [None,None,dataset_l1a_skyrad["err_corr_systematic_corr_rad_irr_radiance"].values],
        #                                                 param_fixed=[False,True,True])
        return dataset_l1c

