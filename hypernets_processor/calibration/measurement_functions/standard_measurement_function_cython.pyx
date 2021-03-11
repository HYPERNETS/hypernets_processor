import numpy as np
cimport numpy as np
DTYPE = np.float
ctypedef np.float_t DTYPE_t



cdef class StandardMeasurementFunctionCython:
    def function(self,np.ndarray[float, ndim=2] digital_number, np.ndarray[float, ndim=2] gains, np.ndarray[float, ndim=2] dark_signal, np.ndarray[float] non_linear,np.ndarray[float,ndim=2] int_time):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        return digital_number

    @staticmethod
    def get_name():
        return "StandardMeasurementFunctionCython"

    def get_argument_names(self):
        return ["digital_number","gains","dark_signal","non_linearity_coefficients","integration_time"]

