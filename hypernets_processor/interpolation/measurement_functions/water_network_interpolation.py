

import scipy.interpolate

class WaterNetworkInterpolationLinear:
    def function(self,output_time,times,variables):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        irradiance_intfunc=scipy.interpolate.interp1d(times,variables, fill_value="extrapolate")

        return irradiance_intfunc(output_time)

    @staticmethod
    def get_name():
        return "WaterNetworkInterpolationLinear"

    def get_argument_names(self):
        return ["output_time","times","irradiance", "downwelling_radiance"]

# class WaterNetworkInterpolationSkyRadianceLinear:
#     def function(self,output_time,times,variables):
#         '''
#         This function implements the measurement function.
#         Each of the arguments can be either a scalar or a vector (1D-array).
#         '''
#         skyradiance_intfunc=scipy.interpolate.interp1d(times,variables)
#
#         return skyradiance_intfunc(output_time)
#
#     @staticmethod
#     def get_name():
#         return "WaterNetworkInterpolationSkyRadianceLinear"
#
#     def get_argument_names(self):
#         return ["output_time","times","downwelling_radiance"]

