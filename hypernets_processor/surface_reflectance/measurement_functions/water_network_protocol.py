



class WaterNetworkProtocol:

    def function(self,radiance_up,radiance_down,irradiance,fresnel_reflectance):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''

        return 3.14159265359*((radiance_up-fresnel_reflectance*radiance_down)/irradiance)

    @staticmethod
    def get_name():
        return "WaterNetworkProtocol"

    def get_argument_names(self):
        return ["lu","ld","Ed","rhof"]

