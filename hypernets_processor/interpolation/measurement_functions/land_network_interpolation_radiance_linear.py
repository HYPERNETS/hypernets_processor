

import scipy.interpolate

class LandNetworkInterpolationRadianceLinear:
    def function(self,output_time,times,radiances):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        radiance_intfunc=scipy.interpolate.interp1d(times,radiances)

        return radiance_intfunc(output_time)

    @staticmethod
    def get_name():
        return "LandNetworkInterpolationRadianceLinear"

    def get_argument_names(self):
        return ["output_time","times","radiances"]

