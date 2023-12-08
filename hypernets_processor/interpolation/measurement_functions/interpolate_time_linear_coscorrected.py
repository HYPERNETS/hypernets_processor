from punpy import MeasurementFunction

import scipy.interpolate
import numpy as np


class InterpolationTimeLinearCoscorrected(MeasurementFunction):
    def meas_function(self, output_time, times, irradiance, output_sza, input_sza):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """

        irradiance = irradiance / np.cos(np.pi / 180.0 * input_sza)

        simpleint = True
        if len(times.shape) > 1:
            simpleint = False
            out = np.empty((len(irradiance), len(output_time)))
            for i in range(len(output_time)):
                if output_time[i] >= np.max(times[:, i]):
                    out[:, i] = irradiance[:, times[:, i] == np.max(times[:, i]), i][
                        :, 0
                    ]
                elif output_time[i] <= np.min(times[:, i]):
                    out[:, i] = irradiance[:, times[:, i] == np.min(times[:, i]), i][
                        :, 0
                    ]
                else:
                    irradiance_intfunc = scipy.interpolate.interp1d(
                        times[:, i], irradiance[:, :, i]
                    )
                    out[:, i] = irradiance_intfunc(output_time[i])

        elif hasattr(output_time, "__len__"):
            if len(output_time) > 1:
                simpleint = False
                out = np.empty((len(irradiance), len(output_time)))
                for i in range(len(output_time)):
                    if output_time[i] >= np.max(times):
                        out[:, i] = np.mean(
                            irradiance[:, times == np.max(times)], axis=1
                        ).squeeze()
                    elif output_time[i] <= np.min(times):
                        out[:, i] = np.mean(
                            irradiance[:, times == np.min(times)], axis=1
                        ).squeeze()
                    else:
                        irradiance_intfunc = scipy.interpolate.interp1d(
                            times, irradiance
                        )
                        out[:, i] = irradiance_intfunc(output_time[i])

        if simpleint:
            if output_time >= max(times):
                out = irradiance[:, times == max(times)]
            elif output_time <= min(times):
                out = irradiance[:, times == min(times)]
            else:
                irradiance_intfunc = scipy.interpolate.interp1d(times, irradiance)
                out = irradiance_intfunc(output_time)
        return out * np.cos(np.pi / 180.0 * output_sza)

    @staticmethod
    def get_name():
        return "InterpolationTimeLinearCoscorrected"

    def get_argument_names(self):
        return ["output_time", "input_time", "irradiance", "output_sza", "input_sza"]


class WaterNetworkInterpolationSkyRadianceLinearCoscorrected(MeasurementFunction):
    def meas_function(self, output_time, times, radiance, sza, sza_out):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """
        radiance = radiance / np.cos(np.pi / 180.0 * sza)

        skyradiance_intfunc = scipy.interpolate.interp1d(times, radiance)

        return skyradiance_intfunc(output_time) * np.cos(np.pi / 180.0 * sza_out)

    @staticmethod
    def get_name():
        return "WaterNetworkInterpolationSkyRadianceLinearCoscorrected"

    def get_argument_names(self):
        return ["output_time", "input_time", "radiance"]
