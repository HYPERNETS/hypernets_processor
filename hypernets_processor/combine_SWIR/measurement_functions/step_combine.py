
import numpy as np


class StepCombine:

    def function(self,wavs_vis,rad_VIS,wavs_swir,rad_SWIR,wav_step):
        '''
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        '''
        if len(wavs_vis.shape)>1:
            rad=np.concatenate((rad_VIS[np.where(wavs_vis[:,0]<=wav_step[0])[0],:],rad_SWIR[np.where(wavs_swir[:,0]>wav_step[0])[0],:]),axis=0)
        else:
            rad=np.concatenate((rad_VIS[np.where(wavs_vis<=wav_step)],rad_SWIR[np.where(wavs_swir>wav_step)]),axis=0)
        return rad

    @staticmethod
    def get_name():
        return "StepCombine"

    def get_argument_names(self):
        return ["wavelength_VIS","radiance_VIS","wavelength_SWIR","radiance_SWIR","wavelength_step"]

