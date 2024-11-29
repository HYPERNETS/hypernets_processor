import numpy as np
import pandas as pd
import xarray as xr
from scipy.optimize import curve_fit

wav_df = xr.open_dataset(r'T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\14\SEQ20240314T070025\HYPERNETS_L_GHNA_L1B_IRR_20240314T0700_20240416T1138_v2.0.nc')
wav = wav_df.wavelength.values

def find_nearest_to_wav(array, wv, value):
    wv = np.asarray(wv)
    idx = (np.abs(wv - value)).argmin()
    mean = np.mean([array[idx-2], array[idx-1], array[idx], array[idx+1], array[idx+2]])
    return mean

def interpolate_irradiance_sza(sza,ds_irr):
    ds_irr_temp = ds_irr.copy()
    ds_irr_temp["solar_irradiance_BOA"].values = ds_irr_temp["solar_irradiance_BOA"].values / np.cos(ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
    ds_irr_temp = ds_irr_temp.interp(sza=sza, wavelength = wav, method="linear")
    ds_irr_temp["solar_irradiance_BOA"].values = ds_irr_temp["solar_irradiance_BOA"].values * np.cos(ds_irr_temp["sza"].values / 180 * np.pi)
    return ds_irr_temp["solar_irradiance_BOA"].values

def modelled_data_read_and_interp(sza, aod):
    mod_data = xr.open_dataset(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance_Gobabeb\Gobabeb_clear_sky_aod{}.nc'.format(aod))
    sza = float(sza)
    interp_mod_data = interpolate_irradiance_sza(sza, mod_data)
    return interp_mod_data

def raa_binning(data, raa_limits):

    if raa_limits[1] > raa_limits[0]:
        new_data = data[(data['raa'] > raa_limits[0]) & (data['raa'] < raa_limits[1])]
        new_data = new_data.reset_index(drop = True)
        return new_data

    if raa_limits[1] < raa_limits[0]:
        new_data = data[(data['raa'] > raa_limits[0]) | (data['raa'] < raa_limits[1])]
        new_data = new_data.reset_index(drop = True)
        return new_data

def quad_plane(xy, a, b, c, d, e, f):
    x, y = xy
    return a + b * x + c * y + d * x ** 2 + e * y ** 2 + f * x * y

def plane_fit_and_plot(data, data_setting, stds):
    x = data[' sza'].values
    y = data[' vza'].values
    z = data[' refl_550nm'].values

    popt, pcov = curve_fit(quad_plane, (x, y), z)
    below = popt - stds * np.sqrt(np.diag(pcov))
    above = popt + stds * np.sqrt(np.diag(pcov))

    z_below = quad_plane((data_setting[' sza'].values, data_setting[' vza'].values), *below) - data_setting[' refl_550nm'].values*0.05
    z_above = quad_plane((data_setting[' sza'].values, data_setting[' vza'].values), *above) + data_setting[' refl_550nm'].values*0.05

    outliers = data_setting[(data_setting[' refl_550nm'] > z_above) | (data_setting[' refl_550nm'] < z_below)]
    good_data = data_setting[(data_setting[' refl_550nm'] < z_above) & (data_setting[' refl_550nm'] > z_below)]
    good_data.reset_index(drop = True, inplace = True)
    outliers.reset_index(drop = True, inplace = True)

    return outliers, good_data

class PostProcessingDataset:

    def __init__(self, rad_path, irr_path):

        #read in radiance
        data = pd.read_csv(rad_path)
        #define raa
        data.loc[:, 'raa'] = (data.loc[:, ' vaa'] - data.loc[:, ' saa'] + 360) % 360
        #extract dates and times
        dates = []
        times = []
        for i in range(len(data)):
            date = data['# id'][i][3:11]
            time = data['# id'][i][12:16]
            dates.append(date)
            times.append(time)
        dt_data = data.assign(date=dates, time=times)
        #set radiance
        self.radiance = dt_data
        #read in irradiance
        self.irradiance = pd.read_csv(irr_path)
        #define other features
        self.cc_radiance = None
        self.radiance_good = None
        self.radiance_outliers = None

    def size(self):
        print(len(self.radiance))

    def maintenance_check(self, bad_dates):
        ### note bad_dates need to be in speech marks###
        bad_inds = []
        # get dates of measurements
        for i in range(len(self.radiance)):
            date = self.radiance['date'][i]

            # remove maintenance dates
            if date in bad_dates:
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

    def sza_check(self, sza_limit):
        bad_inds = []
        for i in range(len(self.radiance)):
            sza = self.radiance[' sza'][i]
            if sza > sza_limit:
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

    def clean_irr_flags(self):
        IDs = self.irradiance['ID']
        flags = self.irradiance['Flag']

        bad_inds = []
        bad_flags = []
        bad_IDs = []
        #find flags in irr data
        for i in range(len(flags)):
            if flags.values[i] != 0:
                bad_inds.append(i)
                bad_flags.append(flags.values[i])
                bad_IDs.append(IDs[i])

        #clean irradiance
        df_clean = self.irradiance.drop(bad_inds)
        df_clean.reset_index(drop=True, inplace=True)
        self.irradiance = df_clean
        #clean radiance
        new = self.radiance[~self.radiance['# id'].isin(bad_IDs)]
        new.reset_index(drop=True, inplace=True)
        self.radiance = new

    def cloud_check(self, tolerance, wavelength, rewrite, rewrite_var = None):
        szas = self.irradiance ['SZA']
        IDs = self.irradiance['ID']

        data = np.zeros((self.irradiance.shape[0], len(self.irradiance.columns) - 5))

        for j in range(self.irradiance.shape[0]):
            for i in range(len(self.irradiance.columns) - 5):
                data[j, i] = self.irradiance['{}'.format(i)][j]

        passes = np.zeros(self.irradiance.shape[0])
        values = np.zeros(self.irradiance.shape[0])

        for i in range(data.shape[0]):
            aod_1 = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], 0.1), wav, wavelength)
            meas = find_nearest_to_wav(data[i, :], wav, wavelength)
            values[i] = aod_1 * tolerance - meas

            if values[i] > 0:
                passes[i] = 1  # cloudy
            else:
                passes[i] = 0  # clear

            print(i, passes[i])

        cut_IDs = IDs[passes == 1]

        if rewrite_var == 'radiance':
            data_refl = self.radiance
        elif rewrite_var == 'good':
            data_refl = self.radiance_good
        elif rewrite_var == 'outliers':
            data_refl = self.radiance_outliers
        else:
            data_refl = self.radiance

        new = data_refl[~data_refl['# id'].isin(cut_IDs)]
        new.reset_index(drop=True, inplace=True)

        if rewrite:
            if rewrite_var == 'radiance':
                self.radiance = new
            elif rewrite_var == 'good':
                self.radiance_good = new
            elif rewrite_var == 'outliers':
                self.radiance_outliers = new
            else:
                print('rewrite_var must be radiance, good, or outliers')
                print('radiances not filtered by cloud check')
        else:
            self.cc_radiance = new

    def plane_fitter(self):

        #define datasets
        data = self.cc_radiance
        data_unmasked = self.radiance

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

        outs, good = plane_fit_and_plot(data_list[0], data_unmasked_list[0], 3)
        for i in range(len(data_list) - 1):
            outs = pd.concat([outs, plane_fit_and_plot(data_list[i + 1], data_unmasked_list[i + 1], 3)[0]],ignore_index=True)
            good = pd.concat([good, plane_fit_and_plot(data_list[i + 1], data_unmasked_list[i + 1], 3)[1]], ignore_index=True)

        self.radiance_good = good
        self.radiance_outliers = outs


def pipeline(dataset : PostProcessingDataset, maintenance, sza_limit):
    dataset.maintenance_check(maintenance)
    dataset.sza_check(sza_limit)
    dataset.clean_irr_flags()
    dataset.cloud_check(0.9, 550, False)
    dataset.plane_fitter()
    dataset.cloud_check(0.9, 550, True)


QC = PostProcessingDataset(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_refl_2024_None_None_None_None.csv',
                           r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/joe_irradiance_2024.csv')

maintenance_dates = ['20240513', '20240514', '20240515', '20240516', '20240517', '20240518', '20240519', '20240520']

pipeline(QC, maintenance_dates, 70)
