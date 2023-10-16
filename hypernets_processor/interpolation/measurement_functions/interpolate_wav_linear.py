from punpy import MeasurementFunction

import scipy.interpolate
import numpy as np


class InterpolationWavLinear(MeasurementFunction):
    def meas_function(self, rad_wavs, irr_wavs, irr):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """
        if len(irr_wavs.shape) > 1:
            irradiance_intfunc = scipy.interpolate.interp1d(
                irr_wavs[:, 0], irr, axis=0, fill_value="extrapolate"
            )
            out = irradiance_intfunc(rad_wavs[:, 0])
        else:
            irradiance_intfunc = scipy.interpolate.interp1d(
                irr_wavs, irr, axis=0, fill_value="extrapolate"
            )
            out = irradiance_intfunc(rad_wavs)
        return out

    @staticmethod
    def get_name():
        return "InterpolationWavLinear"

    def get_argument_names(self):
        return ["radiance_wavelength", "wavelength", "irradiance"]
