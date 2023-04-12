"""
Measurement function object creator
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.measurement_functions.standard_measurement_function import (
    StandardMeasurementFunction,
)
from hypernets_processor.calibration.measurement_functions.template_measurement_function import (
    TemplateMeasurementFunction,
)

# from hypernets_processor.calibration.measurement_functions.standard_measurement_function_cython import StandardMeasurementFunctionCython

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "30/03/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class MeasurementFunctionFactory:
    def __init__(self, *args, **kwargs):
        self.measurement_functions = dict(
            [
                (
                    StandardMeasurementFunction.get_name(),
                    StandardMeasurementFunction(*args, **kwargs),
                ),
                # (StandardMeasurementFunctionCython.get_name(),StandardMeasurementFunctionCython()),
                (
                    TemplateMeasurementFunction.get_name(),
                    TemplateMeasurementFunction(*args, **kwargs),
                ),
            ]
        )

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self, name) -> object:
        return self.measurement_functions[name]
