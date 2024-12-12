import numpy as np
import pandas as pd
import xarray as xr
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from seaborn.external.docscrape import header

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

def modelled_data_read_and_interp(sza, mod_data):
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
        labelled_data = dt_data.assign(post_processing_flags = [ [] for _ in range(len(data))])
        #set radiance
        self.radiance = dt_data
        self.labelled_radiance = labelled_data
        #read in irradiance
        self.irradiance = pd.read_csv(irr_path)
        #define other features
        self.cc_radiance = None
        self.radiance_good = None
        self.radiance_outliers = None
        self.cloud_passes = None
        self.cloud_check_tol = None
        self.clear_sky_model = xr.open_dataset(r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance_Gobabeb\Gobabeb_clear_sky_aod{}.nc'.format(0.1))

    def size(self, var):
        if var == 'radiance':
            print(len(self.radiance))
        elif var == 'good':
            print(len(self.radiance_good))
        elif var == 'outliers':
            print(len(self.radiance_outliers))
        else:
            print('var must be radiance, good, or outliers')

    def save(self, var, filepath):
        if var == 'radiance':
            data = self.radiance
        elif var == 'good':
            data = self.radiance_good
        elif var == 'outliers':
            data = self.radiance_outliers
        else:
            print('data not saved')
            quit()

        data.to_csv(filepath, index = False)

    def basic_outlier_definition(self):
        mean = self.radiance[' refl_550nm'].mean()
        stde = self.radiance[' refl_550nm'].std()
        max_range = mean + (stde * 3)
        min_range = mean - (stde * 3)
        outliers = self.radiance[(self.radiance[' refl_550nm'] > max_range) | (self.radiance[' refl_550nm'] < min_range)]
        good_data = self.radiance[(self.radiance[' refl_550nm'] < max_range) & (self.radiance[' refl_550nm'] > min_range)]
        good_data.reset_index(drop=True, inplace=True)
        outliers.reset_index(drop=True, inplace=True)

        self.radiance_outliers = outliers
        self.radiance_good = good_data

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

        for x in self.labelled_radiance['post_processing_flags'][self.labelled_radiance['date'].isin(bad_dates)]:
            x.append(1)

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

        for x in self.labelled_radiance['post_processing_flags'].loc[self.labelled_radiance[' sza'] > sza_limit]:
            x.append(2)

    def raa_cut(self, raa_limit):
        bad_inds = []
        for i in range(len(self.radiance)):
            raa = self.radiance['raa'][i]
            if (raa < raa_limit) | (raa > 360 - raa_limit):
                bad_index = i
                bad_inds.append(bad_index)
            else:
                continue

        cleaned_data = self.radiance.drop(bad_inds)
        cleaned_data.reset_index(drop=True, inplace=True)
        self.radiance = cleaned_data

        for x in self.labelled_radiance['post_processing_flags'].loc[(self.labelled_radiance['raa'] < raa_limit) | (self.labelled_radiance['raa'] > 360 - raa_limit)]:
            x.append(6)

    def clean_irr(self):
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
        #check irradiance file exists for every radiance
        for i, ID in enumerate(list(self.irradiance['ID'])):
            if ID in list(self.radiance['# id']):
                continue
            else:
                bad_IDs.append(ID)
                bad_inds.append(i)

        #clean irradiance
        df_clean = self.irradiance.drop(bad_inds)
        df_clean.reset_index(drop=True, inplace=True)
        self.irradiance = df_clean
        #clean radiance
        new = self.radiance[~self.radiance['# id'].isin(bad_IDs)]
        new.reset_index(drop=True, inplace=True)
        self.radiance = new

        for x in self.labelled_radiance['post_processing_flags'].loc[self.labelled_radiance['# id'].isin(bad_IDs)]:
            x.append(3)

    def cloud_check(self, tolerance, wavelength, rewrite, rewrite_var = None):
        szas = self.irradiance ['SZA']
        IDs = self.irradiance['ID']

        if self.cloud_passes is None:
            data = np.zeros((self.irradiance.shape[0], len(self.irradiance.columns) - 5))

            for j in range(self.irradiance.shape[0]):
                for i in range(len(self.irradiance.columns) - 5):
                    data[j, i] = self.irradiance['{}'.format(i)][j]

            passes = np.zeros(self.irradiance.shape[0])
            values = np.zeros(self.irradiance.shape[0])

            for i in range(data.shape[0]):
                aod_1 = find_nearest_to_wav(modelled_data_read_and_interp(szas[i], self.clear_sky_model), wav, wavelength)
                meas = find_nearest_to_wav(data[i, :], wav, wavelength)
                values[i] = aod_1 * tolerance - meas

                if values[i] > 0:
                    passes[i] = 1  # cloudy
                else:
                    passes[i] = 0  # clear

                print(i, passes[i])

            #save passes
            self.cloud_passes = passes

        cut_IDs = IDs[self.cloud_passes == 1]

        #rewrite datasets
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
            elif rewrite_var == 'labels':
                for x in self.labelled_radiance['post_processing_flags'].loc[
                    self.labelled_radiance['# id'].isin(cut_IDs)]:
                    x.append(4)

        else:
            print('rewrite_var must be radiance, good, outliers, or labels')
            print('radiances not filtered by cloud check')
            self.cc_radiance = new



    def plane_fitter(self, labelled = False):

        if self.cc_radiance is None:
            self.cc_radiance = self.radiance

        #define datasets
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

        if labelled:
            for y in self.labelled_radiance['post_processing_flags'][self.labelled_radiance.apply(tuple, axis = 1).isin([tuple(x) for x in outs.values])]:
                y.append(5)
        else:
            self.radiance_good = good
            self.radiance_outliers = outs

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
            out_cut = self.radiance_outliers[self.radiance_outliers['# id'].isin(cut_IDs)]
            good_cut = self.radiance_good[self.radiance_good['# id'].isin(cut_IDs)]
            outs.append(len(out_cut) * 100 / len(self.radiance_outliers))
            good.append(len(good_cut) * 100 / len(self.radiance_good))

        optimiser = pd.DataFrame(np.array((tol, outs, good)).T, columns = ['tol', 'outs','good'])
        optimised = optimiser[optimiser['good'] < good_limit]
        best_tol = optimised['tol'][(optimised['outs'] - optimised['good']).argmax()]

        self.cloud_check_tol = best_tol
        self.cloud_passes = None

        if plot:
            fig, ax = plt.subplots(1, 1, figsize=(6, 4), dpi=150)
            ax.plot(tol, outs, label='Outliers', color='r', linestyle='solid')
            ax.plot(tol, good, label='Good Data', color='r', linestyle='dotted')
            ax.set_xlabel('Tolerance')
            ax.set_ylabel('Percentage of Data Removed')
            ax.set_title('Cloud Check Tolerance Analysis for 550nm')
            ax.legend()
            plt.show()

            fig, ax = plt.subplots(1, 1, figsize=(6, 4), dpi=150)
            ax.plot(tol, np.array(outs) - np.array(good), color='r', linestyle='solid')
            ax.set_xlabel('Tolerance')
            ax.set_ylabel('Percentage of Data Removed')
            ax.set_title('Cloud Check Tolerance Analysis for 550nm')
            plt.show()

    def mask(self, data_type):

        if data_type == 'good':
            data = self.radiance_good
        elif data_type == 'outliers':
            data = self.radiance_outliers
        elif data_type == 'labelled':
            data = self.labelled_radiance
        else:
            print('data not masked')
            quit()

        mask1 = np.where(((data[' vza'] < 6) & (data[' saa'] < 90) & (data[' sza'] < 5)))[0]

        mask11 = np.where(((data[' vza'] < 6) & (data[' saa'] < 90) & (data[' saa'] > 30) & (data[' sza'] < 14)))[0]

        mask12 = np.where(((data[' vza'] < 6) & (data[' saa'] < 90) & (data[' saa'] > 60) & (data[' sza'] < 20) & (data[' sza'] > 14)))[0]

        mask13 = np.where(((data[' vza'] < 6) & (data[' saa'] < 90) & (data[' saa'] > 60) & (data[' sza'] < 26) & (data[' sza'] > 22)))[0]

        mask14 = np.where(((data[' vza'] < 6) & (data[' saa'] < 110) & (data[' saa'] > 70) & (data[' sza'] > 53)))[0]

        mask2 = np.where(((data[' vza'] < 6) & (data[' saa'] < 320) & (data[' saa'] > 260) & (data[' sza'] < 20)))[0]

        mask3 = np.where(data[' vza'] < 1)[0]

        mask4 = np.where(((data[' vza'] > 45) & (data[' saa'] < 264) & (data[' saa'] > 254) & (data[' sza'] > 50)))[0]

        #mask5 = np.where(((data[' vza'] > 45) & (data['raa'] < 230) & (data['raa'] > 210) & (data[' sza'] > 65)))[0] #i think same data as 14 in v3

        mask = np.unique(np.hstack((mask1, mask11, mask12, mask13, mask14, mask2, mask3, mask4)))

        if data_type == 'good':
            self.radiance_good = data.loc[~data.index.isin(mask)]
        elif data_type == 'outliers':
            self.radiance_outliers = data.loc[~data.index.isin(mask)]
        elif data_type == 'labelled':
            for x in self.labelled_radiance['post_processing_flags'][mask]:
                x.append(7)
        else:
            print('data not masked')

def pipeline(dataset : PostProcessingDataset, maintenance, sza_limit, raa_limit):
    print('Initial', len(dataset.radiance))
    dataset.maintenance_check(maintenance)
    print('Maintenance', len(dataset.radiance))
    dataset.sza_check(sza_limit)
    print('SZA', len(dataset.radiance))
    dataset.raa_cut(raa_limit)
    print('RAA', len(dataset.radiance))
    dataset.clean_irr()
    print('IRR Flags', len(dataset.radiance))
    dataset.cloud_check(0.9, 550, False)
    dataset.plane_fitter()
    dataset.size('good')
    dataset.size('outliers')
    dataset.cloud_check(0.9, 550, True, rewrite_var = 'good')
    dataset.cloud_check(0.9, 550, True, rewrite_var = 'outliers')
    dataset.size('good')
    dataset.size('outliers')
    #dataset.save('good', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv1_processed_good.csv')
    #dataset.save('outliers', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv1_processed_out.csv')
    dataset.mask('good')
    dataset.mask('outliers')
    dataset.size('good')
    dataset.size('outliers')
    #dataset.save('good', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv3_processed1_good.csv')
    #dataset.save('outliers', r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\GHNAv3_processed1_out.csv')


def tolerance_analysis(dataset : PostProcessingDataset, maintenance, sza_limit, raa_limit):
    #inital checks
    dataset.maintenance_check(maintenance)
    dataset.sza_check(sza_limit)
    dataset.raa_cut(raa_limit)
    dataset.clean_irr()
    #inital outlier definition
    dataset.plane_fitter()
    #sparse tolerance analysis
    dataset.tol_optimiser(0.4, 1.1, 0.1, 550, 100,True)
    #use best tolerance to define planes
    dataset.cloud_check(dataset.cloud_check_tol, 550, False)
    dataset.plane_fitter()
    #in depth tolerance analysis
    dataset.tol_optimiser(dataset.cloud_check_tol - 0.1, dataset.cloud_check_tol + 0.1, 0.01, 550, 10,True)
    #use best tolerance to define planes
    dataset.cloud_check(dataset.cloud_check_tol, 550, False)
    dataset.plane_fitter()
    dataset.plane_fitter(True)
    dataset.size('good')
    dataset.size('outliers')
    #cloud check final definition of data
    dataset.cloud_check(dataset.cloud_check_tol, 550, True, rewrite_var = 'good')
    dataset.cloud_check(dataset.cloud_check_tol, 550, True, rewrite_var = 'outliers')
    dataset.cloud_check(dataset.cloud_check_tol, 550, True, rewrite_var = 'labels')
    print(dataset.cloud_check_tol)
    dataset.size('good')
    dataset.size('outliers')


QC = PostProcessingDataset(r'T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/GHNA_v1_None_None_None_None.csv',
                           r'T:/ECO/EOServer//data/insitu/hypernets/post_processing_qc/GHNAv1_irradiance.csv')

GHNA_maintenance_dates = ['20231016','20231017','20231018','20231019','20231020','20231021','20231022','20231023',
                          '20231024','20231025','20240513','20240514','20240515','20240516','20240517','20240518',
                          '20240519','20240520']

tolerance_analysis(QC, GHNA_maintenance_dates, 70, 10)

#pipeline(QC, GHNA_maintenance_dates, 70, 10)
