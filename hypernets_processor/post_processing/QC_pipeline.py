import numpy as np
import pandas as pd
import xarray as xr
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os
from scipy.stats import binned_statistic_2d
from scipy.ndimage import gaussian_filter
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator
import math
import datetime
import matplotlib
import glob

wav_df = xr.open_dataset(
    r"T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\14\SEQ20240314T070025\HYPERNETS_L_GHNA_L1B_IRR_20240314T0700_20240416T1138_v2.0.nc"
)
wav = wav_df.wavelength.values

root = 'T:/ECO/EOServer/'
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

def sza_vza_bin_and_calc(data,cutting_data, stat, bound, input_data = None, input_wav = '550'):
    sza = data[' sza'].values
    vza = data[' vza'].values
    refl = data[f' refl_{input_wav}nm'].values
    cutting_refl = cutting_data[f' refl_{input_wav}nm'].values
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
    elif stat == 'count':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, 'count', bins, expand_binnumbers=True)
    elif stat == 'std':
        binned_data, x, y, b = binned_statistic_2d(sza, vza, refl, 'std', bins, expand_binnumbers=True)
    elif stat == 'median_plus_3std':
        binned_std, x, y, b = binned_statistic_2d(sza, vza, refl, 'std', bins, expand_binnumbers=True)
        binned_median, x, y, b = binned_statistic_2d(sza, vza, refl, 'median', bins, expand_binnumbers=True)
        binned_data = binned_median + 3*binned_std
    elif stat == 'median_minus_3std':
        binned_std, x, y, b = binned_statistic_2d(sza, vza, refl, 'std', bins, expand_binnumbers=True)
        binned_median, x, y, b = binned_statistic_2d(sza, vza, refl, 'median', bins, expand_binnumbers=True)
        binned_data = binned_median - 3*binned_std
    else:
        print('stat not supported')
        binned_data, x, y, b = None, None, None, None

    if input_data is not None:
        binned_data = input_data

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

    return refl_output, sza_output, vza_output, bound_passes, binned_data

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

def linear_plane(xy, a, b, c):
    x, y = xy
    return a + b*x + c*y

def cubic_plane(xy, a, b, c, d, e, f, g, h, i, j):
    x, y = xy
    return a + b*x + c*y + d*x**2 + e*y**2 + f*x*y + g*x**3 + h*y**3 + i*x*y**2 + j*y*x**2


def plane_fit_and_plot(data, data_setting, stds, plot = True, raa_bin = None, iteration = 0, input_wav = '550'):
    x = data[" sza"].values
    y = data[" vza"].values
    z = data[f' refl_{input_wav}nm'].values

    popt, pcov = curve_fit(quad_plane, (x, y), z)
    below = popt - stds * np.sqrt(np.diag(pcov))
    above = popt + stds * np.sqrt(np.diag(pcov))

    z_below = (
        quad_plane((data_setting[" sza"].values, data_setting[" vza"].values), *below)
        #- data_setting[" refl_550nm"].values * 0.05
    )
    z_above = (
        quad_plane((data_setting[" sza"].values, data_setting[" vza"].values), *above)
        #+ data_setting[" refl_550nm"].values * 0.05
    )

    outliers = data_setting[
        (data_setting[f' refl_{input_wav}nm'] > z_above)
        | (data_setting[f' refl_{input_wav}nm'] < z_below)
    ]
    good_data = data_setting[
        (data_setting[f' refl_{input_wav}nm'] < z_above)
        & (data_setting[f' refl_{input_wav}nm'] > z_below)
    ]
    good_data.reset_index(drop=True, inplace=True)
    outliers.reset_index(drop=True, inplace=True)

    if plot:
        x_range = np.linspace(0, 61, 1000)
        y_range = np.linspace(0, 61, 1000)
        X, Y = np.meshgrid(x_range, y_range)
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        ax.scatter(
            data_setting[" sza"].values,
            data_setting[" vza"].values,
            data_setting[" refl_550nm"].values,
        )

       

        
        Z = quad_plane((X, Y), *popt)
        Z_below = quad_plane((X, Y), *below)
        Z_above = quad_plane((X, Y), *above)

        ax.plot_surface(X, Y, Z, alpha=0.5)
        ax.plot_surface(X, Y, Z_above, alpha=0.5)
        ax.plot_surface(X, Y, Z_below, alpha=0.5)

        ax.set_xlabel("SZA")
        ax.set_ylabel("VZA")
        ax.set_zlabel("Reflectance")
        # fig.savefig(results_path + title)
        plt.show()
        '''

        fig, axs = plt.subplots(1, 3, figsize=(6, 4), sharey=True)
        for i in range(3):
            axs[i].plot(Y, quad_plane(((i + 1) * 20, Y), *popt), color="black", alpha = 0.1)
            axs[i].plot(
                Y, quad_plane(((i + 1) * 20, Y), *below), color="black"
            )
            axs[i].plot(
                Y, quad_plane(((i + 1) * 20, Y), *above), color="black"
            )
            axs[i].set_title(f"SZA = {(i+1)*20}")
            axs[i].scatter(
                data_setting[
                    data_setting[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][" vza"].values,
                data_setting[
                    data_setting[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][f' refl_{input_wav}nm'].values,
                color="black",
                s=5,
            )
            axs[i].scatter(
                good_data[
                    good_data[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][" vza"].values,
                good_data[
                    good_data[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][f' refl_{input_wav}nm'].values,
                color="green",
                s=5,
            )
            axs[i].scatter(
                outliers[
                    outliers[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][" vza"].values,
                outliers[
                    outliers[" sza"].between((i + 1) * 20 - 1, (i + 1) * 20 + 1)
                ][f' refl_{input_wav}nm'].values,
                color="red",
                s=5,
            )
            axs[i].set_xlabel("VZA")
            axs[0].set_ylabel("Reflectance")
            fig.suptitle(raa_bin)
            fig.savefig(r'T:/ECO/EOServer/joe/hypernets_plots/plane_models/' + f'sza_slices_plane_{raa_bin}_{iteration}.png')
            plt.close()

    return outliers, good_data

def new_plane_fit(input_sza, input_vza, input_refl, plane_type = 'quad', count = None):
    x = input_sza
    y = input_vza
    z = input_refl

    if plane_type == 'quad':
        popt, pcov = curve_fit(quad_plane, (x, y), z, nan_policy = 'omit', sigma = count)
    elif plane_type == 'linear':
        popt, pcov = curve_fit(linear_plane, (x, y), z, nan_policy='omit', sigma=count)
    elif plane_type == 'cubic':
        popt, pcov = curve_fit(cubic_plane, (x, y), z, nan_policy='omit', sigma = count)

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
    return (direct_to_diffuse+1) / (new_direct_to_diffuse+1)


class PostProcessingDataset:

    def __init__(self, rad_path, irr_path, clear_sky_path, site, period_name = None, clear_sky_aod = None, input_wav = '550'):

        # read in radiance
        data = pd.read_csv(rad_path)
        # define raa
        data.loc[:, "raa"] = (data.loc[:, " vaa"] - data.loc[:, " saa"] + 360) % 360
        # extract dates and times
        dates = []
        times = []
        datetimes = []
        for i in range(len(data)):
            date = data["# id"][i][3:11]
            time = data["# id"][i][12:16]
            dates.append(date)
            times.append(time)
            datetimes.append(datetime.datetime.strptime(date + ':' + time, '%Y%m%d:%H%M'))
        dt_data = data.assign(date=dates, time=times, datetimes = datetimes)
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
        if period_name is None:
            self.period_name = site
        else:
            self.period_name = period_name
        self.cc_radiance = None
        self.radiance_good = None
        self.radiance_outliers = None
        self.cloud_passes = None
        self.cloud_check_tol = None
        self.clear_sky_path = clear_sky_path
        self.bound_iteration = 0
        self.plane_iteration = 0
        self.input_wav = input_wav
        if clear_sky_aod is None:
            self.clear_sky_list = compile_irradiance_list(clear_sky_path, site)
            self.clear_sky_aod = None
            self.clear_sky_model = None
        else:
            self.clear_sky_list = None
            self.clear_sky_aod = clear_sky_aod
            if self.clear_sky_aod == 'median':
                self.clear_sky_model = xr.open_dataset(
                    "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_medianaod.nc".format(
                        site, clear_sky_aod))
            else:
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

    def calculate_ndvi(self):
        self.radiance['ndvi'] = ((self.radiance[' refl_842nm'] - self.radiance[' refl_665nm'])/
                                 (self.radiance[' refl_842nm'] + self.radiance[' refl_665nm']))

    def calculate_savi(self):
        self.radiance['savi'] = ((self.radiance[' refl_842nm'] - self.radiance[' refl_665nm']) /
                                 (self.radiance[' refl_842nm'] + self.radiance[' refl_665nm'] + 0.5)) * 1.5

    def calculate_s2tci(self):
        self.radiance['s2tci'] = ((self.radiance[' refl_740nm'] - self.radiance[' refl_705nm']) /
                                 (self.radiance[' refl_705nm'] - self.radiance[' refl_665nm']))

    def split_by_date(self, start_date, end_date):
        self.radiance['datetime'] = [datetime.datetime.strptime(x, '%Y%m%d') for x in self.radiance.date]
        self.radiance = self.radiance[
            ((self.radiance.datetime < pd.Timestamp(end_date)) &
             (self.radiance.datetime >= pd.Timestamp(start_date)))]

    def count_by_bin(self):
        bins = [0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5]
        bin_centers = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

        good_count, sza, vza, b, n = sza_vza_bin_and_calc(self.radiance_good, self.radiance_good, 'count', 'na', input_wav = self.input_wav)
        out_count, out_sza, out_vza, out_b, out_n = sza_vza_bin_and_calc(self.radiance_outliers, self.radiance_outliers, 'count', 'na', input_wav = self.input_wav)
        percentage_removed = np.true_divide(np.array(out_count),(np.array(out_count) + np.array(good_count))) * 100

        fig, ax = plt.subplots(1, 1, figsize=(5, 6))
        img = ax.imshow(percentage_removed.reshape(15,15), origin = 'lower', extent = [0,75,0,75])
        ax.set_xticks(bin_centers)
        ax.set_yticks(bin_centers)
        ax.set_ylabel('SZA')
        ax.set_xlabel('VZA')
        fig.colorbar(img)
        #plt.show()

    def basic_outlier_definition(self):
        mean = self.radiance[f' refl_{self.input_wav}nm'].mean()
        stde = self.radiance[f' refl_{self.input_wav}nm'].std()
        max_range = mean + (stde * 3)
        min_range = mean - (stde * 3)
        outliers = self.radiance[
            (self.radiance[f' refl_{self.input_wav}nm'] > max_range)
            | (self.radiance[f' refl_{self.input_wav}nm'] < min_range)
        ]
        good_data = self.radiance[
            (self.radiance[f' refl_{self.input_wav}nm'] < max_range)
            & (self.radiance[f' refl_{self.input_wav}nm'] > min_range)
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

    def vza_check(self, vza_limit):
        bad_inds = []
        for i in range(len(self.radiance)):
            vza = self.radiance[" vza"][i]
            if vza < vza_limit:
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

        for x in self.labelled_radiance["post_processing_flags"].loc[
            self.labelled_radiance[" vza"] < vza_limit
        ]:
            x.append(999)

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
            if (flags.values[i] & 773892) != 0:
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

    def append_aod(self):
        if self.site == 'GHNA':
            aod_path = r'T:/ECO/EOServer/data/insitu/radcalnet/RadCalNet-All-Sites-Feb2025/GONA/'
            dates = [x[3:11] for x in self.irradiance['ID'].values]
            years = [x[0:4] for x in dates]
            doy = [datetime.date(int(x[0:4]), int(x[4:6]), int(x[6:8])).timetuple().tm_yday for x in dates]
            aod_files = [aod_path + f'GONA01_{years[i]}_{doy[i]}_v00.09.input' for i in range(len(dates))]
            aods = []
            for path in aod_files:
                try:
                    f = open(path, 'r')
                    datafile = f.readlines()
                    row = [i for i, s in enumerate(datafile) if "AOD:\t" in s][0]
                    aod = np.mean([float(i.rstrip()) for i in datafile[row].split("\t")[1::] if i.rstrip() != ""])
                    aods.append(aod)
                except:
                    aods.append(np.nan)

            for i, v in enumerate(aods):
                if aods[i] > 10:
                    aods[i] = np.nan

            self.irradiance['aod'] = aods

    def misalignment_correction(self, vza, vaa, mean_corr, multiple_periods = False, period_date = None):
        szas = self.radiance[' sza']
        saas = self.radiance[' saa']
        data = np.zeros((self.irradiance.shape[0], len(self.irradiance.columns) - 6))
        wav_list = [int(''.join(filter(str.isdigit, s))) for s in self.radiance.keys() if 'refl' in s]

        for wv in wav_list:
            dir_to_diff = np.zeros(self.radiance.shape[0])

            for i in range(dir_to_diff.shape[0]):
                dir_to_diff[i] = find_nearest_to_wav(
                    modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'direct_to_diffuse_irradiance_ratio'),
                    wav, wv)

            if not multiple_periods:
                self.radiance[f' refl_{wv}nm'] = self.radiance[f' refl_{wv}nm'] * ratio_calculator(vza, vaa, szas, saas, dir_to_diff)/mean_corr
            else:
                divider_idx = np.min(np.argwhere(self.radiance['date'] == period_date))
                self.radiance[f' refl_{wv}nm'][:divider_idx] = (
                        self.radiance[f' refl_{wv}nm'][:divider_idx] *
                        ratio_calculator(vza[0], vaa[0], szas[:divider_idx], saas[:divider_idx],
                                         dir_to_diff[:divider_idx]))/mean_corr[0]
                self.radiance[f' refl_{wv}nm'][divider_idx:] = (
                        self.radiance[f' refl_{wv}nm'][divider_idx:] *
                        ratio_calculator(vza[1], vaa[1], szas[divider_idx:], saas[divider_idx:],
                                         dir_to_diff[divider_idx:]))/mean_corr[1]


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
            #np.savetxt(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\irradiance_GHNA_v1_diffs.csv',output_data, fmt = '%s',delimiter=',')

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


    def write_irr_analysis_files(self, filename, wavelengths, save = True, plot = False, interp = False):
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
        if interp:
            output_data['AOD'] = self.irradiance['aod']

        for wv in wavelengths:
            model = np.zeros(output_data.shape[0])
            observ = np.zeros(output_data.shape[0])
            dir_to_diff = np.zeros(output_data.shape[0])

            for i in range(output_data.shape[0]):
                if not interp:
                    model[i] = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'solar_irradiance_BOA'),
                                                   wav, wv)
                else:
                    aod_0 = find_nearest_to_wav(
                        modelled_data_read_and_interp(szas[i],
                                                      xr.open_dataset(
                                                          "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_aod{}.nc".format(
                                                              self.site, '0.0')),
                                                      'solar_irradiance_BOA'),
                        wav, wv)
                    aod_1 = find_nearest_to_wav(
                        modelled_data_read_and_interp(szas[i],
                                                      xr.open_dataset(
                                                          "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_aod{}.nc".format(
                                                              self.site, '0.1')),
                                                      'solar_irradiance_BOA'),
                        wav, wv)
                    aod_2 = find_nearest_to_wav(
                        modelled_data_read_and_interp(szas[i],
                                                      xr.open_dataset(
                                                          "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_aod{}.nc".format(
                                                              self.site, '0.2')),
                                                      'solar_irradiance_BOA'),
                        wav, wv)
                    aod_3 = find_nearest_to_wav(
                        modelled_data_read_and_interp(szas[i],
                                                      xr.open_dataset(
                                                          "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_aod{}.nc".format(
                                                              self.site, '0.3')),
                                                      'solar_irradiance_BOA'),
                        wav, wv)

                    mod_arr = [aod_0, aod_1, aod_2, aod_3]
                    mod_aod = [0, 0.1, 0.2, 0.3]
                    model[i] = np.interp(output_data['AOD'][i], mod_aod, mod_arr)


                observ[i] = find_nearest_to_wav(data[i, :], wav, wv)
                dir_to_diff[i] = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], self.clear_sky_model, 'direct_to_diffuse_irradiance_ratio'),
                                                     wav, wv)

            output_data[f'model_{wv}nm'] = model
            output_data[f'obs_{wv}nm'] = observ
            output_data[f'dir_diff_ratio_{wv}nm'] = dir_to_diff
            output_data[f'ratio_{wv}nm'] = model/observ

            if plot:
                fig, ax = plt.subplots(1, 1, )
                ax.scatter(output_data['AOD'], model/observ)
                fig.savefig(r'T:\ECO\EOServer\joe\hypernets_plots\aod_plots\{}_aod_ratio_interpolated_{}.png'.format(self.period_name, wv))


        if save:
            output_data = output_data[output_data['IDs'].isin(self.radiance['# id'])]
            output_data.to_csv(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\{}.csv'.format(filename))

    def plane_fitter(self, labelled = False, plot = False):

        if self.cc_radiance is None:
            self.cc_radiance = self.radiance

        # define datasets
        #data = self.cc_radiance
        data = self.radiance_good
        self.plane_iteration += 1

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
        raa_limits_list = ['30_90', '90_150', '150_210', '210_270', '270_330', '330_30']

        outs, good = plane_fit_and_plot(data_list[0], data_unmasked_list[0], 3, plot, raa_limits_list[0], self.plane_iteration)
        for i in range(len(data_list) - 1):
            outs = pd.concat(
                [
                    outs,
                    plane_fit_and_plot(data_list[i + 1], data_unmasked_list[i + 1], 3, plot, raa_limits_list[i+1], self.plane_iteration)[
                        0
                    ],
                ],
                ignore_index=True,
            )
            good = pd.concat(
                [
                    good,
                    plane_fit_and_plot(data_list[i + 1], data_unmasked_list[i + 1], 3, plot, raa_limits_list[i+1], self.plane_iteration)[
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

    def new_plane_fitter(self, labelled = False, first_iteration = True,
                         plot = False, method = 'plane_fit', save_bounds = False, nc_path = None,
                         last_iteration = False):



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

        raa_limits_list = ['30_90', '90_150', '150_210', '210_270', '270_330', '330_30']

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
        ds_dict = {}
        for i in range(len(data_list)):
            data_cutting = data_unmasked_list[i]

            if len(data_list[i]) == 0:
                continue

            bins = [0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5]
            bin_cents = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

            if method == 'plane_fit':

                binned95, bin_centers_sza, bin_centers_vza, upper_passes, da = sza_vza_bin_and_calc(data_list[i],
                                                                                                    data_cutting,
                                                                                                    '3sigma_max',
                                                                                                    'upper',
                                                                                                    input_wav = self.input_wav)
                binned5, bin_centers_sza, bin_centers_vza, lower_passes, da = sza_vza_bin_and_calc(data_list[i],
                                                                                                   data_cutting,
                                                                                                   '3sigma_min',
                                                                                                   'lower',
                                                                                                   input_wav = self.input_wav)

                below, below_cov = new_plane_fit(bin_centers_sza, bin_centers_vza, binned5)
                above, above_cov = new_plane_fit(bin_centers_sza, bin_centers_vza, binned95)
                z_lower = quad_plane((data_cutting[' sza'].values, data_cutting[' vza'].values),
                                     *below)
                z_upper = quad_plane((data_cutting[' sza'].values, data_cutting[' vza'].values),
                                     *above)

                outliers = data_cutting[(data_cutting[f' refl_{self.input_wav}nm'] > z_upper) |
                                        (data_cutting[f' refl_{self.input_wav}nm'] < z_lower)]
                good_data = data_cutting[(data_cutting[f' refl_{self.input_wav}nm'] < z_upper) &
                                        (data_cutting[f' refl_{self.input_wav}nm'] > z_lower)]

            elif method == 'bounds':
                if i == 0:
                    self.bound_iteration += 1
                    iter_num = self.bound_iteration


                binned95, bin_centers_sza, bin_centers_vza, upper_passes, da = sza_vza_bin_and_calc(data_list[i],
                                                                                                    data_cutting,
                                                                                                    'median_plus_3std',
                                                                                                    'upper',
                                                                                                    input_wav = self.input_wav)
                binned5, bin_centers_sza, bin_centers_vza, lower_passes, da = sza_vza_bin_and_calc(data_list[i],
                                                                                                   data_cutting,
                                                                                                   'median_minus_3std',
                                                                                                   'lower',
                                                                                                   input_wav = self.input_wav)




                below, below_cov = new_plane_fit(bin_centers_sza, bin_centers_vza, binned5)
                above, above_cov = new_plane_fit(bin_centers_sza, bin_centers_vza, binned95)

                df_below = pd.DataFrame({'refl': binned5, 'vza': bin_centers_vza, 'sza': bin_centers_sza})
                df_above = pd.DataFrame({'refl': binned95, 'vza': bin_centers_vza, 'sza': bin_centers_sza})

                passes = [True if v is True and lower_passes[i] is True else False for i, v in enumerate(upper_passes)]
                good_data = data_cutting[passes]
                outliers = data_cutting[[not el for el in passes]]
                if save_bounds:
                    df_both = df_below.rename(columns={'refl': 'lower_bound'})
                    df_both = df_below.assign(upper_bound = df_above['refl'].values)
                    ds_dict[f'{raa_limits_list[i]}'] = df_both

            elif method =='plane_std_fit':
                if i == 0:
                    self.plane_iteration += 1
                    iter_num = self.plane_iteration
                std_flat, bin_centers_sza, bin_centers_vza, lower_passes, stds = sza_vza_bin_and_calc(data_list[i],
                                                                                               data_cutting,
                                                                                               'std', 'na',
                                                                                                      input_wav = self.input_wav)

                med_flat, bin_centers_sza, bin_centers_vza, lower_passes, medians = sza_vza_bin_and_calc(data_list[i],
                                                                                                         data_cutting,
                                                                                                         'median', 'na',
                                                                                                         input_wav = self.input_wav)

                count_flat, bin_centers_sza, bin_centers_vza, lower_passes, counts = sza_vza_bin_and_calc(data_list[i],
                                                                                                          data_cutting,
                                                                                                          'count', 'na',
                                                                                                          input_wav = self.input_wav)

                sza_fit = []
                vza_fit = []
                std_fit = []
                med_fit = []
                cnt_fit = []

                for j, cn in enumerate(count_flat):
                    if ((bin_centers_vza[j] <= 5 and cn < 50) or
                            math.isnan(medians.flatten()[j]) or
                            (bin_centers_vza[j] >= 55 and cn < 50) or
                            (math.isnan(stds.flatten()[j])) or
                            cn < 3):
                        continue
                    else:
                        sza_fit.append(bin_centers_sza[j])
                        vza_fit.append(bin_centers_vza[j])
                        std_fit.append(stds.flatten()[j])
                        med_fit.append(medians.flatten()[j])
                        cnt_fit.append(1/counts.flatten()[j])

                if len(med_fit) < 6:
                    print('Too few points to fit use bounds only')
                    continue

                max_sza = np.ceil(max(data_cutting[' sza'].values))
                max_vza = np.ceil(max(data_cutting[' vza'].values))
                max_sza_idx = np.abs(bin_cents - max_sza).argmin() + 1
                max_vza_idx = np.abs(bin_cents - max_vza).argmin() + 1

                min_sza = np.floor(min(data_cutting[' sza'].values))
                min_vza = np.floor(min(data_cutting[' vza'].values))
                min_sza_idx = np.abs(bin_cents - min_sza).argmin()
                min_vza_idx = np.abs(bin_cents - min_vza).argmin()

                if self.site == 'GHNA':
                    std_coeffs, std_cov = new_plane_fit(sza_fit, vza_fit, std_fit, plane_type = 'quad', )#count = cnt_fit)
                    sza, vza = np.meshgrid(bin_cents[min_sza_idx:max_sza_idx], bin_cents[min_vza_idx:max_vza_idx])
                    plane_std = quad_plane((sza, vza), *std_coeffs)
                    med_coeffs, med_cov = new_plane_fit(sza_fit, vza_fit, med_fit, )  # count = cnt_fit)
                    plane_med = quad_plane((sza, vza), *med_coeffs)
                elif self.period_name == 'WWUKv3':
                    std_coeffs, std_cov = new_plane_fit(sza_fit, vza_fit, std_fit, plane_type='quad')#, count = cnt_fit)
                    sza, vza = np.meshgrid(bin_cents[min_sza_idx:max_sza_idx], bin_cents[min_vza_idx:max_vza_idx])
                    plane_std = quad_plane((sza, vza), *std_coeffs)
                    med_coeffs, med_cov = new_plane_fit(sza_fit, vza_fit, med_fit, plane_type = 'quad')#, count = cnt_fit)
                    plane_med = quad_plane((sza, vza), *med_coeffs)
                else:
                    std_coeffs, std_cov = new_plane_fit(sza_fit, vza_fit, std_fit, plane_type='quad',)# count = cnt_fit)
                    sza, vza = np.meshgrid(bin_cents[min_sza_idx:max_sza_idx], bin_cents[min_vza_idx:max_vza_idx])
                    plane_std = quad_plane((sza, vza), *std_coeffs)
                    med_coeffs, med_cov = new_plane_fit(sza_fit, vza_fit, med_fit, )  # count = cnt_fit)
                    plane_med = quad_plane((sza, vza), *med_coeffs)

                plane_std[plane_std < 0] = 0
                plane_med[plane_med < 0] = 0
                plane_std = np.where(plane_std < 0.03*plane_med, 0.03*plane_med, plane_std)
                plane_std[plane_std <= 0] = gaussian_filter(plane_std, 1)[plane_std <= 0]

                upper_bounds = plane_med + 3*plane_std
                lower_bounds = plane_med - 3*plane_std


                sza = np.pad(sza, 1, 'edge')
                sza[:,0] = 0
                sza[:,-1] = sza[:,-2] + 5

                vza = np.pad(vza, 1, 'edge')
                vza[0, :] = 0
                vza[-1, :] = vza[-2, :] + 5

                upper_bounds = np.pad(upper_bounds, 1, 'edge')
                lower_bounds = np.pad(lower_bounds, 1, 'edge')

                upper_bounds = upper_bounds.flatten()[~np.isnan(upper_bounds.flatten())]
                lower_bounds = lower_bounds.flatten()[~np.isnan(lower_bounds.flatten())]

                lower_bounds[lower_bounds < 0] = 0
                upper_bounds = np.where(lower_bounds >= upper_bounds,
                                        lower_bounds + 0.03*np.mean(plane_med),
                                        upper_bounds)

                df_below = pd.DataFrame({'refl': lower_bounds, 'vza': vza.flatten(), 'sza': sza.flatten()})
                df_above = pd.DataFrame({'refl': upper_bounds, 'vza': vza.flatten(), 'sza': sza.flatten()})

                lower_interp = LinearNDInterpolator((sza.flatten(), vza.flatten()), lower_bounds)
                lower_passes = [True if v > lower_interp(data_cutting[' sza'], data_cutting[' vza'])[i] else False for i, v in
                                enumerate(data_cutting[f' refl_{self.input_wav}nm'])]

                upper_interp = LinearNDInterpolator((sza.flatten(), vza.flatten()), upper_bounds)
                upper_passes = [True if v < upper_interp(data_cutting[' sza'], data_cutting[' vza'])[i] else False for
                                i, v in
                                enumerate(data_cutting[f' refl_{self.input_wav}nm'])]

                passes = [True if v is True and lower_passes[i] is True else False for i, v in enumerate(upper_passes)]
                good_data = data_cutting[passes]
                outliers = data_cutting[[not el for el in passes]]
                if save_bounds:
                    df_both = df_below.rename(columns={'refl': 'lower_bound'})
                    df_both = df_below.assign(upper_bound=df_above['refl'].values)
                    ds_dict[f'{raa_limits_list[i]}'] = df_both
            else:
                print('invalid_method')
                exit()

            good_data.reset_index(drop=True, inplace=True)
            outliers.reset_index(drop=True, inplace=True)

            if plot:
                x_range = np.arange(0, 65, 5)
                fig, axs = plt.subplots(1, 3, figsize=(6, 4), sharey=True)
                for j in range(3):
                    axs[j].set_title(f'SZA = {(j + 1) * 20}')
                    axs[j].scatter(
                        outliers[outliers[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' vza'].values,
                        outliers[outliers[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][f' refl_{self.input_wav}nm'].values,
                        color='red', s=5)
                    axs[j].scatter(
                        good_data[good_data[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' vza'].values,
                        good_data[good_data[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][f' refl_{self.input_wav}nm'].values,
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
                    '''
                    axs[1, j].scatter(
                        df_below.loc[(df_below['sza'] > (j + 1) * 20 - 1) & (df_below['sza'] < (j + 1) * 20 + 1)][
                            'vza'].values,
                        df_below.loc[(df_below['sza'] > (j + 1) * 20 - 1) & (df_below['sza'] < (j + 1) * 20 + 1)][
                            'refl'].values,
                        color='blue', s=20, marker='v')
                    axs[1, j].scatter(
                        df_above.loc[(df_above['sza'] > (j + 1) * 20 - 1) & (df_above['sza'] < (j + 1) * 20 + 1)][
                            'vza'].values,
                        df_above.loc[(df_above['sza'] > (j + 1) * 20 - 1) & (df_above['sza'] < (j + 1) * 20 + 1)][
                            'refl'].values,
                        color='blue', s=20, marker='^')

                    #norm = matplotlib.colors.CenteredNorm()
                    im = axs[1, j].scatter(
                        data_cutting[data_cutting[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' vza'].values,
                        data_cutting[data_cutting[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' refl_550nm'].values,
                        c = data_cutting[data_cutting[' sza'].between((j + 1) * 20 - 1, (j + 1) * 20 + 1)][' vaa'].values,
                        s=5, cmap = 'hsv')
                    cbar = fig.colorbar(im, ax=axs[1,2])
                    cbar.set_label(label='VAA', fontsize=16)

                    '''
                    axs[j].set_xlabel('VZA')
                    axs[0].set_ylabel('Reflectance')
                fig.suptitle('RAA {}'.format(raa_limits_list[i]))
                fig.savefig(r'T:/ECO/EOServer/joe/hypernets_plots/plane_models/' +
                            'sza_slices_3sig_{}_{}_{}_{}.png'.format(raa_limits_list[i], iter_num, method, self.period_name))
                plt.close()
                #plt.show()

            if ('outs' and 'good') not in locals():
                outs = outliers
                good = good_data

            else:
                outs = pd.concat([outs, outliers], ignore_index=True)
                good = pd.concat([good, good_data], ignore_index=True)

        if nc_path is not None:
            ds_raa_list = []
            ds_raa_keys_list = []
            for i, key in enumerate(ds_dict.keys()):
                ds_raa_list.append(xr.Dataset.from_dataframe(ds_dict[key]))
                ds_raa_keys_list.append(key)
                ds_raa_vals_list = [np.mean([float(x) for x in ds_raa_keys_list[i].split('_')]) for i in range(len(ds_raa_keys_list))]
                if '330_30' in ds_raa_keys_list:
                    ds_raa_vals_list[ds_raa_keys_list.index('330_30')] = 0

            comb_ds = xr.concat(ds_raa_list, pd.Index(ds_raa_keys_list, name = 'raa'))
            comb_ds = comb_ds.rename_vars({'refl': 'lower_bound'})
            comb_ds.set_coords(('vza', 'sza'))

            comb_ds.to_netcdf(nc_path)

        if labelled:
            for y in self.labelled_radiance['post_processing_flags'][self.labelled_radiance.apply(tuple, axis = 1).isin([tuple(x) for x in outs.values])]:
                y.append(5)
        else:
            self.radiance_good = good
            self.radiance_outliers = outs

        if last_iteration:
            self.radiance = good

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

    def plot_ndvi_timeseries(self):
        #mask = np.where((self.radiance[' vza'] > 8) &
         #               (self.radiance[' vza'] < 12) &
          #              (self.radiance[' vaa'] < 115) &
           #             (self.radiance[' vaa'] > 96))[0]
        #self.radiance = self.radiance.drop(mask)
        #self.radiance.reset_index(drop = True, inplace = True)
        x = self.radiance.datetimes.values
        y = self.radiance.ndvi.values
        dates = self.radiance['date']
        #summer_dates = [dat for dat in dates if dat[4:6] == '06' or dat[4:6] == '07' or dat[4:6] == '08']
        #summer_y = [v for i, v in enumerate(y) if dates[i] in summer_dates]
        #y_mean = np.nanmean(summer_y)
        #y_std = np.nanstd(summer_y)
        ys = pd.Series(y)
        rolling_mean = ys.rolling(100).mean()
        rolling_std = ys.rolling(100).std()

        fig, ax = plt.subplots(2, 1, figsize = (20, 14))
        ax[0].scatter(x, y, color='g', s=2, alpha=0.7)
        ax[0].plot(x, rolling_mean, color = 'b')
        ax[0].fill_between(x, rolling_mean - rolling_std, rolling_mean + rolling_std, color = 'blue', alpha = 0.2)
        #ax[0].axhline(y_mean, color = 'black')
        #ax[0].axhline(y_mean + y_std, color='red')
        #ax[0].axhline(y_mean - y_std, color='red')
        #ax[0].axhline(y_mean + 2*y_std, color='orange')
        #ax[0].axhline(y_mean - 2*y_std, color='orange')
        #ax[0].axhline(y_mean + 3*y_std, color='yellow')
        #ax[0].axhline(y_mean - 3*y_std, color='yellow')

        ax[1].plot(x, rolling_std)
        #ax[1].axhline(y_std, color='red')
        #ax[1].axhline(2 * y_std, color='orange')
        #ax[1].axhline(3 * y_std, color='yellow')

        ax[0].set_ylabel('NDVI')
        ax[1].set_ylabel('NDVI StD')
        ax[1].set_xlabel('Date')
        ax[0].set_title(f'{self.period_name} NDVI Timeseries')
        plt.gcf().autofmt_xdate()
        fig.savefig(root + f'/joe/hypernets_plots/QC_pipeline_plots/{self.period_name}_ndvi_timeseries')


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
    dataset.new_plane_fitter(plot = True, method = 'bounds')
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

def new_plane_pipeline(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit, misalign_vza, misalign_vaa, mean_corr,
                       multiple_periods = False, period_date = None, fit_method = 'plane_fit',
                       split_by_date = False, start = None, end = None):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    if dataset.site == 'JSIT':
        dataset.vza_check(7)
        print('VZA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))
    dataset.calculate_ndvi()
    dataset.calculate_savi()
    dataset.calculate_s2tci()
    #dataset.save('radiance', r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/WWUK_initalQC.csv')
    if misalign_vza != 0 and misalign_vaa != 0:
        dataset.misalignment_correction(misalign_vza, misalign_vaa, mean_corr, multiple_periods, period_date)
    #dataset.save('radiance', r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_v3_misalignment_corrected.csv')
    dataset.cloud_check(0.9, 550, True, rewrite_var = 'radiance')
    dataset.save('radiance', f'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/{dataset.period_name}_CC.csv')
    print('Cloud Check', len(dataset.radiance))
    if split_by_date is True:
        dataset.split_by_date(start, end)
    dataset.new_plane_fitter(plot = True, method = fit_method)
    print('1st Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.new_plane_fitter(first_iteration = False, plot = True, method = fit_method)
    print('2nd Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.new_plane_fitter(first_iteration = False, plot = True, method = fit_method, last_iteration = True)
    print('3rd Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.save('good', f'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/{dataset.period_name}_bounds_good.csv')
    dataset.save('outliers', f'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/{dataset.period_name}_bounds_out.csv')

    dataset.new_plane_fitter(first_iteration = False, plot = True, method = 'plane_std_fit')
    print('Plane Fit 1st Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.new_plane_fitter(first_iteration = False, plot = True, method = 'plane_std_fit')
    print('Plane Fit 2nd Iteration')
    dataset.size('good')
    dataset.size('outliers')
    dataset.new_plane_fitter(first_iteration = False, plot = True, method = 'plane_std_fit', last_iteration = True,
                             save_bounds=True,
                             nc_path=f'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/bounds/{dataset.period_name}_bounds.nc'
                             )
    print('Plane Fit 3rd Iteration')
    dataset.size('good')
    dataset.size('outliers')
    #dataset.count_by_bin()
    dataset.save('good', f'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/{dataset.period_name}_QC_good.csv')
    dataset.save('outliers', f'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/{dataset.period_name}_QC_out.csv')

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

def aod_plotter(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit, filename, wvs):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))
    dataset.append_aod()
    dataset.write_irr_analysis_files(filename, wvs, save = True, plot = True, interp = True)
    print('Done')

def ndvi_bound_calculator(dataset: PostProcessingDataset, maintenance, sza_limit, raa_limit):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))
    dataset.calculate_ndvi()
    dataset.plot_ndvi_timeseries()

def misalignment_correction_writer(dataset: PostProcessingDataset, vza, vaa, mean_corr,
                                   multiple_periods = False, period_date = None):
    dataset.misalignment_correction(vza, vaa, mean_corr, multiple_periods, period_date)
    dataset.save('radiance',
                 r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_2023-10-26_present_None_None_None_None_misalign_corrected.csv')

JSIT_dict = {'NovDec24Jan25': ('2024-11-14', '2025-01-31'),
             'FebApr25': ('2025-02-01', '2025-04-30')}

JSIT_maintenance_dates = []
'''
for k, v in JSIT_dict.items():
    QC = PostProcessingDataset(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/LOBE_2023-05-31_2023-08-11_None_None_None_None_misalign_corrected.csv',
                            r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/LOBEv1_irradiance.csv',
                            r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/irradiance/',
                            'LOBE',
                            f'JSIT_{k}',
                            '0.1')

    new_plane_pipeline(QC, JSIT_maintenance_dates, 70, 10, 0.78, 176.9, False,
                     fit_method = 'bounds', split_by_date = True, start = v[0], end = v[1])
'''
QC = PostProcessingDataset(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_2023-10-26_present_None_None_None_None.csv',
                            r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/GHNAv3_irradiance.csv',
                            r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/irradiance/',
                            'GHNA',
                            f'GHNA_Oct23_May24',
                            'median',
                           '550')
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


WWUK_maintenance_dates = []
JAES_maintenance_dates = []
LOBE_maintenance_dates = []

#ndvi_bound_calculator(QC, LOBE_maintenance_dates, 60, 10)
misalignment_correction_writer(QC,  (1.96, 1.28), (-72.2, -36.4), (1.009, 1.011), True, '20240521')

QC = PostProcessingDataset(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_2023-10-26_present_None_None_None_None_misalign_corrected.csv',
                            r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/GHNAv3_irradiance.csv',
                            r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/irradiance/',
                            'GHNA',
                            f'GHNA_Oct23_May24',
                            'median',
                           '550')

new_plane_pipeline(QC, GHNA_maintenance_dates, 60, 10, 0, #(1.76,1.59),
                   0,# (-80, -77),
                   0,
                   False,
                   split_by_date = True, start = '20231026', end = '20240521',
                   fit_method = 'bounds')
QC.period_name = f'GHNA_May24_Aug25'
new_plane_pipeline(QC, GHNA_maintenance_dates, 60, 10, 0, #(1.76,1.59),
                   0,# (-80, -77),
                   0,
                   False,
                   split_by_date = True, start = '20240521', end = '20250801',
                   fit_method = 'bounds')


#new_plane_pipeline(QC, JSIT_maintenance_dates, 70, 10, 0.78, 176.9, False,
                 #  fit_method = 'bounds')

#new_plane_pipeline(QC, GHNA_maintenance_dates, 60, 10,
 #                  1.01,
  #                 96.7,
   #                0.996,
    #               False,
     #              fit_method = 'bounds')

#new_plane_pipeline(QC, WWUK_maintenance_dates, 70, 10, 0.93, 24.8, False,
      #             fit_method = 'bounds')

#irradiance_analysis_writer(QC, LOBE_maintenance_dates, 60, 10,
 #                          'irradiance_LOBEv4_analysis',
  #                       [415, 490, 550, 665, 675, 705, 740, 765, 842, 870, 1020, 1640])


#new_plane_pipeline(QC, JAES_maintenance_dates, 70, 10, 0, 0, False,
              #     fit_method = 'bounds')

#new_plane_pipeline(QC, LOBE_maintenance_dates, 60, 10, 0, 0, False,
 #                  fit_method = 'bounds')

#aod_plotter(QC, LOBE_maintenance_dates, 60, 10,
 #                          'irradiance_LOBEv3_analysis',
  #                       [415, 490, 550, 665, 675, 705, 740, 765, 842, 870, 1020, 1640])