import numpy as np
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.rhymer.rhymer.processing.rhymer_processing import (
    RhymerProcessing,
)
from hypernets_processor.rhymer.rhymer.shared.rhymer_shared import RhymerShared
from punpy import MeasurementFunction


class WaterNetworkProtocol(MeasurementFunction):
    def setup(self, context):
        self.context = context
        self.rh = RhymerHypstar(context)
        self.rhp = RhymerProcessing(context)
        self.rhs = RhymerShared(context)

    def meas_function(
        self, water_leaving_radiance, irradiance, wavelength
    ):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """

        reflectance_nosc = np.pi * water_leaving_radiance/ irradiance

        # NIR SIMIL CORRECTION
        # retrieve variables for NIR SIMIL correction
        w1 = 720#self.context.get_config_value("similarity_w1")
        w2 = 780#self.context.get_config_value("similarity_w2")
        alpha = 2.35#self.context.get_config_value("similarity_alpha")

        iref1, wref1 = self.rhs.closest_idx(wavelength, w1)
        iref2, wref2 = self.rhs.closest_idx(wavelength, w2)

        ## get pixel index for similarity
        if alpha is None:
            ssd = self.rhp.similarity_read()
            id1, w1 = self.rhs.closest_idx(ssd["wave"], w1 / 1000.0)
            id2, w2 = self.rhs.closest_idx(ssd["wave"], w2 / 1000.0)
            alpha = ssd["ave"][id1] / ssd["ave"][id2]

        epsilon = (alpha * reflectance_nosc[iref2] - reflectance_nosc[iref1]) / (
            alpha - 1.0
        )
        reflectance = np.array([r - epsilon for r in reflectance_nosc])
        return reflectance_nosc, reflectance, epsilon

    @staticmethod
    def get_name():
        return "WaterNetworkProtocol"

    def get_argument_names(self):
        return [
            "water_leaving_radiance",
            "irradiance",
            "wavelength",
        ]
