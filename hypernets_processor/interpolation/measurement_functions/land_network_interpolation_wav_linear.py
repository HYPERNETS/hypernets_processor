

import scipy.interpolate
import numpy as np

class LandNetworkInterpolationWavLinear:
    def function(self,rad_wavs,irr_wavs,irr):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        irradiance_intfunc = scipy.interpolate.interp1d(irr_wavs,irr,axis=0,
                                                        fill_value="extrapolate")
        out = irradiance_intfunc(rad_wavs)
        return out


    @staticmethod
    def get_name():
        return "LandNetworkInterpolationWavLinear"

    def get_argument_names(self):
        return ["radiance_wavelengths","irradiance_wavelengths","irradiances"]

