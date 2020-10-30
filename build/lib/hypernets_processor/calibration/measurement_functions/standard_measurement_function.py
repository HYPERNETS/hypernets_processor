



class StandardMeasurementFunction:

    def function(self,digital_number,gains,dark_signal,non_linear,int_time):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        DN=digital_number-dark_signal
        corrected_DN = DN /(non_linear[0]+non_linear[1]*DN+
                                       non_linear[2]*DN**2+
                                       non_linear[3]*DN**3+
                                       non_linear[4]*DN**4+
                                       non_linear[5]*DN**5+
                                       non_linear[6]*DN**6+
                                       non_linear[7]*DN**7)

        # print(DN[500,5],corrected_DN[500,5],(gains*corrected_DN/int_time*1000)[500,5])

        return gains*corrected_DN/int_time*1000

    @staticmethod
    def get_name():
        return "StandardMeasurementFunction"

    def get_argument_names(self):
        return ["digital_number","gains","dark_signal","non_linearity_coefficients","integration_time"]

