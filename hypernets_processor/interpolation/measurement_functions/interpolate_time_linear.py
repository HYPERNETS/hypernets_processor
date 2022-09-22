
from punpy import MeasurementFunction

import scipy.interpolate
import numpy as np

class InterpolationTimeLinear(MeasurementFunction):
    def meas_function(self,output_time,times,variables):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        # print(output_time.shape,times.shape,variables.shape)
        simpleint=True
        if len(times.shape)>1:
            simpleint=False
            out = np.empty((len(variables),len(output_time)))
            for i in range(len(output_time)):
                if output_time[i] >= np.max(times[:,i]):
                    out[:,i] = variables[:,times[:,i] == np.max(times[:,i]),
                               i][:,0]
                elif output_time[i] <= np.min(times[:,i]):
                    out[:,i] = variables[:,times[:,i] == np.min(times[:,i]),
                               i][:,0]
                else:
                    irradiance_intfunc = scipy.interpolate.interp1d(
                        times[:,i],variables[:,:,i])
                    out[:,i] = irradiance_intfunc(output_time[i])

        elif hasattr(output_time,'__len__'):
            if len(output_time)>1:
                simpleint=False
                out = np.empty((len(variables),len(output_time)))
                for i in range(len(output_time)):
                    if output_time[i] >= np.max(times):
                        out[:,i] = variables[:,times == np.max(times)][:,0]
                    elif output_time[i] <= np.min(times):
                        out[:,i] = variables[:,times == np.min(times)][:,0]
                    else:
                        irradiance_intfunc = scipy.interpolate.interp1d(times,
                                                                        variables)
                        out[:,i] = irradiance_intfunc(output_time[i])

        if simpleint:
            if output_time >= max(times):
                out= variables[:,times == max(times)]
            elif output_time <= min(times):
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
#     def meas_function(self,output_time,times,variables):
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

