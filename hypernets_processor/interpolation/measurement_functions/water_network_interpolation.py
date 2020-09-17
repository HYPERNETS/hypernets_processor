

import scipy.interpolate

class WaterNetworkInterpolationIrradianceLinear:
    def function(self,output_time,times,irradiances):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        irradiance_intfunc=scipy.interpolate.interp1d(times,radiances)

        return irradiance_intfunc(output_time)

    @staticmethod
    def get_name():
        return "WaterNetworkInterpolationIrradianceLinear"

    def get_argument_names(self):
        return ["output_time","times","irradiances"]

