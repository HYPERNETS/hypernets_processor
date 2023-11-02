from punpy import MeasurementFunction
import numpy as np


class WaterNetworkProtocolWaterLeavingRadiance(MeasurementFunction):
    def meas_function(self, upwelling_radiance, downwelling_radiance, rhof
    ):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """

        # default water network processing
        water_leaving_radiance = np.array(
            [
                (upwelling_radiance[w] - (rhof * downwelling_radiance[w]))
                for w in range(len(downwelling_radiance))
            ]
        )

        return water_leaving_radiance

    @staticmethod
    def get_name():
        return "WaterNetworkProtocolWaterLeavingRadiance"

    def get_argument_names(self):
        return [
            "upwelling_radiance",
            "downwelling_radiance",
            "rhof",
        ]