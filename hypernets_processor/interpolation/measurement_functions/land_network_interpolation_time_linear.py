

import scipy.interpolate
import numpy as np

class LandNetworkInterpolationTimeLinear:
    def function(self,output_time,times_irr,irradiances):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        if hasattr(output_time,'__len__'):
            out=np.empty((len(irradiances),len(output_time)))
            for i in range(len(output_time)):
                if output_time[i] > max(times_irr):
                    out[:,i]=irradiances[:,times_irr == max(times_irr)][:,0]
                elif output_time[i] < min(times_irr):
                    out[:,i]= irradiances[:,times_irr == min(times_irr)][:,0]
                else:
                    irradiance_intfunc = scipy.interpolate.interp1d(times_irr,
                                                                    irradiances)
                    out[:,i]= irradiance_intfunc(output_time[i])

        else:
            if output_time > max(times_irr):
                out =  irradiances[:,times_irr == max(times_irr)][:,0]
            elif output_time<min(times_irr):
                out =  irradiances[:,times_irr==min(times_irr)][:,0]
            else:
                irradiance_intfunc=scipy.interpolate.interp1d(times_irr,irradiances)
                out =  irradiance_intfunc(output_time)
        return out


    @staticmethod
    def get_name():
        return "LandNetworkInterpolationTimeLinear"

    def get_argument_names(self):
        return ["output_time","times","irradiances"]

