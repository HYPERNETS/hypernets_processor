'''
Measurement function object creator
'''

from hypernets_processor.version import __version__
from hypernets_processor.interpolation.measurement_functions.water_network_interpolation import WaterNetworkInterpolationLinear
from hypernets_processor.interpolation.measurement_functions.land_network_interpolation_irradiance_linear import LandNetworkInterpolationIrradianceLinear

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "30/03/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class InterpolationFactory:
    def __init__(self):
        self.measurement_functions = dict([(WaterNetworkInterpolationLinear.get_name(),WaterNetworkInterpolationLinear()),
                                (LandNetworkInterpolationIrradianceLinear.get_name(),LandNetworkInterpolationIrradianceLinear())])

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self,name):
        return self.measurement_functions[name]
