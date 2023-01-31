from punpy import MeasurementFunction


class LandNetworkProtocol(MeasurementFunction):
    def meas_function(self, radiance, irradiance):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """

        return 3.14159265359 * radiance / irradiance

    @staticmethod
    def get_name():
        return "LandNetworkProtocol"

    def get_argument_names(self):
        return ["radiance", "irradiance"]
