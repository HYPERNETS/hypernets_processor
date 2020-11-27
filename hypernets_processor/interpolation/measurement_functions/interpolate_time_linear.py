

import scipy.interpolate
import numpy as np

class InterpolationTimeLinear:
    def function(self,output_time,times,variables):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        if hasattr(output_time,'__len__'):
            out = np.empty((len(variables),len(output_time)))
            for i in range(len(output_time)):
                if output_time[i] > max(times):
                    out[:,i] = variables[:,times == max(times)][:,0]
                elif output_time[i] < min(times):
                    out[:,i] = variables[:,times == min(times)][:,0]
                else:
                    irradiance_intfunc = scipy.interpolate.interp1d(times,
                                                                    variables)
                    out[:,i] = irradiance_intfunc(output_time[i])
        else:
            if output_time > max(times):
                out= variables[:,times == max(times)]
            elif output_time < min(times):
                out=  variables[:,times == min(times)]
            else:
                irradiance_intfunc = scipy.interpolate.interp1d(times,variables)
                out = irradiance_intfunc(output_time)
        return out

    @staticmethod
    def get_name():
        return "InterpolationTimeLinear"

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

