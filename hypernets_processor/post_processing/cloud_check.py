import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.pyplot import tight_layout
import scipy.optimize as spo
import xarray as xr
from ast import literal_eval

# read in data
windows_results_path = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/joe"

linux_data_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc"
windows_data_path = r"T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc"

dataframe = pd.read_csv(windows_data_path + r"/LOBEv4_irradiance.csv")
wav_df = xr.open_dataset(
    "T:/ECO/EOServer/data/insitu/hypernets/archive/LOBE/2025/07/07/SEQ20250707T143048/HYPERNETS_L_LOBE_L1B_IRR_20250707T1430_20250707T1623_v2.1.nc"
)
wav = wav_df.wavelength.values

def find_nearest_to_wav(array, wv, value):
    wv = np.asarray(wv)
    idx = (np.abs(wv - value)).argmin()
    mean = np.mean(
        [array[idx - 2], array[idx - 1], array[idx], array[idx + 1], array[idx + 2]]
    )
    return mean


def interpolate_irradiance_sza(sza, ds_irr):
    ds_irr_temp = ds_irr.copy()
    ds_irr_temp["solar_irradiance_BOA"].values = (
        ds_irr_temp["solar_irradiance_BOA"].values
        / np.cos(ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
    )
    ds_irr_temp = ds_irr_temp.interp(sza=sza, wavelength=wav, method="linear")
    ds_irr_temp["solar_irradiance_BOA"].values = ds_irr_temp[
        "solar_irradiance_BOA"
    ].values * np.cos(ds_irr_temp["sza"].values / 180 * np.pi)
    return ds_irr_temp["solar_irradiance_BOA"].values


def modelled_data_read_and_interp(sza, aod):
    mod_data = xr.open_dataset(
        r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\LOBE_clear_sky_medianaod.nc".format(
            aod
        )
    )
    sza = float(sza)
    interp_mod_data = interpolate_irradiance_sza(sza, mod_data)
    return interp_mod_data


IDs = dataframe["ID"]
flags = dataframe["Flag"]

##get dates and times of measurements


def get_dates_times(data):
    dates = []
    times = []
    for i in range(len(data)):
        date = int(IDs[i][3:11])
        time = int(IDs[i][12:16])
        dates.append(date)
        times.append(time)
    new_data = data.assign(date=dates, time=times)
    return new_data


##remove flagged data

bad_inds = []
bad_flags = []
for i in range(len(flags)):
    if flags.values[i] != 0:
        bad_inds.append(i)
        bad_flags.append(flags.values[i])

df_clean = dataframe.drop(bad_inds)
df_clean.reset_index(drop=True, inplace=True)
df_clean = get_dates_times(df_clean)

IDs = df_clean.iloc[:, 0]

IDs.to_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\clean_irr_IDs.csv"
)
szas = df_clean["SZA"]


def read_irr(df):
    data = np.zeros((df.shape[0], len(df.columns) - 6))

    for j in range(df.shape[0]):
        for i in range(len(df.columns) - 6):
            data[j, i] = df["{}".format(i)][j]

    return data


data = read_irr(df_clean)
"""
outliers = pd.read_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_outliers.csv"
)
good_data = pd.read_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_good.csv"
)

outliers_IDs = outliers["# id"]
good_IDs = good_data["# id"]

is_outlier = IDs.isin(outliers_IDs)
print(len(is_outlier))
"""

# plotting
print(len(szas))
print(np.argwhere(IDs == 'SEQ20250707T143048'))
ID_num = np.argwhere(IDs == 'SEQ20250707T143048')[1]
aod_1_data = modelled_data_read_and_interp(szas[ID_num], 0.1)

plt.plot(wav, data[ID_num,:].T, label = 'Measured Data')
plt.plot(wav, aod_1_data, label = 'Model')

plt.ylabel("Irradiance")
plt.xlabel("Wavelength (nm)")
plt.legend()
plt.show()


def check(data, tolerance, wavelength):
    passes = np.zeros((data.shape[0], 4))
    values = np.zeros((data.shape[0], 4))
    for i in range(data.shape[0]):
        aod_0 = find_nearest_to_wav(
            modelled_data_read_and_interp(szas[i], 0.0), wav, wavelength
        )
        aod_1 = find_nearest_to_wav(
            modelled_data_read_and_interp(szas[i], 0.1), wav, wavelength
        )
        aod_2 = find_nearest_to_wav(
            modelled_data_read_and_interp(szas[i], 0.2), wav, wavelength
        )
        aod_3 = find_nearest_to_wav(
            modelled_data_read_and_interp(szas[i], 0.3), wav, wavelength
        )
        meas = find_nearest_to_wav(data[i, :], wav, wavelength)

        values[i, 0] = aod_0 * tolerance - meas
        values[i, 1] = aod_1 * tolerance - meas
        values[i, 2] = aod_2 * tolerance - meas
        values[i, 3] = aod_3 * tolerance - meas

        for j in range(4):
            if values[i, j] > 0:
                passes[i, j] = 1  # cloudy
            else:
                passes[i, j] = 0  # clear

        print(i, passes[i, :])
    return values, passes


"""
val, pas = check(data, 0.9, 550)

out_pas = pas[is_outlier == True]
good_pas = pas[is_outlier == False]

print(len(out_pas))

outs_removed_0 = list(out_pas[:, 0]).count(1)/len(out_pas)
good_removed_0 = list(good_pas[:, 0]).count(1)/len(good_pas)

outs_removed_1 = list(out_pas[:, 1]).count(1)/len(out_pas)
good_removed_1 = list(good_pas[:, 1]).count(1)/len(good_pas)

outs_removed_2 = list(out_pas[:, 2]).count(1)/len(out_pas)
good_removed_2 = list(good_pas[:, 2]).count(1)/len(good_pas)

outs_removed_3 = list(out_pas[:, 3]).count(1)/len(out_pas)
good_removed_3 = list(good_pas[:, 3]).count(1)/len(good_pas)

print('For AOD = 0.0, the percentage of outliers removed is {:.2f}% and the percentage of good data removed is {:.2f}%'.format(outs_removed_0*100, good_removed_0*100))
print('For AOD = 0.1, the percentage of outliers removed is {:.2f}% and the percentage of good data removed is {:.2f}%'.format(outs_removed_1*100, good_removed_1*100))
print('For AOD = 0.2, the percentage of outliers removed is {:.2f}% and the percentage of good data removed is {:.2f}%'.format(outs_removed_2*100, good_removed_2*100))
print('For AOD = 0.3, the percentage of outliers removed is {:.2f}% and the percentage of good data removed is {:.2f}%'.format(outs_removed_3*100, good_removed_3*100))
"""


def tol_checks(data, tol_start, tol_stop, tol_step, wavelength):
    tol = np.arange(tol_start, tol_stop, tol_step)
    aod_0_outs = []
    aod_0_good = []
    aod_1_outs = []
    aod_1_good = []
    aod_2_outs = []
    aod_2_good = []
    aod_3_outs = []
    aod_3_good = []
    for i in tol:
        val, pas = check(data, i, wavelength)
        # out_pas = pas[is_outlier == True]
        # good_pas = pas[is_outlier == False]

        cut_IDs_0 = IDs[pas[:, 0] == 1]
        out_cut_0 = outliers[outliers["# id"].isin(cut_IDs_0)]
        good_cut_0 = good_data[good_data["# id"].isin(cut_IDs_0)]
        aod_0_outs.append(len(out_cut_0) * 100 / len(outliers))
        aod_0_good.append(len(good_cut_0) * 100 / len(good_data))

        cut_IDs_1 = IDs[pas[:, 1] == 1]
        out_cut_1 = outliers[outliers["# id"].isin(cut_IDs_1)]
        good_cut_1 = good_data[good_data["# id"].isin(cut_IDs_1)]
        aod_1_outs.append(len(out_cut_1) * 100 / len(outliers))
        aod_1_good.append(len(good_cut_1) * 100 / len(good_data))

        cut_IDs_2 = IDs[pas[:, 2] == 1]
        out_cut_2 = outliers[outliers["# id"].isin(cut_IDs_2)]
        good_cut_2 = good_data[good_data["# id"].isin(cut_IDs_2)]
        aod_2_outs.append(len(out_cut_2) * 100 / len(outliers))
        aod_2_good.append(len(good_cut_2) * 100 / len(good_data))

        cut_IDs_3 = IDs[pas[:, 3] == 1]
        out_cut_3 = outliers[outliers["# id"].isin(cut_IDs_3)]
        good_cut_3 = good_data[good_data["# id"].isin(cut_IDs_3)]
        aod_3_outs.append(len(out_cut_3) * 100 / len(outliers))
        aod_3_good.append(len(good_cut_3) * 100 / len(good_data))

    return np.vstack(
        (
            tol,
            aod_0_outs,
            aod_0_good,
            aod_1_outs,
            aod_1_good,
            aod_2_outs,
            aod_2_good,
            aod_3_outs,
            aod_3_good,
        )
    )


def wav_checks(data, tol, wav_start, wav_stop, wav_step):
    wav = np.arange(wav_start, wav_stop, wav_step)
    aod_0_outs = []
    aod_0_good = []
    aod_1_outs = []
    aod_1_good = []
    aod_2_outs = []
    aod_2_good = []
    aod_3_outs = []
    aod_3_good = []
    for i in wav:
        val, pas = check(data, tol, i)
        out_pas = pas[is_outlier == True]
        good_pas = pas[is_outlier == False]

        aod_0_outs.append(list(out_pas[:, 0]).count(1) * 100 / len(out_pas))
        aod_0_good.append(list(good_pas[:, 0]).count(1) * 100 / len(good_pas))

        aod_1_outs.append(list(out_pas[:, 1]).count(1) * 100 / len(out_pas))
        aod_1_good.append(list(good_pas[:, 1]).count(1) * 100 / len(good_pas))

        aod_2_outs.append(list(out_pas[:, 2]).count(1) * 100 / len(out_pas))
        aod_2_good.append(list(good_pas[:, 2]).count(1) * 100 / len(good_pas))

        aod_3_outs.append(list(out_pas[:, 3]).count(1) * 100 / len(out_pas))
        aod_3_good.append(list(good_pas[:, 3]).count(1) * 100 / len(good_pas))

    return np.vstack(
        (
            wav,
            aod_0_outs,
            aod_0_good,
            aod_1_outs,
            aod_1_good,
            aod_2_outs,
            aod_2_good,
            aod_3_outs,
            aod_3_good,
        )
    )


# np.savetxt(r'C:/Users/jr20/code/hypernets_cloud_checks/na.csv', tol_checks(data, 0.8, 1, 0.02, 550), delimiter = ',')


def make_new_csvs(data_refl, passes, filepath=None):
    cut_IDs = IDs[passes == 1]

    new = data_refl[~data_refl["# id"].isin(cut_IDs)]
    new.reset_index(drop=True, inplace=True)
    print(len(new), len(data_refl))
    if filepath is not None:
        new.to_csv(filepath, index=False)


refl_data = pd.read_csv(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_prelim_and_raa10.csv"
)
"""
val_0_875, pass_0_875 = check(data, 0.875, 550)
make_new_csvs(refl_data, pass_0_875[:,0], r'T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\prelim_cc0875.csv')
"""
val_1_9, pass_1_9 = check(data, 0.9, 550)
make_new_csvs(
    good_data,
    pass_1_9[:, 1],
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_cc_good.csv",
)
make_new_csvs(
    outliers,
    pass_1_9[:, 1],
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\joe\GHNA_2022_cc_outliers.csv",
)


JSIT = xr.open_dataset(
    r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\irr_clear_sky_JSIT_0.0_10.nc"
)
print(JSIT)
