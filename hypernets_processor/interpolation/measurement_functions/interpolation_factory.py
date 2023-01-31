"""
Measurement function object creator
"""

from hypernets_processor.version import __version__
from hypernets_processor.interpolation.measurement_functions.interpolate_time_linear import (
    InterpolationTimeLinear,
)
from hypernets_processor.interpolation.measurement_functions.interpolate_time_linear import (
    WaterNetworkInterpolationSkyRadianceLinear,
)
from hypernets_processor.interpolation.measurement_functions.interpolate_wav_linear import (
    InterpolationWavLinear,
)

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "30/03/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class InterpolationFactory:
    def __init__(self, *args, **kwargs):
        self.measurement_functions = dict(
            [
                (
                    InterpolationTimeLinear.get_name(),
                    InterpolationTimeLinear(*args, **kwargs),
                ),
                (
                    InterpolationWavLinear.get_name(),
                    InterpolationWavLinear(*args, **kwargs),
                ),
                (
                    WaterNetworkInterpolationSkyRadianceLinear.get_name(),
                    WaterNetworkInterpolationSkyRadianceLinear(*args, **kwargs),
                ),
            ]
        )

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self, name):
        return self.measurement_functions[name]
