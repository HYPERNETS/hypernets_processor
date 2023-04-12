from punpy import MeasurementFunction
import numpy as np


class StandardMeasurementFunction(MeasurementFunction):
    def meas_function(self, digital_number, gains, dark_signal, non_linear, int_time):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """
        DN = digital_number - dark_signal
        DN[DN == 0] = 1

        corrected_DN = self.correct_nonlin(DN, non_linear)

        if gains.ndim == 1:
            return gains[:, None] * corrected_DN / int_time * 1000
        else:
            return gains * corrected_DN / int_time * 1000

    def correct_nonlin(self, DN, non_linear):
        corrected_DN = np.zeros_like(DN)
        if non_linear.ndim > 1:
            for i in range(len(non_linear[0])):
                corrected_DN[..., i] = self.correct_nonlin(DN[..., i], non_linear[:, i])

        else:
            non_lin_func = np.poly1d(np.flip(non_linear))
            corrected_DN = DN / non_lin_func(DN)

            # print(np.mean((corrected_DN)/DN),non_linear,non_linear.dtype)
        return corrected_DN

    @staticmethod
    def get_name():
        return "StandardMeasurementFunction"

    def get_argument_names(self):
        return [
            "digital_number",
            "gains",
            "dark_signal",
            "non_linearity_coefficients",
            "integration_time",
        ]
