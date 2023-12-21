from punpy import MeasurementFunction

import scipy.interpolate
import numpy as np


class InterpolationTimeLinear(MeasurementFunction):
    def meas_function(self, output_time, input_time, irradiance):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """

        simpleint = True
        if len(input_time.shape) > 1:
            simpleint = False
            out = np.empty((len(irradiance), len(output_time)))
            for i in range(len(output_time)):
                if output_time[i] >= np.max(input_time[:, i]):
                    out[:, i] = irradiance[
                        :, input_time[:, i] == np.max(input_time[:, i]), i
                    ][:, 0]
                elif output_time[i] <= np.min(input_time[:, i]):
                    out[:, i] = irradiance[
                        :, input_time[:, i] == np.min(input_time[:, i]), i
                    ][:, 0]
                else:
                    irradiance_intfunc = scipy.interpolate.interp1d(
                        input_time[:, i], irradiance[:, :, i]
                    )
                    out[:, i] = irradiance_intfunc(output_time[i])

        elif hasattr(output_time, "__len__"):
            if len(output_time) > 1:
                simpleint = False
                out = np.empty((len(irradiance), len(output_time)))
                for i in range(len(output_time)):
                    if output_time[i] >= np.max(input_time):
                        out[:, i] = np.mean(
                            irradiance[:, input_time == np.max(input_time)], axis=1
                        ).squeeze()
                    elif output_time[i] <= np.min(input_time):
                        out[:, i] = np.mean(
                            irradiance[:, input_time == np.min(input_time)], axis=1
                        ).squeeze()
                    else:
                        irradiance_intfunc = scipy.interpolate.interp1d(
                            input_time, irradiance
                        )
                        out[:, i] = irradiance_intfunc(output_time[i])

        if simpleint:
            if output_time >= max(input_time):
                out = irradiance[:, input_time == max(input_time)]
            elif output_time <= min(input_time):
                out = irradiance[:, input_time == min(input_time)]
            else:
                irradiance_intfunc = scipy.interpolate.interp1d(input_time, irradiance)
                out = irradiance_intfunc(output_time)
        return out

    @staticmethod
    def get_name():
        return "InterpolationTimeLinear"

    def get_argument_names(self):
        return ["output_time", "input_time", "irradiance"]


class WaterNetworkInterpolationSkyRadianceLinear(MeasurementFunction):
    def meas_function(self, output_time, input_time, radiance):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """
        skyradiance_intfunc = scipy.interpolate.interp1d(input_time, radiance)

        return skyradiance_intfunc(output_time)

    @staticmethod
    def get_name():
        return "WaterNetworkInterpolationSkyRadianceLinear"

    def get_argument_names(self):
        return ["output_time", "input_time", "radiance"]
