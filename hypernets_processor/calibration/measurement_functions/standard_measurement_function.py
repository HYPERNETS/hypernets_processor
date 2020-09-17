



class StandardMeasurementFunction:

    def function(self,digital_number,gains,dark_signal,temp):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        return gains*(digital_number-dark_signal)*temp**0

    @staticmethod
    def get_name():
        return "StandardMeasurementFunction"

    def get_argument_names(self):
        return ["digital_number","gains","dark_signal","temp"]

