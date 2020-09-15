

from hypernets_processor.rhymer.rhymer import RhymerShared
import numpy as np

class WaterNetworkProtocol:

    def function(self,upwelling_radiance,downwelling_radiance,irradiance,rhof,epsilon):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        lw_all = [(upwelling_radiance[w] - (rhof * downwelling_radiance[w])) for w in range(len(downwelling_radiance))]
        rhow_nosc_all = [np.pi * (upwelling_radiance[w] - (rhof * downwelling_radiance[w])) / irradiance[w] for w in range(len(downwelling_radiance))]

        rhow_all = [r - epsilon for r in rhow_nosc_all]

        return lw_all, rhow_nosc_all, rhow_all

    @staticmethod
    def get_name():
        return "WaterNetworkProtocol"

    def get_argument_names(self):
        return ["upwelling_radiance","downwelling_radiance","irradiance","rhof", "epsilon"]

