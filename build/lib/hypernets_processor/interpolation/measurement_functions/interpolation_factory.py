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

from hypernets_processor.interpolation.measurement_functions.interpolate_wav_clearsky import (
    InterpolationWavClearSky,
)

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "30/03/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"

interpolators = [
    InterpolationTimeLinear,
    WaterNetworkInterpolationSkyRadianceLinear,
    InterpolationWavLinear,
    InterpolationWavClearSky,
]


class InterpolationFactory:
    def __init__(self, *args, **kwargs):
        self.measurement_functions = dict(
            [
                (
                    interpolator.get_name(),
                    interpolator(*args, **kwargs),
                )
                for interpolator in interpolators
            ]
        )

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self, name):
        return self.measurement_functions[name]
