"""
Measurement function object creator
"""

from hypernets_processor.version import __version__
from hypernets_processor.combine_SWIR.measurement_functions.sliding_average_combine import (
    SlidingAverageCombine,
)
from hypernets_processor.combine_SWIR.measurement_functions.step_combine import (
    StepCombine,
)

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "30/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class CombineFactory:
    def __init__(self, *args, **kwargs):
        self.measurement_functions = dict(
            [
                (
                    SlidingAverageCombine.get_name(),
                    SlidingAverageCombine(*args, **kwargs),
                ),
                (StepCombine.get_name(), StepCombine(*args, **kwargs)),
            ]
        )

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self, name):
        return self.measurement_functions[name]
