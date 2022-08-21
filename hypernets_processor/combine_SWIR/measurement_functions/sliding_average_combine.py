from punpy import MeasurementFunction

class SlidingAverageCombine(MeasurementFunction):

    def meas_function(self,wav_VIS,rad_VIS,wav_SWIR,rad_SWIR):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        return

    @staticmethod
    def get_name():
        return "SlidingAverageCombine"

    def get_argument_names(self):
        return ["wavelength_VIS","radiance_VIS","wavelength_SWIR","radiance_SWIR"]

