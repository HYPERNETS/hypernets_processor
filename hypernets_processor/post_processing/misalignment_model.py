import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.random import normal
from scipy.optimize import curve_fit
import xarray as xr
from scipy.stats import chisquare
from scipy.stats import binned_statistic
import datetime
from curepy import MCMCRetrieval, plot_trace, plot_corner
import os
import matplotlib
matplotlib.use('Qt5Agg')

results_path = r"T:\ECO\EOServer\joe\hypernets_plots\misalignment"
#read in data
data = pd.read_csv(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\irradiance_GHNA_v3_analysis.csv', delimiter = ',')
data.drop('Unnamed: 0', axis = 'columns')

#cloud check and flag removal
data = data[data['model_550nm']*0.9 < data['obs_550nm']]
data = data[data['model_550nm']*1.1 > data['obs_550nm']]
data = data[data['Flag'] == 0]

#format data
sza_measured = data['SZA'].values
saa_measured = data['SAA'].values
wavelengths = []

for i in range(len(saa_measured)):
    if saa_measured[i] > 180:
        saa_measured[i] = saa_measured[i] - 360



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
        ratio = data[model_key].values/data[obs_key].values
        ratio_dict[wv] = ratio.reshape(-1)
        wavelengths.append(wv)

data = xr.Dataset(data_vars = dict(
    sza = (['date'], sza_measured),
    saa = (['date'], saa_measured),
    dir_diff_ratio = (['wv','date'], list(dir_diff_dict.values())),
    ratio = (['wv', 'date'], list(ratio_dict.values())),
    time = (['date'], [str(x).zfill(4) for x in data['Time']])),

    coords = dict(
        date = ('date', [datetime.datetime.strptime(str(x), '%Y%m%d') for x in data['Date']]),
        wv = ('wv', list(ratio_dict.keys()))
    ))

data_before_may24 = data.sel(date = slice('2023-10-01', '2024-05-23'))
data_after_may24 = data.sel(date = slice('2024-05-24', '2025-01-01'))

def ratio_calculator(vza, vaa, offset, sza, saa, direct_to_diffuse=1000):
    if vza < 0:
        vza = -vza
        vaa += -180

    sza = np.radians(sza)
    saa = np.radians(saa)
    vza = np.radians(vza)
    vaa = np.radians(vaa)
    #new_sza = np.cos(sza + vza*np.cos((saa - vaa + 360) % 360))
    new_sza = np.arccos(np.cos(sza) * np.cos(vza) + np.sin(sza) * np.sin(vza) * np.cos((saa - vaa)))
    new_direct_to_diffuse=direct_to_diffuse*np.cos(new_sza)/np.cos(sza)
    return (new_direct_to_diffuse+1) / (direct_to_diffuse+1) + offset

def ratio_calculator_10offsets(vza, vaa, offset, offset2, offset3, offset4, offset5, offset6, offset7, offset8, offset9, offset10, sza, saa, direct_to_diffuse=1000):
    if vza < 0:
        vza = -vza
        vaa += -180

    sza = np.radians(sza)
    saa = np.radians(saa)
    vza = np.radians(vza)
    vaa = np.radians(vaa)
    #new_sza = np.cos(sza + vza*np.cos((saa - vaa + 360) % 360))
    new_sza = np.arccos(np.cos(sza) * np.cos(vza) + np.sin(sza) * np.sin(vza) * np.cos((saa - vaa)))
    new_direct_to_diffuse=direct_to_diffuse*np.cos(new_sza)/np.cos(sza)
    offsets=np.array([offset, offset2, offset3, offset4, offset5, offset6, offset7, offset8, offset9, offset10])
    return (new_direct_to_diffuse+1) / (direct_to_diffuse+1) + offsets[:,None]

def ratio_uncertainty_calculator(vza, vaa, sza, saa, u_vza, u_vaa):
    if vza < 0:
        vza = -vza
        vaa += -180

    sza = np.radians(sza)
    saa = np.radians(saa)
    vza = np.radians(vza)
    vaa = np.radians(vaa)

    unc = np.sqrt((np.sin(sza) * np.sin(vza) * np.sin(saa - vaa) * u_vaa)**2 +
                  ((-np.cos(sza) * np.sin(sza) + np.sin(sza) * np.cos(vza) * np.cos(saa - vaa)) * u_vza)**2)
    new_sza = np.cos(sza) * np.cos(vza) + np.sin(sza) * np.sin(vza) * np.cos((saa - vaa))
    return unc/new_sza * 100

def convergence_test(d, window_length, threshold):
    series = pd.Series(d)
    std = list(series.rolling(window_length).std())[::-1]
    turning_point = [i for i, v in enumerate(std) if v > threshold][0]
    return turning_point

def quad_plane(xy, a, b, c, d, e, f):
    x, y = xy
    return a + b * x + c * y + d * x ** 2 + e * y ** 2 + f * x * y

def plane_fit(input_sza, input_saa, ratio):
    x = input_sza
    y = input_saa
    z = ratio

    popt, pcov = curve_fit(quad_plane, (x, y), z, nan_policy = 'omit')

    return popt, pcov

def plane_plotter(ax, input_sza, input_saa, ratio, color, dot_color):
    coeff, cov = plane_fit(input_sza, input_saa, ratio)
    coeff = [round(x,9) for x in coeff]
    sza, saa = np.meshgrid(np.linspace(np.min(input_sza) , np.max(input_sza) , 1000),
                           np.linspace(np.min(input_saa), np.max(input_saa) , 1000))
    plane = quad_plane((sza,saa), *coeff)

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection = '3d')
    ax = ax
    ax.scatter(input_sza, input_saa, ratio, marker = 'x', alpha = 0.7, s = 2, color = dot_color)
    ax.plot_surface(sza, saa, plane, alpha = 0.5, color = color)
    ax.set_xlabel('SZA')
    ax.set_ylabel('SAA')
    ax.set_zlabel('Model to Measurement Ratio')

def comparison_plotter(sza, saa, vza, vaa, ratio):


    sza_range = np.linspace(np.min(sza), np.max(sza), 100)
    saa_range = np.linspace(np.min(saa), np.max(saa), 100)

    sza_mesh, saa_mesh = np.meshgrid(sza_range, saa_range)

    vzas = vza * np.ones(sza_mesh.shape)
    vaas = vaa * np.ones(saa_mesh.shape)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plane_plotter(ax, sza_mesh, saa_mesh, ratio_calculator(vzas, vaas, sza_mesh, saa_mesh), 'green', 'black')
    plane_plotter(ax, sza, saa, ratio, 'red', 'blue')
    plt.show()

def chi_square_minimiser(sza, saa, measured_ratio):
    chi = 10000000
    vza = 999
    vaa = 999
    max_sza = max(sza)
    min_sza = min(sza)
    max_saa = max(saa)
    min_saa = min(saa)

    sza_range = np.linspace(min_sza, max_sza, 10)
    saa_range = np.linspace(min_saa, max_saa, 10)

    sza_mesh, saa_mesh = np.meshgrid(sza_range, saa_range)
    coeff, cov = plane_fit(sza, saa, measured_ratio)
    coeff = [round(x,9) for x in coeff]

    measured_fit = quad_plane((sza_mesh,saa_mesh), *coeff)
    for i in np.arange(0, 5, 0.1):
        for j in range(-180, 180):
            vzas = i * np.ones(sza.shape)
            vaas = j * np.ones(saa.shape)
            calculated_fit = ratio_calculator(vzas, vaas, sza, saa)

            # new_chi = chisquare(measured_fit, (np.sum(measured_fit)/np.sum(calculated_fit))*calculated_fit).statistic
            new_chi = np.sum((measured_ratio - calculated_fit) ** 2 / calculated_fit)
            if new_chi < chi:
                chi = new_chi
                vza = i
                vaa = j

    best_fit = ratio_calculator(vza * np.ones(sza_mesh.shape), vaa * np.ones(saa_mesh.shape), sza_mesh, saa_mesh)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    ax.scatter(sza, saa, measured_ratio, marker='x', alpha=0.7, s=2)
    ax.plot_surface(sza_mesh, saa_mesh, best_fit, alpha=0.5, color = 'green')
    ax.plot_surface(sza_mesh, saa_mesh, measured_fit, alpha=0.5, color = 'red')
    plt.show()

    print(chi, vza, vaa, np.size(sza_mesh) - 6)
    return chi, vza, vaa, np.size(sza_mesh) - 6

def chi_square_minimiser_mesh(sza, saa, measured_ratio):
    chi = 10000000
    vza = 999
    vaa = 999
    max_sza = max(sza)
    min_sza = min(sza)
    max_saa = max(saa)
    min_saa = min(saa)

    sza_range = np.linspace(min_sza, max_sza, 10)
    saa_range = np.linspace(min_saa, max_saa, 10)

    sza_mesh, saa_mesh = np.meshgrid(sza_range, saa_range)
    coeff, cov = plane_fit(sza, saa, measured_ratio)
    coeff = [round(x,9) for x in coeff]

    measured_fit = quad_plane((sza_mesh,saa_mesh), *coeff)
    best_fit = np.ones(sza_mesh.shape)
    for i in np.arange(0,10,0.1):
        for j in range(0,360):
            vzas = i * np.ones(sza_mesh.shape)
            vaas = j * np.ones(saa_mesh.shape)
            calculated_fit = ratio_calculator(vzas, vaas, sza_mesh, saa_mesh)

            #new_chi = chisquare(measured_fit, (np.sum(measured_fit)/np.sum(calculated_fit))*calculated_fit).statistic
            new_chi = np.sum((measured_fit - calculated_fit)**2 / calculated_fit)
            if new_chi < chi:
                chi = new_chi
                vza = i
                vaa = j
                best_fit = calculated_fit

    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    ax.scatter(sza, saa, measured_ratio, marker='x', alpha=0.7, s=2)
    ax.plot_surface(sza_mesh, saa_mesh, best_fit, alpha=0.5, color = 'green')
    ax.plot_surface(sza_mesh, saa_mesh, measured_fit, alpha=0.5, color = 'red')
    plt.show()
    plt.close()

    print(chi, vza, vaa, np.size(sza_mesh) - 6)
    return chi, vza, vaa, np.size(sza_mesh) - 6



def chi_square_minimiser_MCMC(sza, saa, dir_diff_ratio, measured_ratio, plot_name = ''):

    mcmc = MCMCRetrieval(
        ratio_calculator,
        measured_ratio,
        rand_uncertainty=0.05,
        syst_uncertainty=0.03,
        initial_guess=[2,-40,0.01],
        downlims=[-90,-180,-1],
        uplims=[90,180,1],
        n_input=3,
        b=[sza, saa, dir_diff_ratio],
        u_b=[0, 0, 0],
        b_iter=1,
        circular = True
    )
    mean, unc, corr, samples = mcmc.run_retrieval(
        100, 1000, 100, return_corr=True, return_samples=True
    )
    chisq = mcmc.find_chisum(mean)
    print(len(sza), chisq)
    print(mean, unc)

    plot_corner(
         samples,
         os.path.join(results_path, "plot_corner_%s.png" % plot_name),
         labels=['vza','vaa', 'offset'],
     )
    plot_trace(
         samples,
         labels=['vza', 'vaa', 'offset'],
         path=results_path,
        tag = plot_name
     )

    return mean, unc


def chi_square_minimiser_MCMC_10offsets(sza, saa, dir_diff_ratio, measured_ratio, plot_name = ''):
    mcmc = MCMCRetrieval(
        ratio_calculator_10offsets,
        measured_ratio,
        rand_uncertainty=0.05,
        syst_uncertainty=0.03,
        initial_guess=[2,20,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01],
        downlims=[-90,-180,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        uplims=[90,180,1,1,1,1,1,1,1,1,1,1],
        n_input=12,
        b=[sza, saa, dir_diff_ratio],
        u_b=[0, 0, 0],
        b_iter=1,
        circular = True
    )
    mean, unc, corr, samples = mcmc.run_retrieval(
        1000, 1000, 100, return_corr=True, return_samples=True
    )
    chisq = mcmc.find_chisum(mean)
    print('CHI',len(sza) - 12, chisq, chisq/(len(sza) - 12))


    plot_corner(
         samples,
         os.path.join(results_path, "plot_corner_%s.png" % plot_name),
         labels=['vza','vaa', 'offset', 'offset2', 'offset3', 'offset4', 'offset5', 'offset6', 'offset7', 'offset8', 'offset9', 'offset10'],
     )
#    plot_trace(
 #        samples,
  #       labels=['vza','vaa', 'offset', 'offset2', 'offset3', 'offset4', 'offset5', 'offset6', 'offset7', 'offset8', 'offset9', 'offset10'],
   #      path=results_path,
    #    tag = plot_name
     #)

    return mean, unc

def plot_misalign_change(dataset):
    ma_dict = {'vza': {}, 'unc_vza': {}, 'num': {}, 'sza': {}, 'saa': {}}
    earliest = min(dataset.date.values)
    recent = max(dataset.date.values)
    earliest_year = np.datetime64(earliest, 'Y').astype(int) + 1970
    recent_year = np.datetime64(recent, 'Y').astype(int) + 1970
    for y in range(earliest_year, recent_year + 1):
        for m in range(0,12):
            m = str(m).zfill(2)
            try:
                ds_month = dataset.loc[dict(date = f'{y}-{m}')]
                mean, unc = chi_square_minimiser_MCMC_10offsets(ds_month.sza.values, ds_month.saa.values,
                                                      ds_month.dir_diff_ratio.values,
                                                      np.array(list(ds_month.ratio.values)))
                #comparison_plotter(ds_month.sza.values, ds_month.saa.values, vza, vaa, list(ds_month.ratio.values))
                ma_dict['vza'][f'{y}-{m}'] = mean[0]
                ma_dict['unc_vza'][f'{y}-{m}'] = unc[0]
                ma_dict['num'][f'{y}-{m}'] = len(ds_month.sza.values)
                ma_dict['sza'][f'{y}-{m}'] = ds_month.sza.values
                ma_dict['saa'][f'{y}-{m}'] = ds_month.saa.values

            except:
                ma_dict[f'{y}-{m}'] = np.nan

    fig, axs = plt.subplots(4,1)
    axs[0].errorbar(ma_dict['vza'].keys(), list(ma_dict['vza'].values()), yerr = list(ma_dict['unc_vza'].values()),
                 marker = '', linestyle = '', capsize = 5)
    axs[1].bar(ma_dict['vza'].keys(), list(ma_dict['num'].values()))
    axs[2].violinplot(ma_dict['sza'].values())
    axs[3].violinplot(ma_dict['saa'].values())

    axs[0].set_ylabel('VZA')
    axs[1].set_ylabel('Number of Measurements')
    axs[2].set_ylabel('SZA')
    axs[3].set_ylabel('SAA')
    plt.show()

def plot_misalign_sza(dataset, wav, ret = False):
    ma_dict = {'vza': {}, 'unc_vza': {}, 'vaa': {}, 'ratio': {},'unc_ratio': {}, 'unc_vaa': {}, 'num': {}, 'sza': {}, 'saa': {}, 'obs_ratio': {}}
    #sza_bounds = [0,7.5,12.5,17.5,22.5,27.5,32.5,37.5,42.5,47.5,52.5,57.5,62.5,67.5]
    val, bins = pd.qcut(dataset.sza, 10, retbins = True)
    bins.round(1)
    bins[0] = 0
    sza_bounds = bins
    #sza_bounds = [0,20,40,60,80]
    ratio_0 = 999
    for i in range(len(sza_bounds) - 1):
        sza_min = sza_bounds[i]
        sza_max = sza_bounds[i+1]
        sza_center = np.mean([sza_min, sza_max]).round(1)

        ds = dataset.loc[dict(wv = wav)].set_coords('sza').where((dataset.sza < sza_max) & (dataset.sza > sza_min))
        ds = ds.dropna(dim = 'date')
        try:
            mean, unc = chi_square_minimiser_MCMC(ds.sza.values, ds.saa.values,
                                                  ds.dir_diff_ratio.values,
                                                  np.array(list(ds.ratio.values)), wav + f'_{sza_center}')

            mean = list(mean)
            unc = list(unc)
            if mean[0] < 0:
                mean[0] = -mean[0]
                mean[1] += -180

            ma_dict['vza'][f'{sza_center}'] = mean[0]
            ma_dict['unc_vza'][f'{sza_center}'] = unc[0]
            ma_dict['vaa'][f'{sza_center}'] = mean[1]
            ma_dict['unc_vaa'][f'{sza_center}'] = unc[1]
            ma_dict['num'][f'{sza_center}'] = len(ds.sza.values)
            ma_dict['sza'][f'{sza_center}'] = ds.sza.values
            ma_dict['saa'][f'{sza_center}'] = ds.saa.values

            ratio_grid = ratio_calculator(mean[0], mean[1], mean[2],
                                          sza_center, ds.saa.values,
                                          ds.dir_diff_ratio.values)
            ratio_unc = ratio_uncertainty_calculator(mean[0], mean[1],
                                                     sza_center, ds.saa.values,
                                                     unc[0], unc[1]) * ratio_grid/100
            if ratio_0 == 999:
                ratio_0 = np.mean(ratio_grid)

            ma_dict['ratio'][f'{sza_center}'] = np.mean(ratio_grid)#/ratio_0
            ma_dict['unc_ratio'][f'{sza_center}'] = np.sqrt((np.std(ratio_grid)**2 + np.sum(ratio_unc**2)/len(ratio_unc)**2))
            ma_dict['obs_ratio'][f'{sza_center}'] = np.mean(np.array(list(ds.ratio.values)))

        except:
            ma_dict[f'{sza_center}'] = np.nan

    fig, axs = plt.subplots(4,1, sharex = True)
    axs[0].errorbar(ma_dict['vza'].keys(), list(ma_dict['vza'].values()), yerr = list(ma_dict['unc_vza'].values()),
                 marker = '', linestyle = '', capsize = 5)
    axs[1].errorbar(ma_dict['vza'].keys(), list(ma_dict['vaa'].values()), yerr=list(ma_dict['unc_vaa'].values()),
                    marker='', linestyle='', capsize=5)
    axs[2].errorbar(ma_dict['vza'].keys(), list(ma_dict['ratio'].values()), yerr=list(ma_dict['unc_ratio'].values()),
                    marker='x', linestyle='', capsize=5)
    axs[2].scatter(ma_dict['vza'].keys(), list(ma_dict['obs_ratio'].values()),
                    marker='o')
    axs[2].hlines(y = 1, color = 'black', alpha = 0.5, xmin = 0, xmax = 15)
    axs[3].bar(ma_dict['vza'].keys(), list(ma_dict['num'].values()))

    axs[0].grid(color = 'black', alpha = 0.5, axis = 'y')
    axs[1].grid(color = 'black', alpha = 0.5, axis = 'y')

    axs[2].set_ylim(0.9,1.1)

    axs[0].set_ylabel('VZA')
    axs[1].set_ylabel('VAA')
    axs[2].set_ylabel('Ratio')
    axs[3].set_ylabel('Number of \nMeasurements')
    fig.suptitle(wav)
    fig.tight_layout()
    fig.savefig(os.path.join(results_path , f'sza_plot_{wav}_after.png'))

    if ret:
        return ma_dict

def plot_misalign_sza_all_wavs(dataset):
    ma_dict = {'vza': {}, 'unc_vza': {}, 'num': {}, 'sza': {}, 'saa': {}}
    #sza_bounds = [0,7.5,12.5,17.5,22.5,27.5,32.5,37.5,42.5,47.5,52.5,57.5,62.5,67.5]
    sza_bounds = [0,20,40,60,80]
    fig1, ax1 = plt.subplots(1, 1)
    fig2, ax2 = plt.subplots(4,1, sharey = True)
    for wav in dataset.wv.values:

        for i in range(len(sza_bounds) - 1):
            sza_min = sza_bounds[i]
            sza_max = sza_bounds[i+1]
            sza_center = np.mean([sza_min, sza_max])

            ds = dataset.loc[dict(wv = wav)].set_coords('sza').where((dataset.sza < sza_max) & (dataset.sza > sza_min))
            ds = ds.dropna(dim = 'date')
            try:
                mean, unc = chi_square_minimiser_MCMC(ds.sza.values, ds.saa.values,
                                                      ds.dir_diff_ratio.values,
                                                      np.array(list(ds.ratio.values)))

                ma_dict['vza'][f'{sza_center}'] = mean[0]
                ma_dict['unc_vza'][f'{sza_center}'] = unc[0]
                ma_dict['num'][f'{sza_center}'] = len(ds.sza.values)
                ma_dict['sza'][f'{sza_center}'] = ds.sza.values
                ma_dict['saa'][f'{sza_center}'] = ds.saa.values

            except:
                ma_dict[f'{sza_center}'] = np.nan

            ax2[i].errorbar(wav, mean[0], yerr = unc[0],
                     marker = '', linestyle = '', capsize = 5, label = wav)
            ax2[i].set_ylabel('VZA')
            ax2[i].set_title(f'{sza_center}')
            ax2[i].set_ylim(0,10)

        ax1.errorbar(ma_dict['vza'].keys(), list(ma_dict['vza'].values()), yerr = list(ma_dict['unc_vza'].values()),
                     marker = '', linestyle = '', capsize = 5, label = wav)

    ax1.set_ylabel('VZA')
    ax1.legend()

    fig2.tight_layout()
    plt.show()

def plot_misalign_saa(dataset, wav):
    ma_dict = {'vza': {}, 'unc_vza': {}, 'num': {}, 'sza': {}, 'saa': {}}
    saa_bounds = [-180, -160, -140, -120, -100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100, 120, 140, 160, 180]
    for i in range(len(saa_bounds) - 1):
        saa_min = saa_bounds[i]
        saa_max = saa_bounds[i+1]
        saa_center = np.mean([saa_min, saa_max])

        ds = dataset.loc[dict(wv = wav)].set_coords('saa').where((dataset.saa < saa_max) & (dataset.saa > saa_min))
        ds = ds.dropna(dim = 'date')
        try:
            mean, unc = chi_square_minimiser_MCMC(ds.sza.values, ds.saa.values,
                                                  ds.dir_diff_ratio.values,
                                                  np.array(list(ds.ratio.values)))

            ma_dict['vza'][f'{saa_center}'] = mean[0]
            ma_dict['unc_vza'][f'{saa_center}'] = unc[0]
            ma_dict['num'][f'{saa_center}'] = len(ds.sza.values)
            ma_dict['sza'][f'{saa_center}'] = ds.sza.values
            ma_dict['saa'][f'{saa_center}'] = ds.saa.values

        except:
            ma_dict[f'{saa_center}'] = np.nan

    for key in ma_dict['vza'].keys():
        if ma_dict['num'][key] < 100:
            del ma_dict['vza'][key]
            del ma_dict['unc_vza'][key]

    fig, axs = plt.subplots(2,1)
    axs[0].errorbar(ma_dict['vza'].keys(), list(ma_dict['vza'].values()), yerr = list(ma_dict['unc_vza'].values()),
                 marker = '', linestyle = '', capsize = 5)
    axs[1].bar(ma_dict['vza'].keys(), list(ma_dict['num'].values()))

    axs[0].set_ylabel('VZA')
    axs[1].set_ylabel('Number of Measurements')
    plt.show()

def normalise_ratios(dataset):
    val, bins = pd.qcut(dataset.sza, 15, retbins = True)
    bins.round(1)
    bins[0] = 0
    sza_bounds = bins
    sza_min = sza_bounds[0]
    sza_max = sza_bounds[1]
    sza_center = np.mean([sza_min, sza_max]).round(1)

    for wav in wavelengths:
        ds = dataset.loc[dict(wv = wav)].set_coords('sza').where((dataset.sza < sza_max) & (dataset.sza > sza_min))
        ds = ds.dropna(dim = 'date')
        mean, unc = chi_square_minimiser_MCMC(ds.sza.values, ds.saa.values,
                                              ds.dir_diff_ratio.values,
                                              np.array(list(ds.ratio.values)), wav + f'_{sza_center}')

        ratio_grid = ratio_calculator(mean[0], mean[1], mean[2],
                                      dataset.sza.values, dataset.saa.values,
                                      dataset.dir_diff_ratio.loc[dict(wv = wav)].values)

        dataset.ratio.loc[dict(wv = wav)] = dataset.ratio.loc[dict(wv = wav)].values/ratio_grid

    return dataset

def find_misalignment_angles(dataset, ratio_thresh):
    retrieval_dict = {'vza': {}, 'unc_vza': {}, 'vaa': {}, 'unc_vaa': {}}
    #dataset = normalise_ratios(dataset)

    for wv in wavelengths:
        ma_dict = plot_misalign_sza(dataset, wv, True)

        converged_vza = convergence_test(ma_dict['vza'].values(), 3, 1)
        converged_vaa = convergence_test(ma_dict['vaa'].values(), 3, 10)

        converged_keys = list(ma_dict['ratio'].keys())[-(min(converged_vza, converged_vaa)):]

        thresh_keys = [k for k,v in ma_dict['ratio'].items() if abs(v - list(ma_dict['ratio'].values())[0]) > ratio_thresh]

        sza_keys = [k for k in ma_dict['ratio'].keys() if k in converged_keys and thresh_keys]

        retrieval_dict['vza'][f'{wv}'] = np.mean([v for k, v in ma_dict['vza'].items() if k in sza_keys])
        retrieval_dict['unc_vza'][f'{wv}'] = np.std([v for k, v in ma_dict['vza'].items() if k in sza_keys])
        retrieval_dict['vaa'][f'{wv}'] = np.mean([v for k, v in ma_dict['vaa'].items() if k in sza_keys])
        retrieval_dict['unc_vaa'][f'{wv}'] = np.std([v for k, v in ma_dict['vaa'].items() if k in sza_keys])

    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].errorbar(retrieval_dict['vza'].keys(), list(retrieval_dict['vza'].values()),
                    yerr=list(retrieval_dict['unc_vza'].values()),
                    marker='', linestyle='', capsize=5)
    axs[1].errorbar(retrieval_dict['vza'].keys(), list(retrieval_dict['vaa'].values()),
                    yerr=list(retrieval_dict['unc_vaa'].values()),
                    marker='', linestyle='', capsize=5)

    axs[0].grid(color='black', alpha=0.5, axis='y')
    axs[1].grid(color='black', alpha=0.5, axis='y')

    axs[0].set_ylabel('VZA')
    axs[1].set_ylabel('VAA')

    fig.tight_layout()
    fig.savefig(os.path.join(results_path, f'retrieval_plot_after.png'))

def wav_separated_misalignment_calculator(dataset, wavelength, site):
    ma_dict = {'vza': {}, 'unc_vza': {}, 'vaa': {}, 'ratio': {}, 'unc_ratio': {}, 'unc_vaa': {}, 'num': {},
               'obs_ratio': {}, 'offset': {}, 'obs_grid': {}, 'ratio_grid': {}, 'time': {}, 'unc_grid': {}}

    residuals = []

    for wav in wavelength:
        ds = dataset.loc[dict(wv = wav)].set_coords('sza').where(dataset.sza > 0)
        ds = ds.dropna(dim = 'date')
        try:
            mean, unc = chi_square_minimiser_MCMC(ds.sza.values, ds.saa.values,
                                                  ds.dir_diff_ratio.values,
                                                  np.array(list(ds.ratio.values)))

            mean = list(mean)
            unc = list(unc)

            if mean[0] < 0:
                mean[0] = -mean[0]
                mean[1] += -180

            ratio_grid = ratio_calculator(mean[0], mean[1], mean[2],
                                          ds.sza.values, ds.saa.values,
                                          ds.dir_diff_ratio.values)
            ratio_unc = ratio_uncertainty_calculator(mean[0], mean[1],
                                                     ds.sza.values, ds.saa.values,
                                                     unc[0], unc[1]) * ratio_grid / 100
            ma_dict['vza'][f'{wav}'] = mean[0]
            ma_dict['unc_vza'][f'{wav}'] = unc[0]
            ma_dict['vaa'][f'{wav}'] = mean[1]
            ma_dict['unc_vaa'][f'{wav}'] = unc[1]
            ma_dict['num'][f'{wav}'] = len(ds.sza.values)
            ma_dict['offset'][f'{wav}'] = mean[2]
            ma_dict['obs_grid'][f'{wav}'] = np.array(list(ds.ratio.values))
            ma_dict['ratio_grid'][f'{wav}'] = ratio_grid
            ma_dict['time'][f'{wav}'] = np.array(list(ds.time.values))
            ma_dict['unc_grid'][f'{wav}'] = ratio_unc
            residuals += [float(x) for x in list((np.array(list(ds.ratio.values)) - ratio_grid) / ratio_unc)]

            ratio_grid = ratio_calculator(mean[0], mean[1], mean[2],
                                          ds.sza.values, ds.saa.values,
                                          ds.dir_diff_ratio.values)
            ratio_unc = ratio_uncertainty_calculator(mean[0], mean[1],
                                                     ds.sza.values, ds.saa.values,
                                                     unc[0], unc[1]) * ratio_grid/100

            ma_dict['ratio'][f'{wav}'] = np.mean(ratio_grid)
            ma_dict['unc_ratio'][f'{wav}'] = np.sqrt((np.std(ratio_grid)**2 + np.sum(ratio_unc**2)/len(ratio_unc)**2))
            ma_dict['obs_ratio'][f'{wav}'] = np.mean(np.array(list(ds.ratio.values)))

        except:
            ma_dict[f'{wav}'] = np.nan

    fig, axs = plt.subplots(4,1, sharex = True)
    axs[0].errorbar(ma_dict['vza'].keys(), list(ma_dict['vza'].values()), yerr = list(ma_dict['unc_vza'].values()),
                 marker = '', linestyle = '', capsize = 5)
    axs[1].errorbar(ma_dict['vza'].keys(), list(ma_dict['vaa'].values()), yerr=list(ma_dict['unc_vaa'].values()),
                    marker='', linestyle='', capsize=5)
    axs[2].errorbar(ma_dict['vza'].keys(), list(ma_dict['ratio'].values()), yerr=list(ma_dict['unc_ratio'].values()),
                    marker='x', linestyle='', capsize=5)
    axs[2].scatter(ma_dict['vza'].keys(), list(ma_dict['obs_ratio'].values()),
                    marker='o')
    axs[3].bar(ma_dict['vza'].keys(), list(ma_dict['num'].values()))

    axs[0].grid(color = 'black', alpha = 0.5, axis = 'y')
    axs[1].grid(color = 'black', alpha = 0.5, axis = 'y')
    axs[2].grid(color = 'black', alpha = 0.5, axis = 'y')

    axs[2].set_ylim(0.9,1.1)

    axs[0].set_ylabel('VZA')
    axs[1].set_ylabel('VAA')
    axs[2].set_ylabel('Ratio')
    axs[3].set_ylabel('Number of \nMeasurements')
    fig.tight_layout()
    fig.savefig(os.path.join(results_path , f'{site}_retrieval_plot.png'))

    return ma_dict


def wav_together_misalignment_calculator(dataset, wavelength, site):
    ma_dict = {'vza': [], 'unc_vza': [], 'vaa': [], 'ratio': {}, 'unc_ratio': {}, 'unc_vaa': {}, 'num': [],
               'obs_ratio': {}, 'offset': {}, 'ratio_grid': {}, 'obs_grid': {}, 'time': {}, 'unc_grid': {}}

    residuals = []

    ds = dataset.set_coords('sza').where(dataset.sza > 0)
    ds = ds.dropna(dim = 'date')

    mean, unc = chi_square_minimiser_MCMC_10offsets(ds.sza.values, ds.saa.values,
                                          ds.dir_diff_ratio.values,
                                          np.array(list(ds.ratio.values)),
                                                    plot_name=site)

    print('VZA', mean[0], unc[0])
    print('VAA', mean[1], unc[1])
    mean = list(mean)
    unc = list(unc)

    if mean[0] < 0:
        mean[0] = -mean[0]
        mean[1] += -180

    ma_dict['vza'] = mean[0]
    ma_dict['unc_vza'] = unc[0]
    ma_dict['vaa'] = mean[1]
    ma_dict['unc_vaa'] = unc[1]
    ma_dict['num'] = len(ds.sza.values)

    for iwav, wav in enumerate(wavelength):
        ds = dataset.loc[dict(wv=wav)].set_coords('sza').where(dataset.sza > 0)
        ds = ds.dropna(dim='date')
        try:

            ratio_grid = ratio_calculator(mean[0], mean[1], mean[iwav+2],
                                          ds.sza.values, ds.saa.values,
                                          ds.dir_diff_ratio.values)
            ratio_unc = ratio_uncertainty_calculator(mean[0], mean[1],
                                                     ds.sza.values, ds.saa.values,
                                                     unc[0], unc[1]) * ratio_grid / 100

            ma_dict['ratio'][f'{wav}'] = np.mean(ratio_grid)
            ma_dict['unc_ratio'][f'{wav}'] = np.sqrt(
                (np.std(ratio_grid) ** 2 + np.sum(ratio_unc ** 2) / len(ratio_unc) ** 2))
            ma_dict['obs_ratio'][f'{wav}'] = np.mean(np.array(list(ds.ratio.values)))
            ma_dict['offset'][f'{wav}'] = mean[iwav + 2]
            ma_dict['obs_grid'][f'{wav}'] = np.array(list(ds.ratio.values))
            ma_dict['ratio_grid'][f'{wav}'] = ratio_grid
            ma_dict['time'][f'{wav}'] = np.array(list(ds.time.values))
            ma_dict['unc_grid'][f'{wav}'] = ratio_unc
            residuals += [float(x) for x in list((np.array(list(ds.ratio.values)) - ratio_grid)/ratio_unc)]

        except:
            ma_dict[f'{wav}'] = np.nan

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.hist(residuals, 50, density = True, edgecolor = 'black', align = 'mid')
    fig.savefig(os.path.join(results_path, f'{site}_residuals_hist.png'))

    fig = plt.figure()
    ax = fig.add_subplot(projection = 'polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.errorbar(np.radians(ma_dict['vaa']), ma_dict['vza'], xerr = np.radians(ma_dict['unc_vaa']), yerr = ma_dict['unc_vza'], capsize = 5)
    ax.set_ylim([0, 5])
    fig.savefig(os.path.join(results_path, f'{site}_retrieval_plot_combined.png'))

    fig, ax = plt.subplots(1,1, sharex = True)
    ax.errorbar(ma_dict['ratio'].keys(), [ma_dict['ratio'][k] - ma_dict['offset'][k] for k in ma_dict['ratio'].keys()],
                yerr=list(ma_dict['unc_ratio'].values()),
                    marker='x', linestyle='', capsize=5)

    ax.grid(color = 'black', alpha = 0.5, axis = 'y')
    ax.set_ylabel('Ratio')
    ax.set_xlabel('Wavelength')
    fig.tight_layout()
    fig.savefig(os.path.join(results_path , f'{site}_ratio_plot_combined.png'))

    return ma_dict

'''
ma_dict = {'mean': {}, 'unc': {}}
for wv in ratio_dict.keys():
    vza, u_vza = chi_square_minimiser_MCMC(sza_measured, saa_measured,dir_diff_dict[wv], ratio_dict[wv])
    ma_dict['mean'][wv] = vza[0]
    ma_dict['unc'][wv] = u_vza[0]

plt.errorbar(ma_dict['mean'].keys(), list(ma_dict['mean'].values()), yerr = list(ma_dict['unc'].values()),
                 marker = '', linestyle = '', capsize = 5)
plt.show()
'''
#for wv in wavelengths:
    #plot_misalign_sza(data,  wv)
#plot_misalign_sza_all_wavs(data_before_may24)

#find_misalignment_angles(data_after_may24, 0.02)
#plot_misalign_sza(data,  '1640')
#wav_separated_misalignment_calculator(data, wavelengths)

#wav_together_misalignment_calculator(data, wavelengths, 'GHNAv3')


##GHNA TOD PLOTS
bins = [630, 715, 745, 815, 845, 915, 945, 1015, 1045, 1115, 1145, 1315, 1345, 1415, 1445, 1515, 1545]
time = ['0700', '0730', '0800', '0830', '0900', '0930', '1000', '1030', '1100', '1130', '1300', '1330', '1400', '1430',
        '1500', '1530']

before_dict = wav_separated_misalignment_calculator(data_before_may24, wavelengths, 'GHNAv3_before')
after_dict = wav_separated_misalignment_calculator(data_after_may24, wavelengths, 'GHNAv3_after')
all_dict = wav_separated_misalignment_calculator(data, wavelengths, 'GHNAv3')



for wav in wavelengths:

    fig, axs = plt.subplots(4, 1, sharex=True)

    before_dict['time'][f'{wav}'] = [int(x) for x in before_dict['time'][f'{wav}']]
    after_dict['time'][f'{wav}'] = [int(x) for x in after_dict['time'][f'{wav}']]
    all_dict['time'][f'{wav}'] = [int(x) for x in all_dict['time'][f'{wav}']]

#    before_dict['ratio_grid'][f'{wav}'] = ratio_calculator(all_dict['vza'], all_dict['vza'], before_dict['offset'][f'{wav}'],
 #                                                           data_before_may24.sza.values, data_before_may24.saa.values,
  #                                                          data_before_may24.dir_diff_ratio.loc[dict(wv=wav)].values)

#    after_dict['ratio_grid'][f'{wav}'] = ratio_calculator(all_dict['vza'], all_dict['vza'], after_dict['offset'][f'{wav}'],
 #                                                           data_after_may24.sza.values, data_after_may24.saa.values,
  #                                                          data_after_may24.dir_diff_ratio.loc[dict(wv=wav)].values)

    before_medians, be, bn = binned_statistic(list(before_dict['time'][f'{wav}']), list(before_dict['ratio_grid'][f'{wav}']), statistic = 'median', bins = bins)
    before_std, be, bn  = binned_statistic(list(before_dict['time'][f'{wav}']), list(before_dict['ratio_grid'][f'{wav}']), statistic = 'std', bins = bins)

    after_medians, bin_edges, binnumber = binned_statistic(list(after_dict['time'][f'{wav}']), list(after_dict['ratio_grid'][f'{wav}']), statistic = 'median', bins = bins)
    after_std, bin_edge, binnumbe = binned_statistic(list(after_dict['time'][f'{wav}']), list(after_dict['ratio_grid'][f'{wav}']), statistic = 'std', bins = bins)

    all_medians, bin_edges, binnumber = binned_statistic(list(all_dict['time'][f'{wav}']), list(all_dict['ratio_grid'][f'{wav}']), statistic = 'median', bins = bins)
    all_std, bin_edge, binnumbe = binned_statistic(list(all_dict['time'][f'{wav}']), list(all_dict['ratio_grid'][f'{wav}']), statistic = 'std', bins = bins)

    before_obs_medians, be, bn = binned_statistic(list(before_dict['time'][f'{wav}']),
                                              list(before_dict['obs_grid'][f'{wav}']), statistic='median', bins=bins)
    before_obs_std, be, bn = binned_statistic(list(before_dict['time'][f'{wav}']),
                                          list(before_dict['obs_grid'][f'{wav}']), statistic='std', bins=bins)

    after_obs_medians, bin_edges, binnumber = binned_statistic(list(after_dict['time'][f'{wav}']),
                                                           list(after_dict['obs_grid'][f'{wav}']), statistic='median',
                                                           bins=bins)
    after_obs_std, bin_edge, binnumbe = binned_statistic(list(after_dict['time'][f'{wav}']),
                                                     list(after_dict['obs_grid'][f'{wav}']), statistic='std',
                                                     bins=bins)

    all_obs_medians, bin_edges, binnumber = binned_statistic(list(all_dict['time'][f'{wav}']),
                                                         list(all_dict['obs_grid'][f'{wav}']), statistic='median',
                                                         bins=bins)
    all_obs_std, bin_edge, binnumbe = binned_statistic(list(all_dict['time'][f'{wav}']),
                                                   list(all_dict['obs_grid'][f'{wav}']), statistic='std', bins=bins)

    before_sza, be, bn = binned_statistic(list(before_dict['time'][f'{wav}']),
                                              data_before_may24.sza.values, statistic='median', bins=bins)
    before_sza_std, be, bn = binned_statistic(list(before_dict['time'][f'{wav}']),
                                         data_before_may24.sza.values, statistic='std', bins=bins)

    after_sza, bin_edges, binnumber = binned_statistic(list(after_dict['time'][f'{wav}']),
                                                           data_after_may24.sza.values, statistic='median',
                                                           bins=bins)
    after_sza_std, bin_edge, binnumbe = binned_statistic(list(after_dict['time'][f'{wav}']),
                                                     data_after_may24.sza.values, statistic='std',
                                                     bins=bins)

    all_sza, bin_edges, binnumber = binned_statistic(list(all_dict['time'][f'{wav}']),
                                                         data.sza.values, statistic='median',
                                                         bins=bins)
    all_sza_std, bin_edge, binnumbe = binned_statistic(list(all_dict['time'][f'{wav}']),
                                                   data.sza.values, statistic='std', bins=bins)

    axs[0].errorbar(time, before_medians, yerr=before_std, linestyle='', marker='x', capsize=5, color = 'red', label = 'before')
    axs[0].errorbar(time, after_medians, yerr=after_std, linestyle='', marker='x', capsize=5, color = 'green', label = 'after')
    axs[0].errorbar(time, all_medians, yerr=all_std, linestyle='', marker='x', capsize=5, color = 'blue', label = 'all')

    axs[1].errorbar(time, before_obs_medians, yerr=before_obs_std, linestyle='', marker='x', capsize=5, color='red',
                    label='before')
    axs[1].errorbar(time, after_obs_medians, yerr=after_obs_std, linestyle='', marker='x', capsize=5, color='green',
                    label='after')
    axs[1].errorbar(time, all_obs_medians, yerr=all_obs_std, linestyle='', marker='x', capsize=5, color='blue', label='all')

    axs[2].scatter(time, before_medians - before_obs_medians, linestyle = '', marker = 'x', color = 'red')
    axs[2].scatter(time, after_medians - after_obs_medians, linestyle='', marker='x', color='green')
    axs[2].scatter(time, all_medians - all_obs_medians, linestyle='', marker='x', color='blue')

    axs[3].errorbar(time, before_sza, yerr=before_sza_std, linestyle='', marker='x', capsize=5, color='red',
                    label='before')
    axs[3].errorbar(time, after_sza, yerr=after_sza_std, linestyle='', marker='x', capsize=5, color='green',
                    label='after')
    axs[3].errorbar(time, all_sza, yerr=all_sza_std, linestyle='', marker='x', capsize=5, color='blue',
                    label='all')

    axs[0].set_ylabel('Modelled Ratio')
    axs[1].set_ylabel('Observed Ratio')
    axs[2].set_ylabel('Modelled - Observed')
    axs[3].set_ylabel('SZA')
    axs[1].set_xlabel('Time of Day')

    axs[0].legend()
    axs[0].grid(color = 'black', alpha = 0.5, axis = 'y')
    axs[1].grid(color = 'black', alpha = 0.5, axis = 'y')
    axs[2].grid(color='black', alpha=0.5, axis='y')
    axs[3].grid(color='black', alpha=0.5, axis='y')

    fig.suptitle(f'{wav}')

    fig.tight_layout()
    fig.savefig(os.path.join(results_path , f'GHNA_ratio_tod_plot_{wav}.png'))




'''
corrected_measurements = measurements * ratio_calculator(sza_measured, saa_measured, 1.7, 95)
corrected_perc = (clear_sky_model - corrected_measurements) / corrected_measurements * 100
perc = (clear_sky_model - measurements) / measurements * 100

#corr_data = np.vstack((corrected_ratio, sza_measured, saa_measured, data[:,5])).T
#np.savetxt(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\irradiance_GHNA_v3_corrected.csv', corr_data, delimiter = ',')

bins = [630, 715, 745, 815, 845, 915, 945, 1015, 1045, 1115, 1145, 1315, 1345, 1415, 1445, 1515, 1545]
time = ['0700', '0730', '0800', '0830', '0900', '0930', '1000', '1030', '1100', '1130', '1300', '1330', '1400', '1430',
        '1500', '1530']

tod = data[:, 5]
timeWWUK = ['0900', '0930', '1000', '1030', '1100', '1130', '1300', '1330', '1400', '1430', '1500', '1530']
binsWWUK = [845, 915, 945, 1015, 1045, 1115, 1145, 1315, 1345, 1415, 1445, 1515, 1545]

corr_medians, bin_edges, binnumber = binned_statistic(tod, corrected_perc, statistic='median', bins=bins)
corr_std, bin_edge, binnumbe = binned_statistic(tod, corrected_perc, statistic='std', bins=bins)

medians, bin_edges, binnumber = binned_statistic(tod, perc, statistic='median', bins=bins)
std, bin_edge, binnumbe = binned_statistic(tod, perc, statistic='std', bins=bins)

plt.errorbar(time, medians, yerr=std, linestyle='', marker='x', capsize=5, color = 'red', label = 'measurements')
plt.errorbar(time, corr_medians, yerr=corr_std, linestyle='', marker='x', capsize=5, color = 'green', label = 'corrected')
plt.hlines(y=0, xmin=-0.1, xmax=15.5, alpha=0.5, color='black')
plt.xlabel('Time of Day')
plt.ylabel('Percentage Difference between \nModel and Measurements')
plt.legend()
plt.tight_layout()
plt.savefig(r'T:\ECO\EOServer\joe\hypernets_plots\misalignment\GHNAv3_corrected_tod_perc.png')
plt.show()

bins = [-5, 5, 15, 25, 35, 45, 55, 65, 75]
szas_binned = [0, 10, 20, 30, 40, 50, 60, 70]

corr_medians, bin_edges, binnumber = binned_statistic(sza_measured, corrected_perc, statistic='median', bins=bins)
corr_std, bin_edge, binnumbe = binned_statistic(sza_measured, corrected_perc, statistic='std', bins=bins)

medians, bin_edges, binnumber = binned_statistic(sza_measured, perc, statistic='median', bins=bins)
std, bin_edge, binnumbe = binned_statistic(sza_measured, perc, statistic='std', bins=bins)

plt.errorbar(szas_binned, medians, yerr=std, linestyle='', marker='x', capsize=5, color = 'red', label = 'measurements')
plt.errorbar(szas_binned, corr_medians, yerr=corr_std, linestyle='', marker='x', capsize=5, color = 'green', label = 'corrected')
plt.hlines(y=0, xmin=-0.1, xmax=70.5, alpha=0.5, color='black')
plt.xlabel('SZA')
plt.ylabel('Percentage Difference between \nModel and Measurements')
plt.tight_layout()
plt.savefig(r'T:\ECO\EOServer\joe\hypernets_plots\misalignment\GHNAv3_corrected_SZA_perc.png')
plt.show()

'''