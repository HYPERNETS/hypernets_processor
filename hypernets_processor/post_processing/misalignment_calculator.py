import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import xarray as xr
from scipy.stats import chisquare
from scipy.stats import binned_statistic
import datetime
from curepy import MCMCRetrieval, plot_trace, plot_corner
import os
import matplotlib
matplotlib.use('Qt5Agg')

def ratio_calculator(vza, vaa, sza, saa, direct_to_diffuse):
    if vaa < 0:
        vza = -vza
        vaa += 180

    if sza.shape == ():
        if saa < 0:
            sza = -sza
            saa += 180
    else:
        sza[saa < 0] = -sza[saa < 0]
        saa[saa < 0] += 180

    sza = np.radians(sza)
    saa = np.radians(saa)
    vza = np.radians(vza)
    vaa = np.radians(vaa)
    #new_sza = np.cos(sza + vza*np.cos((saa - vaa + 360) % 360))
    new_sza = np.arccos(np.cos(sza) * np.cos(vza) + np.sin(sza) * np.sin(vza) * np.cos((saa - vaa)))
    new_direct_to_diffuse=direct_to_diffuse*np.cos(new_sza)/np.cos(sza)
    return (new_direct_to_diffuse+1) / (direct_to_diffuse+1)

class MisalignmentModel:

    def __init__(self,
                 data_path,
                 sza_data,
                 saa_data,
                 ratio_rand_unc,
                 ratio_syst_unc):

        data = pd.read_csv(data_path, delimiter=',')
        data.drop('Unnamed: 0', axis='columns')

        self.wavelengths = []
        ratio_dict = {}
        dir_diff_dict = {}

        for key in data.keys():
            if 'model' in key:
                wv = ''.join(filter(str.isdigit, key))
                idx = np.argwhere(data.keys() == key)[0]
                model_key = data.keys()[idx]
                obs_key = data.keys()[idx + 1]
                dir_diff_ratio_key = data.keys()[idx + 2]
                dir_diff_dict[wv] = data[dir_diff_ratio_key].values.reshape(-1)
                ratio = data[model_key].values / data[obs_key].values
                ratio_dict[wv] = ratio.reshape(-1)
                self.wavelengths.append(wv)

        self.dataset = xr.Dataset(data_vars=dict(
            sza=(['date'], sza_data),
            saa=(['date'], saa_data),
            dir_diff_ratio=(['wv', 'date'], list(dir_diff_dict.values())),
            ratio=(['wv', 'date'], list(ratio_dict.values()))),

            coords=dict(
                date=('date', [datetime.datetime.strptime(str(x), '%Y%m%d') for x in data['Date']]),
                wv=('wv', list(ratio_dict.keys()))
            ))





