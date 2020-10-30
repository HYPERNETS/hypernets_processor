import numpy as np

class WaterNetworkProtocol:

    def function(self,upwelling_radiance,downwelling_radiance,irradiance,rhof,epsilon):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        water_leaving_radiance = [(upwelling_radiance[w] - (rhof * downwelling_radiance[w])) for w in range(len(downwelling_radiance))]
        reflectance_nosc = [np.pi * (upwelling_radiance[w] - (rhof * downwelling_radiance[w])) / irradiance[w] for w in range(len(downwelling_radiance))]

        reflectance = [r - epsilon for r in reflectance_nosc]

        return water_leaving_radiance, reflectance_nosc, reflectance

    @staticmethod
    def get_name():
        return "WaterNetworkProtocol"

    def get_argument_names(self):
        return ["upwelling_radiance","downwelling_radiance","irradiance","rhof", "epsilon"]

