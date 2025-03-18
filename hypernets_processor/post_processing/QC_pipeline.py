import numpy as np
import pandas as pd
import xarray as xr
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os
from scipy.stats import binned_statistic_2d
import glob
from seaborn.external.docscrape import header

wav_df = xr.open_dataset(
    r"T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\14\SEQ20240314T070025\HYPERNETS_L_GHNA_L1B_IRR_20240314T0700_20240416T1138_v2.0.nc"
)
wav = wav_df.wavelength.values


def find_nearest_to_wav(array, wv, value):
    wv = np.asarray(wv)
    idx = (np.abs(wv - value)).argmin()
    mean = np.mean(
        [array[idx - 2], array[idx - 1], array[idx], array[idx + 1], array[idx + 2]]
    )
    return mean

def interpolate_irradiance_sza(sza,ds_irr,variable):
    ds_irr_temp = ds_irr.copy()
    ds_irr_temp[variable].values = ds_irr_temp[variable].values / np.cos(np.float64(ds_irr_temp["sza"].values) / 180 * np.pi)[:, None]
    ds_irr_temp = ds_irr_temp.interp(sza=sza, wavelength = wav, method="linear")
    ds_irr_temp[variable].values = ds_irr_temp[variable].values * np.cos(np.float64(ds_irr_temp["sza"].values) / 180 * np.pi)
    return ds_irr_temp[variable].values

def modelled_data_read_and_interp(sza, mod_data, variable):
    sza = float(sza)
    interp_mod_data = interpolate_irradiance_sza(sza, mod_data, variable)
    return interp_mod_data

def percentile95(array):
    return np.nanpercentile(array, 95)

def percentile5(array):
    return np.nanpercentile(array, 5)

def percentile2_5(array):
    return np.nanpercentile(array, 2.5)

def percentile97_5(array):
    return np.nanpercentile(array, 97.5)

def percentile1(array):
    return np.nanpercentile(array, 1)

def percentile99(array):
    return np.nanpercentile(array, 99)

def percentile_3sigma_min(array):
    return np.nanpercentile(array, 0.3)

def percentile_3sigma_max(array):
    return np.nanpercentile(array, 99.7)

def sza_vza_bin_and_calc(data,cutting_data, stat, bound):
    sza = data[' sza'].values
    vza = data[' vza'].values
    refl = data[' refl_550nm'].values
    cutting_refl = cutting_data[' refl_550nm'].values
    cutting_sza = cutting_data[' sza'].values
    cutting_vza = cutting_data[' vza'].values

    bins = [0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5]
    bin_centers = [(bins[i] + bins[i+1])/2 for i in range(len(bins) - 1)]

    sza_bin_idx = []
    vza_bin_idx = []

    for j in range(len(cutting_sza)):
        for i in range(len(bins)):
            if bins[i] <= cutting_sza[j] < bins[i + 1]:
                sza_bin_idx.append(i)
            if bins[i] <= cutting_vza[j] < bins[i + 1]:
                vza_bin_idx.append(i)

    if stat == 'median':
        binned_data,x ,y ,b = binned_statistic_2d(sza, vza, refl, 'median', bins, expand_binnumbers=True)
    elif stat == '95th':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile95, bins, expand_binnumbers=True)
    elif stat == '5th':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile5, bins, expand_binnumbers=True)
    elif stat == '2.5th':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile2_5, bins, expand_binnumbers=True)
    elif stat == '97.5th':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile97_5, bins, expand_binnumbers=True)
    elif stat == '1st':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile1, bins, expand_binnumbers=True)
    elif stat == '99th':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile99, bins, expand_binnumbers=True)
    elif stat == '3sigma_min':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile_3sigma_min, bins, expand_binnumbers=True)
    elif stat == '3sigma_max':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, percentile_3sigma_max, bins, expand_binnumbers=True)
    else:
        print('stat not supported')
        binned_data, x, y, b = None, None, None, None

    refl_output = []
    sza_output = []
    vza_output = []

    if bound == 'lower':
        bound_passes = [False if v < binned_data[sza_bin_idx[i] , vza_bin_idx[i]] else True for i, v in enumerate(cutting_refl)]
    elif bound == 'upper':
        bound_passes = [False if v > binned_data[sza_bin_idx[i] , vza_bin_idx[i]] else True for i, v in enumerate(cutting_refl)]
    else:
        print('bound must be upper or lower')
        bound_passes = None

    for i in range(len(bin_centers)):
        for j in range(len(bin_centers)):
            if not np.isnan(binned_data[i][j]):
                refl_output.append(binned_data[i][j])
                sza_output.append(bin_centers[i])
                vza_output.append(bin_centers[j])

    return refl_output, sza_output, vza_output, bound_passes

def raa_binning(data, raa_limits):

    if raa_limits[1] > raa_limits[0]:
        new_data = data[(data["raa"] > raa_limits[0]) & (data["raa"] < raa_limits[1])]
        new_data = new_data.reset_index(drop=True)
        return new_data

    if raa_limits[1] < raa_limits[0]:
        new_data = data[(data["raa"] > raa_limits[0]) | (data["raa"] < raa_limits[1])]
        new_data = new_data.reset_index(drop=True)
        return new_data


def quad_plane(xy, a, b, c, d, e, f):
    x, y = xy
    return a + b * x + c * y + d * x**2 + e * y**2 + f * x * y


def plane_fit_and_plot(data, data_setting, stds):
    x = data[" sza"].values
    y = data[" vza"].values
    z = data[" refl_550nm"].values

    popt, pcov = curve_fit(quad_plane, (x, y), z)
    below = popt - stds * np.sqrt(np.diag(pcov))
    above = popt + stds * np.sqrt(np.diag(pcov))

    z_below = (
        quad_plane((data_setting[" sza"].values, data_setting[" vza"].values), *below)
        - data_setting[" refl_550nm"].values * 0.05
    )
    z_above = (
        quad_plane((data_setting[" sza"].values, data_setting[" vza"].values), *above)
        + data_setting[" refl_550nm"].values * 0.05
    )

    outliers = data_setting[
        (data_setting[" refl_550nm"] > z_above)
        | (data_setting[" refl_550nm"] < z_below)
    ]
    good_data = data_setting[
        (data_setting[" refl_550nm"] < z_above)
        & (data_setting[" refl_550nm"] > z_below)
    ]
    good_data.reset_index(drop=True, inplace=True)
    outliers.reset_index(drop=True, inplace=True)

    return outliers, good_data

def new_plane_fit(input_sza, input_vza, input_refl):
    x = input_sza
    y = input_vza
    z = input_refl

    popt, pcov = curve_fit(quad_plane, (x, y), z, nan_policy = 'omit')

    return popt, pcov

def compile_irradiance_list(irr_folder, site):
    files = [f for f in os.listdir(irr_folder) if f'{site}_clear_sky' in f]

    return files

def ratio_calculator(vza, vaa, sza, saa, direct_to_diffuse):
    sza = np.radians(sza)
    saa = np.radians(saa)
    vza = np.radians(vza)
    vaa = np.radians(vaa)
    #new_sza = np.cos(sza + vza*np.cos((saa - vaa + 360) % 360))
    new_sza = np.arccos(np.cos(sza) * np.cos(vza) + np.sin(sza) * np.sin(vza) * np.cos((saa - vaa)))
    new_direct_to_diffuse=direct_to_diffuse*np.cos(new_sza)/np.cos(sza)
    return (new_direct_to_diffuse+1) / (direct_to_diffuse+1)


class PostProcessingDataset:

    def __init__(self, rad_path, irr_path, clear_sky_path, site, clear_sky_aod = None):

        # read in radiance
        data = pd.read_csv(rad_path)
        # define raa
        data.loc[:, "raa"] = (data.loc[:, " vaa"] - data.loc[:, " saa"] + 360) % 360
        # extract dates and times
        dates = []
        times = []
        for i in range(len(data)):
            date = data["# id"][i][3:11]
            time = data["# id"][i][12:16]
            dates.append(date)
            times.append(time)
        dt_data = data.assign(date=dates, time=times)
        labelled_data = dt_data.assign(
            post_processing_flags=[[] for _ in range(len(data))]
        )
        # set radiance
        self.radiance = dt_data
        self.labelled_radiance = labelled_data
        # read in irradiance
        self.irradiance = pd.read_csv(irr_path)
        #define other features
        self.site = site
        self.cc_radiance = None
        self.radiance_good = None
        self.radiance_outliers = None
        self.cloud_passes = None
        self.cloud_check_tol = None
        self.clear_sky_path = clear_sky_path
        self.plane_iteration = 0
        if clear_sky_aod is None:
            self.clear_sky_list = compile_irradiance_list(clear_sky_path, site)
            self.clear_sky_aod = None
            self.clear_sky_model = None
        else:
            self.clear_sky_list = None
            self.clear_sky_aod = clear_sky_aod
            self.clear_sky_model = xr.open_dataset("T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_aod{}.nc".format(site, clear_sky_aod))

    def choose_clear_sky_model(self, aod):
        if self.clear_sky_list is not None:
            model = [f for f in self.clear_sky_list if aod in f]
            self.clear_sky_aod = aod
            self.clear_sky_model = xr.open_dataset(self.clear_sky_path + str(model[0]))

    def size(self, var):
        if var == "radiance":
            print(len(self.radiance))
        elif var == "good":
            print(len(self.radiance_good))
        elif var == "outliers":
            print(len(self.radiance_outliers))
        else:
            print("var must be radiance, good, or outliers")

    def save(self, var, filepath):
        if var == "radiance":
            data = self.radiance
        elif var == "good":
            data = self.radiance_good
        elif var == "outliers":
            data = self.radiance_outliers
        else:
            print("data not saved")
            quit()

        data.to_csv(filepath, index=False)


    def basic_outlier_definition(self):
        mean = self.radiance[" refl_550nm"].mean()
        stde = self.radiance[" refl_550nm"].std()
        max_range = mean + (stde * 3)
        min_range = mean - (stde * 3)
        outliers = self.radiance[
            (self.radiance[" refl_550nm"] > max_range)
            | (self.radiance[" refl_550nm"] < min_range)
        ]
        good_data = self.radiance[
            (self.radiance[" refl_550nm"] < max_range)
            & (self.radiance[" refl_550nm"] > min_range)
        ]
        good_data.reset_index(drop=True, inplace=True)
        outliers.reset_index(drop=True, inplace=True)

        self.radiance_outliers = outliers
        self.radiance_good = good_data

    def maintenance_check(self, bad_dates):
        ### note bad_dates need to be in speech marks###
        bad_inds = []
        # get dates of measurements
        for i in range(len(self.radiance)):
            date = self.radiance["date"][i]

            # remove maintenance dates
            if date in bad_dates:
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

        for x in self.labelled_radiance["post_processing_flags"][
            self.labelled_radiance["date"].isin(bad_dates)
        ]:
            x.append(1)

    def sza_check(self, sza_limit):
        bad_inds = []
        for i in range(len(self.radiance)):
            sza = self.radiance[" sza"][i]
            if sza > sza_limit:
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

        for x in self.labelled_radiance["post_processing_flags"].loc[
            self.labelled_radiance[" sza"] > sza_limit
        ]:
            x.append(2)

    def raa_cut(self, raa_limit):
        bad_inds = []
        for i in range(len(self.radiance)):
            raa = self.radiance["raa"][i]
            if (raa < raa_limit) | (raa > 360 - raa_limit):
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

        for x in self.labelled_radiance["post_processing_flags"].loc[
            (self.labelled_radiance["raa"] < raa_limit)
            | (self.labelled_radiance["raa"] > 360 - raa_limit)
        ]:
            x.append(6)

    def clean_irr(self):
        IDs = self.irradiance["ID"]
        flags = self.irradiance["Flag"]

        bad_inds = []
        bad_flags = []
        bad_IDs = []
        # find flags in irr data
        for i in range(len(flags)):
            if flags.values[i] != 0:
                bad_inds.append(i)
                bad_flags.append(flags.values[i])
                bad_IDs.append(IDs[i])
        # check irradiance file exists for every radiance
        for i, ID in enumerate(list(self.irradiance["ID"])):
            if ID in list(self.radiance["# id"]):
                continue
            else:
                bad_IDs.append(ID)
                bad_inds.append(i)

        # clean irradiance
        df_clean = self.irradiance.drop(bad_inds)
        df_clean.reset_index(drop=True, inplace=True)
        self.irradiance = df_clean
        # clean radiance
        new = self.radiance[~self.radiance["# id"].isin(bad_IDs)]
        new.reset_index(drop=True, inplace=True)
        self.radiance = new

        for x in self.labelled_radiance["post_processing_flags"].loc[
            self.labelled_radiance["# id"].isin(bad_IDs)
        ]:
            x.append(3)

    def misalignment_correction(self, vza, vaa, multiple_periods = False, period_date = None):
        szas = self.radiance[' sza']
        saas = self.radiance[' saa']
        data = np.zeros((self.irradiance.shape[0], len(self.irradiance.columns) - 6))
        wav_list = [int(''.join(filter(str.isdigit, s))) for s in self.radiance.keys() if 'refl' in s]

        for wv in wav_list:
            dir_to_diff = np.zeros(self.radiance.shape[0])

            for i in range(data.shape[0]):
                dir_to_diff[i] = find_nearest_to_wav(
                    modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'direct_to_diffuse_irradiance_ratio'),
                    wav, wv)

            if not multiple_periods:
                self.radiance[f' refl_{wv}nm'] = self.radiance[f' refl_{wv}nm'] * ratio_calculator(vza, vaa, szas, saas, dir_to_diff)
            else:
                divider_idx = np.min(np.argwhere(self.radiance['date'] == period_date))
                self.radiance[f' refl_{wv}nm'][:divider_idx] = (
                        self.radiance[f' refl_{wv}nm'][:divider_idx] *
                        ratio_calculator(vza[0], vaa[0], szas[:divider_idx], saas[:divider_idx],
                                         dir_to_diff[:divider_idx]))
                self.radiance[f' refl_{wv}nm'][divider_idx:] = (
                        self.radiance[f' refl_{wv}nm'][divider_idx:] *
                        ratio_calculator(vza[1], vaa[1], szas[divider_idx:], saas[divider_idx:],
                                         dir_to_diff[divider_idx:]))


    def cloud_check(self, tolerance, wavelength, rewrite, rewrite_var = None):
        szas = self.irradiance['SZA']
        IDs = self.irradiance['ID']
        saas = self.irradiance['SAA']

        if self.cloud_passes is None:
            data = np.zeros((self.irradiance.shape[0], len(self.irradiance.columns) - 6))

            for j in range(self.irradiance.shape[0]):
                for i in range(len(self.irradiance.columns) - 6):
                    data[j, i] = self.irradiance['{}'.format(i)][j]

            passes = np.zeros(self.irradiance.shape[0])
            values = np.zeros(self.irradiance.shape[0])
            abs_diff = np.zeros(self.irradiance.shape[0])
            model = np.zeros(self.irradiance.shape[0])
            observ = np.zeros(self.irradiance.shape[0])

            for i in range(data.shape[0]):
                aod_1 = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'solar_irradiance_BOA'), wav, wavelength)
                meas = find_nearest_to_wav(data[i, :], wav, wavelength)
                values[i] = aod_1 * tolerance - meas
                abs_diff[i] = aod_1 - meas
                model[i] = aod_1
                observ[i] = meas

                if values[i] > 0:
                    passes[i] = 1  # cloudy
                else:
                    passes[i] = 0  # clear

                print(i, passes[i])

            # save passes
            self.cloud_passes = passes
            output_data = np.array([IDs,szas, saas ,model, observ, abs_diff, [x[12:16] for x in IDs], [x[3:11] for x in IDs], self.irradiance['Flag']]).T
            np.savetxt(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\irradiance_GHNA_v1_diffs.csv',output_data, fmt = '%s',delimiter=',')

        cut_IDs = IDs[self.cloud_passes == 1]

        # rewrite datasets
        if rewrite_var == "radiance":
            data_refl = self.radiance
        elif rewrite_var == "good":
            data_refl = self.radiance_good
        elif rewrite_var == "outliers":
            data_refl = self.radiance_outliers
        else:
            data_refl = self.radiance

        new = data_refl[~data_refl["# id"].isin(cut_IDs)]
        new.reset_index(drop=True, inplace=True)

        if rewrite:

            if rewrite_var == "radiance":
                self.radiance = new
            elif rewrite_var == "good":
                self.radiance_good = new
            elif rewrite_var == "outliers":
                self.radiance_outliers = new
            elif rewrite_var == "labels":
                for x in self.labelled_radiance["post_processing_flags"].loc[
                    self.labelled_radiance["# id"].isin(cut_IDs)
                ]:
                    x.append(4)

        else:
            print("rewrite_var must be radiance, good, outliers, or labels")
            print("radiances not filtered by cloud check")
            self.cc_radiance = new

    def write_irr_analysis_files(self, filename, wavelengths):
        szas = self.irradiance['SZA']
        IDs = self.irradiance['ID']
        saas = self.irradiance['SAA']

        data = np.zeros((self.irradiance.shape[0], len(self.irradiance.columns) - 6))
        for j in range(self.irradiance.shape[0]):
            for i in range(len(self.irradiance.columns) - 6):
                data[j, i] = self.irradiance['{}'.format(i)][j]

        output_data = pd.DataFrame({'IDs': IDs, 'SZA': szas, 'SAA': saas,
                                    'Time': [x[12:16] for x in IDs],'Date': [x[3:11] for x in IDs],
                                    'Flag': self.irradiance['Flag']})

        for wv in wavelengths:
            model = np.zeros(self.irradiance.shape[0])
            observ = np.zeros(self.irradiance.shape[0])
            dir_to_diff = np.zeros(self.irradiance.shape[0])

            for i in range(data.shape[0]):
                model[i] = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'solar_irradiance_BOA'),
                                               wav, wv)
                observ[i] = find_nearest_to_wav(data[i, :], wav, wv)
                dir_to_diff[i] = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'direct_to_diffuse_irradiance_ratio'),
                                                     wav, wv)

            output_data[f'model_{wv}nm'] = model
            output_data[f'obs_{wv}nm'] = observ
            output_data[f'dir_diff_ratio_{wv}nm'] = dir_to_diff

        output_data.to_csv(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\{}.csv'.format(filename))

    def plane_fitter(self, labelled = False):

        if self.cc_radiance is None:
            self.cc_radiance = self.radiance

        # define datasets
        data = self.cc_radiance

        if labelled:
            data_unmasked = self.labelled_radiance
        else:
            data_unmasked = self.radiance

        data_30_90 = raa_binning(data, (30, 90))
        data_90_150 = raa_binning(data, (90, 150))
        data_150_210 = raa_binning(data, (150, 210))
        data_210_270 = raa_binning(data, (210, 270))
        data_270_330 = raa_binning(data, (270, 330))
        data_330_30 = raa_binning(data, (330, 30))

        data_list = [
            data_30_90,
            data_90_150,
            data_150_210,
            data_210_270,
            data_270_330,
            data_330_30,
        ]

        data_unmasked_30_90 = raa_binning(data_unmasked, (30, 90))
        data_unmasked_90_150 = raa_binning(data_unmasked, (90, 150))
        data_unmasked_150_210 = raa_binning(data_unmasked, (150, 210))
        data_unmasked_210_270 = raa_binning(data_unmasked, (210, 270))
        data_unmasked_270_330 = raa_binning(data_unmasked, (270, 330))
        data_unmasked_330_30 = raa_binning(data_unmasked, (330, 30))

        data_unmasked_list = [
            data_unmasked_30_90,
            data_unmasked_90_150,
            data_unmasked_150_210,
            data_unmasked_210_270,
            data_unmasked_270_330,
            data_unmasked_330_30,
        ]

        outs, good = plane_fit_and_plot(data_list[0], data_unmasked_list[0], 3)
        for i in range(len(data_list) - 1):
            outs = pd.concat(
                [
                    outs,
                    plane_fit_and_plot(data_list[i + 1], data_unmasked_list[i + 1], 3)[
                        0
                    ],
                ],
                ignore_index=True,
            )
            good = pd.concat(
                [
                    good,
                    plane_fit_and_plot(data_list[i + 1], data_unmasked_list[i + 1], 3)[
                        1
                    ],
                ],
                ignore_index=True,
            )

        if labelled:
            for y in self.labelled_radiance["post_processing_flags"][
                self.labelled_radiance.apply(tuple, axis=1).isin(
                    [tuple(x) for x in outs.values]
                )
            ]:
                y.append(5)
        else:
            self.radiance_good = good
            self.radiance_outliers = outs

        #make this general so fitted variables and binned variables can be changed

    def new_plane_fitter(self, labelled = False, first_iteration = True, plot = False, method = 'plane_fit'):

        self.plane_iteration += 1

        if self.cc_radiance is None:
            self.cc_radiance = self.radiance

        if not first_iteration:
            data = self.radiance_good
        else:
            data = self.cc_radiance

        if labelled:
            data_unmasked = self.labelled_radiance
        else:
            data_unmasked = self.radiance

        raa_limits_list = ['(30,90)', '(90,150)', '(150,210)', '(210,270)', '(270,330)', '(330,30)']

        data_30_90 = raa_binning(data, (30, 90))
        data_90_150 = raa_binning(data, (90, 150))
        data_150_210 = raa_binning(data, (150, 210))
        data_210_270 = raa_binning(data, (210, 270))
        data_270_330 = raa_binning(data, (270, 330))
        data_330_30 = raa_binning(data, (330, 30))

        data_list = [data_30_90, data_90_150, data_150_210, data_210_270, data_270_330, data_330_30]

        data_unmasked_30_90 = raa_binning(data_unmasked, (30, 90))
        data_unmasked_90_150 = raa_binning(data_unmasked, (90, 150))
        data_unmasked_150_210 = raa_binning(data_unmasked, (150, 210))
        data_unmasked_210_270 = raa_binning(data_unmasked, (210, 270))
        data_unmasked_270_330 = raa_binning(data_unmasked, (270, 330))
        data_unmasked_330_30 = raa_binning(data_unmasked, (330, 30))

        data_unmasked_list = [data_unmasked_30_90, data_unmasked_90_150, data_unmasked_150_210, data_unmasked_210_270,
                              data_unmasked_270_330, data_unmasked_330_30]

        for i in range(len(data_list)):
            data_cutting = data_unmasked_list[i]
            binned95, bin_centers_sza, bin_centers_vza, upper_passes = sza_vza_bin_and_calc(data_list[i],data_cutting, '3sigma_max', 'upper')
            binned5, bin_centers_sza, bin_centers_vza, lower_passes = sza_vza_bin_and_calc(data_list[i],data_cutting, '3sigma_min', 'lower')

            below, below_cov = new_plane_fit(bin_centers_sza, bin_centers_vza, binned5)
            above, above_cov = new_plane_fit(bin_centers_sza, bin_centers_vza, binned95)

            df_below = pd.DataFrame({'refl': binned5, 'vza': bin_centers_vza, 'sza': bin_centers_sza})
            df_above = pd.DataFrame({'refl': binned95, 'vza': bin_centers_vza, 'sza': bin_centers_sza})



            z_lower = quad_plane((data_cutting[' sza'].values, data_cutting[' vza'].values),
                                 *below)
            z_upper = quad_plane((data_cutting[' sza'].values, data_cutting[' vza'].values),
                                 *above)

            if method == 'plane_fit':
                outliers = data_cutting[(data_cutting[' refl_550nm'] > z_upper) |
                                        (data_cutting[' refl_550nm'] < z_lower)]
                good_data = data_cutting[(data_cutting[' refl_550nm'] < z_upper) &
                                        (data_cutting[' refl_550nm'] > z_lower)]
            if method == 'bounds':
                good_data = data_cutting[(upper_passes and lower_passes)]
                outliers = data_cutting[not (upper_passes and lower_passes)]
            else:
                print('invalid_method')
                exit()

            good_data.reset_index(drop=True, inplace=True)
            outliers.reset_index(drop=True, inplace=True)

            if plot:
                x_range = np.arange(0, 65, 5)
                fig, axs = plt.subplots(1, 3, figsize=(6, 4), sharey=True)
                for j in range(3):
                    axs[j].plot(x_range, quad_plane(((j + 1) * 20, x_range), *below), color='black')
                    axs[j].plot(x_range, quad_plane(((j + 1) * 20, x_range), *above), color='black')
                    axs[j].set_title(f'SZA = {(j + 1) * 20}')
                    axs[j].scatter(
                        outliers[outliers[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' vza'].values,
                        outliers[outliers[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' refl_550nm'].values,
                        color='red', s=5)
                    axs[j].scatter(
                        good_data[good_data[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' vza'].values,
                        good_data[good_data[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' refl_550nm'].values,
                        color='green', s=5)
                    axs[j].scatter(
                        df_below.loc[(df_below['sza'] > (j + 1)*20 -1) & (df_below['sza'] < (j+1) *20 + 1)]['vza'].values,
                        df_below.loc[(df_below['sza'] > (j + 1)*20 -1) & (df_below['sza'] < (j+1) *20 + 1)]['refl'].values,
                        color='blue', s=20, marker = 'v')
                    axs[j].scatter(
                        df_above.loc[(df_above['sza'] > (j + 1) * 20 - 1) & (df_above['sza'] < (j + 1) * 20 + 1)][
                            'vza'].values,
                        df_above.loc[(df_above['sza'] > (j + 1) * 20 - 1) & (df_above['sza'] < (j + 1) * 20 + 1)][
                            'refl'].values,
                        color='blue', s=20, marker = '^')
                    axs[j].set_xlabel('VZA')
                    axs[0].set_ylabel('Reflectance')
                    fig.suptitle('RAA {}'.format(raa_limits_list[i]))
                    fig.savefig(r'T:/ECO/EOServer/joe/hypernets_plots/plane_models/' +
                                'sza_slices_3sig_{}_{}_{}.png'.format(raa_limits_list[i], self.plane_iteration, method))
                plt.show()

            if ('outs' and 'good') not in locals():
                outs = outliers
                good = good_data

            else:
                outs = pd.concat([outs, outliers], ignore_index=True)
                good = pd.concat([good, good_data], ignore_index=True)

        if labelled:
            for y in self.labelled_radiance['post_processing_flags'][self.labelled_radiance.apply(tuple, axis = 1).isin([tuple(x) for x in outs.values])]:
                y.append(5)
        else:
            self.radiance_good = good
            self.radiance_outliers = outs



        del outs
        del good


    def tol_optimiser(self, tol_start, tol_stop, tol_step, wavelength, good_limit,
                      plot = False):
        IDs = self.irradiance['ID']
        tol = np.arange(tol_start, tol_stop, tol_step)
        outs = []
        good = []

        for i in tol:
            self.cloud_passes = None
            self.cloud_check(i, wavelength, False)
            self.cloud_check(i, wavelength, False)

            cut_IDs = IDs[self.cloud_passes == 1]
            out_cut = self.radiance_outliers[
                self.radiance_outliers["# id"].isin(cut_IDs)
            ]
            good_cut = self.radiance_good[self.radiance_good["# id"].isin(cut_IDs)]
            outs.append(len(out_cut) * 100 / len(self.radiance_outliers))
            good.append(len(good_cut) * 100 / len(self.radiance_good))

        optimiser = pd.DataFrame(
            np.array((tol, outs, good)).T, columns=["tol", "outs", "good"]
        )
        optimised = optimiser[optimiser["good"] < good_limit]
        best_tol = optimised["tol"][(optimised["outs"] - optimised["good"]).argmax()]

        self.cloud_check_tol = best_tol
        self.cloud_passes = None

        if plot:
            fig, ax = plt.subplots(1, 1, figsize=(6, 4), dpi=150)
            ax.plot(tol, outs, label="Outliers", color="r", linestyle="solid")
            ax.plot(tol, good, label="Good Data", color="r", linestyle="dotted")
            ax.set_xlabel("Tolerance")
            ax.set_ylabel("Percentage of Data Removed")
            ax.set_title("Cloud Check Tolerance Analysis for 550nm")
            ax.legend()
            plt.show()

            fig, ax = plt.subplots(1, 1, figsize=(6, 4), dpi=150)
            ax.plot(tol, np.array(outs) - np.array(good), color="r", linestyle="solid")
            ax.set_xlabel("Tolerance")
            ax.set_ylabel("Percentage of Data Removed")
            ax.set_title("Cloud Check Tolerance Analysis for 550nm")
            plt.show()

    def mask(self, data_type):

        if data_type == "good":
            data = self.radiance_good
        elif data_type == "outliers":
            data = self.radiance_outliers
        elif data_type == "labelled":
            data = self.labelled_radiance
        else:
            print("data not masked")
            quit()

        mask1 = np.where(
            ((data[" vza"] < 6) & (data[" saa"] < 90) & (data[" sza"] < 5))
        )[0]

        mask11 = np.where(
            (
                (data[" vza"] < 6)
                & (data[" saa"] < 90)
                & (data[" saa"] > 30)
                & (data[" sza"] < 14)
            )
        )[0]

        mask12 = np.where(
            (
                (data[" vza"] < 6)
                & (data[" saa"] < 90)
                & (data[" saa"] > 60)
                & (data[" sza"] < 20)
                & (data[" sza"] > 14)
            )
        )[0]

        mask13 = np.where(
            (
                (data[" vza"] < 6)
                & (data[" saa"] < 90)
                & (data[" saa"] > 60)
                & (data[" sza"] < 26)
                & (data[" sza"] > 22)
            )
        )[0]

        mask14 = np.where(
            (
                (data[" vza"] < 6)
                & (data[" saa"] < 110)
                & (data[" saa"] > 70)
                & (data[" sza"] > 53)
            )
        )[0]

        mask2 = np.where(
            (
                (data[" vza"] < 6)
                & (data[" saa"] < 320)
                & (data[" saa"] > 260)
                & (data[" sza"] < 20)
            )
        )[0]

        mask3 = np.where(data[" vza"] < 1)[0]

        mask4 = np.where(
            (
                (data[" vza"] > 45)
                & (data[" saa"] < 264)
                & (data[" saa"] > 254)
                & (data[" sza"] > 50)
            )
        )[0]

        # mask5 = np.where(((data[' vza'] > 45) & (data['raa'] < 230) & (data['raa'] > 210) & (data[' sza'] > 65)))[0] #i think same data as 14 in v3

        mask = np.unique(
            np.hstack((mask1, mask11, mask12, mask13, mask14, mask2, mask3, mask4))
        )

        if data_type == "good":
            self.radiance_good = data.loc[~data.index.isin(mask)]
        elif data_type == "outliers":
            self.radiance_outliers = data.loc[~data.index.isin(mask)]
        elif data_type == "labelled":
            for x in self.labelled_radiance["post_processing_flags"][mask]:
                x.append(7)
        else:
            print("data not masked")


def pipeline(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit):
    print("Initial", len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print("Maintenance", len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print("SZA", len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print("RAA", len(dataset.radiance))
    dataset.clean_irr()
    print("IRR Flags", len(dataset.radiance))
    dataset.cloud_check(0.9, 550, False)
    dataset.plane_fitter()
    dataset.size("good")
    dataset.size("outliers")
    dataset.cloud_check(0.9, 550, True, rewrite_var="good")
    dataset.cloud_check(0.9, 550, True, rewrite_var="outliers")
    dataset.size("good")
    dataset.size("outliers")
    # dataset.save('good', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv1_processed_good.csv')
    # dataset.save('outliers', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv1_processed_out.csv')
    dataset.mask("good")
    dataset.mask("outliers")
    dataset.size("good")
    dataset.size("outliers")
    # dataset.save('good', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv3_processed1_good.csv')
    # dataset.save('outliers', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv3_processed1_out.csv')


def tolerance_analysis(
    dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit
):
    # inital checks
    dataset.maintenance_check(maintenance)
    dataset.sza_check(sza_limit)
    dataset.raa_cut(raa_limit)
    dataset.clean_irr()
    # inital outlier definition
    dataset.plane_fitter()
    # sparse tolerance analysis
    dataset.tol_optimiser(0.4, 1.1, 0.1, 550, 100, True)
    # use best tolerance to define planes
    dataset.cloud_check(dataset.cloud_check_tol, 550, False)
    dataset.plane_fitter()
    # in depth tolerance analysis
    dataset.tol_optimiser(
        dataset.cloud_check_tol - 0.1,
        dataset.cloud_check_tol + 0.1,
        0.01,
        550,
        10,
        True,
    )
    # use best tolerance to define planes
    dataset.cloud_check(dataset.cloud_check_tol, 550, False)
    dataset.plane_fitter()
    dataset.plane_fitter(True)
    dataset.size("good")
    dataset.size("outliers")
    # cloud check final definition of data
    dataset.cloud_check(dataset.cloud_check_tol, 550, True, rewrite_var="good")
    dataset.cloud_check(dataset.cloud_check_tol, 550, True, rewrite_var="outliers")
    dataset.cloud_check(dataset.cloud_check_tol, 550, True, rewrite_var="labels")
    print(dataset.cloud_check_tol)
    dataset.size("good")
    dataset.size("outliers")

def JSIT_pipeline(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))

    dataset.cloud_check(0.9, 550, True, 'radiance')
    dataset.save('radiance', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\JSIT_initial_cc9.csv')

def multi_aod_tolerance_analysis(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit):
    #inital checks
    dataset.maintenance_check(maintenance)
    dataset.sza_check(sza_limit)
    dataset.raa_cut(raa_limit)
    dataset.clean_irr()

def new_plane_pipeline(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit, misalign_vza, misalign_vaa,
                       multiple_periods = False, period_date = None, fit_method = 'plane_fit'):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))
    dataset.misalignment_correction(misalign_vza, misalign_vaa, multiple_periods, period_date)
    dataset.cloud_check(0.9, 550, None)
    print('Cloud Check', len(dataset.cc_radiance))
    dataset.new_plane_fitter(plot = True, method = fit_method)
    print('1st Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.new_plane_fitter(first_iteration = False, plot = True, method = fit_method)
    print('2nd Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.new_plane_fitter(first_iteration = False, plot = True, method = fit_method)
    print('3rd Iteration')
    dataset.size('good')
    dataset.size('outliers')

def irradiance_analysis_writer(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit, filename, wvs):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))
    dataset.write_irr_analysis_files(filename, wvs)
    print('File Written')


QC = PostProcessingDataset(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_v3_None_None_None_None.csv',
                           r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/GHNAv3_irradiance.csv',
                           r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/irradiance/',
                           'GHNA',
                           '0.1')

GHNA_maintenance_dates = [
    "20231016",
    "20231017",
    "20231018",
    "20231019",
    "20231020",
    "20231021",
    "20231022",
    "20231023",
    "20231024",
    "20231025",
    "20240513",
    "20240514",
    "20240515",
    "20240516",
    "20240517",
    "20240518",
    "20240519",
    "20240520",
]

JSIT_maintenance_dates = []



new_plane_pipeline(QC, GHNA_maintenance_dates, 70, 10, (1.76, 1.59), (-80, -77),
                   True, '20240521', 'bounds')


#irradiance_analysis_writer(QC, GHNA_maintenance_dates, 70, 10,
                           #'irradiance_GHNA_v1_analysis',
                         #  [415,490,550,675,740,765,870,1020,1230,1640])


