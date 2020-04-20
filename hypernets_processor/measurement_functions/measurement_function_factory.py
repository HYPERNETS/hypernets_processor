'''
Measurement function object creator
'''

from hypernets_processor.version import __version__
from hypernets_processor.measurement_functions.standard_measurement_function import StandardMeasurementFunction
from hypernets_processor.measurement_functions.template_measurement_function import TemplateMeasurementFunction

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "30/03/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class MeasurementFunctionFactory:
    def __init__(self):
        self.measurement_functions = dict([(StandardMeasurementFunction.get_name(),StandardMeasurementFunction()),
                                (TemplateMeasurementFunction.get_name(),TemplateMeasurementFunction())])

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self,name):
        return self.measurement_functions[name]
