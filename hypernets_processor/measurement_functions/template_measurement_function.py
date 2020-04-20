



class TemplateMeasurementFunction:


    def function(self,counts,gains,dark_signal,temp):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        return gains*(counts-dark_signal)+temp**0.3

    @staticmethod
    def get_name():
        return "TemplateMeasurementFunction"

    def get_argument_names(self):
        return ["counts","gains","dark signal","temp"]
