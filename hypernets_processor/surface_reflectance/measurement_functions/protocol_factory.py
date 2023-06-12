"""
Measurement function object creator
"""

from hypernets_processor.version import __version__
from hypernets_processor.surface_reflectance.measurement_functions.land_network_protocol import (
    LandNetworkProtocol,
)
from hypernets_processor.surface_reflectance.measurement_functions.water_network_protocol import (
    WaterNetworkProtocol,
)

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "30/04/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class ProtocolFactory:
    def __init__(self, *args, **kwargs):
        self.measurement_functions = dict(
            [
                (LandNetworkProtocol.get_name(), LandNetworkProtocol(*args, **kwargs)),
                (
                    WaterNetworkProtocol.get_name(),
                    WaterNetworkProtocol(*args, **kwargs),
                ),
            ]
        )

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self, name):
        return self.measurement_functions[name]

class ProtocolFactoryOld:
    def __init__(self, context):
        self.measurement_functions = dict([(LandNetworkProtocol.get_name(),LandNetworkProtocol()),
                                        (WaterNetworkProtocol.get_name(),WaterNetworkProtocol(context))])

    def get_names(self):
        return self.measurement_functions.keys()

    def get_measurement_function(self,name):
        return self.measurement_functions[name]