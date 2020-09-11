"""
Interpolation class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.interpolation.measurement_functions.interpolation_factory import InterpolationFactory
import punpy
import numpy as np

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "12/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

class InterpolateL1c:
    def __init__(self,context,MCsteps=1000,parallel_cores=1):
        self._measurement_function_factory = InterpolationFactory()
        self.prop= punpy.MCPropagation(MCsteps,parallel_cores=parallel_cores)
        self.hdsb = HypernetsDSBuilder(context=context)
        self.writer=HypernetsWriter(context)
        self.context=context

    def interpolate_l1b_w(self,dataset_l1a_rad,dataset_l1b_uprad, dataset_l1b_irr,measurement_function):
        # chek for upwelling radiance
        upscan = [i for i, e in enumerate(dataset_l1a_rad['viewing_zenith_angle'].values) if e <= 90]

        print("upscan {}".format(upscan) + "is the same as L1A-rad {}".format(len(dataset_l1a_rad.scan)))

        l1b_dim_sizes_dict = {"wavelength":len(dataset_l1a_rad["wavelength"]),
                              "scan":len(upscan)}

        dataset_l1b = self.hdsb.create_ds_template(l1b_dim_sizes_dict,"W_L1B")
        dataset_l1b["wavelength"] = dataset_l1a_rad["wavelength"]
        dataset_l1b["upwelling_radiance"] = dataset_l1a_rad["radiance"].sel(scan=upscan)
        dataset_l1b["acquisition_time"] = dataset_l1a_rad["acquisition_time"].sel(scan=upscan)
        # is this correct????
        dataset_l1b["u_random_upwelling_radiance"] = dataset_l1a_rad["u_random_radiance"].sel(scan=upscan)
        dataset_l1b["u_systematic_upwelling_radiance"] = dataset_l1a_rad["u_systematic_radiance"].sel(scan=upscan)
        dataset_l1b["corr_random_upwelling_radiance"] = dataset_l1a_rad["corr_random_radiance"]
        dataset_l1b["corr_systematic_upwelling_radiance"] = dataset_l1a_rad["corr_systematic_radiance"]
        print("interpolate sky radiance")
        dataset_l1b=self.interpolate_skyradiance(dataset_l1b, dataset_l1b_uprad, measurement_function)
        print("interpolate irradiances")
        dataset_l1b=self.interpolate_irradiance(dataset_l1b, dataset_l1b_irr, measurement_function)
        self.writer.write(dataset_l1b,overwrite=True)
        return dataset_l1b

    def interpolate_l1c(self,dataset_l1b_rad,dataset_l1b_irr,measurement_function):
        l1c_dim_sizes_dict = {"wavelength":len(dataset_l1b_rad["wavelength"]),
                              "series":len(dataset_l1b_rad['series'])}

        dataset_l1c = self.hdsb.create_ds_template(l1c_dim_sizes_dict,"L_L1C")
        dataset_l1c["wavelength"] = dataset_l1b_rad["wavelength"]
        dataset_l1c["acquisition_time"] = dataset_l1b_rad["acquisition_time"]

        dataset_l1c["radiance"] = dataset_l1b_rad["radiance"]
        dataset_l1c["u_random_radiance"] = dataset_l1b_rad["u_random_radiance"]
        dataset_l1c["u_systematic_radiance"] = dataset_l1b_rad["u_systematic_radiance"]
        dataset_l1c["corr_random_radiance"] = dataset_l1b_rad["corr_random_radiance"]
        dataset_l1c["corr_systematic_radiance"] = dataset_l1b_rad["corr_systematic_radiance"]

        dataset_l1c=self.interpolate_irradiance(dataset_l1c,dataset_l1b_irr,measurement_function)

        self.writer.write(dataset_l1c,overwrite=True)
        return dataset_l1c

    def interpolate_irradiance(self,dataset_l1c,dataset_l1b_irr,measurement_function):
        interpolation_function = self._measurement_function_factory.get_measurement_function(measurement_function)

        acqui_irr = dataset_l1b_irr['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values
        dataset_l1c = self.process_measurement_function("irradiance",dataset_l1c,interpolation_function.function,
                                                        [acqui_rad,acqui_irr,dataset_l1b_irr['irradiance'].values],
                                                        [None,None,dataset_l1b_irr['u_random_irradiance'].values],
                                                        [None,None,dataset_l1b_irr['u_systematic_irradiance'].values])
        return dataset_l1c

    def interpolate_skyradiance(self,dataset_l1c,dataset_l1a_skyrad,measurement_function):
        interpolation_function = self._measurement_function_factory.get_measurement_function(measurement_function)

        acqui_irr = dataset_l1a_skyrad['acquisition_time'].values
        acqui_rad = dataset_l1c['acquisition_time'].values


        # haw can I pass the new name : "u_random_downwelling_radiance and u_systematic_downwelling_radiance"?
        dataset_l1c = self.process_measurement_function("downwelling_radiance",dataset_l1c,interpolation_function.function,
                                                        [acqui_rad,acqui_irr,dataset_l1a_skyrad['radiance'].values],
                                                        [None,None,dataset_l1a_skyrad['u_random_radiance'].values],
                                                        [None,None,dataset_l1a_skyrad['u_systematic_radiance'].values])
        return dataset_l1c



    def process_measurement_function(self,measurandstring,dataset,measurement_function,input_quantities,u_random_input_quantities,
                                     u_systematic_input_quantities):
        measurand = measurement_function(*input_quantities)
        u_random_measurand = self.prop.propagate_random(measurement_function,input_quantities,u_random_input_quantities)
        u_systematic_measurand,corr_systematic_measurand = self.prop.propagate_systematic(measurement_function,
                                                                                          input_quantities,
                                                                                          u_systematic_input_quantities,
                                                                                          return_corr=True,corr_axis=0)
        dataset[measurandstring].values = measurand
        dataset["u_random_"+measurandstring].values = u_random_measurand
        dataset["u_systematic_"+measurandstring].values = u_systematic_measurand
        # If following two lines are not commented: "ValueError: replacement data must match the Variable's shape"
        # dataset["corr_random_"+measurandstring].values = np.eye(len(u_random_measurand))
        # dataset["corr_systematic_"+measurandstring].values = corr_systematic_measurand

        return dataset



