import numpy as np
import hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

# set appropriate folders (different for linux or windows) and settings
data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
results_path = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc"
site = "GHNA"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)
start_time = "20251015T0000"
stop_time = "20251201T0000"
wavelength = 550

# start_tod = ["0900","0930","1000","1030","1100"]
# stop_tod = ["0930","1000","1030","1100","1130"]
#
# start_tod = ["0900","1000","1100"]
# stop_tod = ["1000","1100","1200"]

start_tod = [None]
stop_tod = [None]

# #set minimum and maximum reflectance for colourbar plots (Set to None to let it work it out automatically)
vmin = 0.18
vmax = 0.28

vzas = [20]
vaas = [83]


def find_nearest_to_wav(array, wv, value):

    wv = np.asarray(wv)
    idx = (np.abs(wv - value)).argmin()
    return array[idx]


data_clear = xr.open_dataset(
    "T:/ECO/EOServer/data/insitu/hypernets/archive/GHNA/2025/11/05/SEQ20251105T123143/HYPERNETS_L_GHNA_L1B_IRR_20251105T1231_20251113T0335_v2.2.nc")
wav_ori = data_clear.wavelength.values
print("Got wavelengths")

def get_irr(data, wav_val):
    data = xr.open_dataset(r"%s" % data)
    wav = data.wavelength.values
    irr = data.irradiance.to_pandas()
    szas = data.solar_zenith_angle.values
    saas = data.solar_azimuth_angle.values
    if wav_val is None:
        if irr.shape[1] != 2 or szas.shape[0] != 2:
            irr1 = np.zeros(len(wav))
            irr2 = np.zeros(len(wav))
            qual = [999, 999]
            sza = [999, 999]
            saa = [999, 999]
        else:
            irr1 = np.array(irr.iloc[:, 0].values)
            irr2 = np.array(irr.iloc[:, 1].values)
            qual = data.quality_flag.values
            sza = szas
            saa = saas
    else:
        if irr.shape[1] != 2 or szas.shape[0] != 2:
            irr1 = 0
            irr2 = 0
            qual = [999, 999]
            sza = [999, 999]
        else:
            irr1 = find_nearest_to_wav(irr.iloc[:, 0].values, wav, wav_val)
            irr2 = find_nearest_to_wav(irr.iloc[:, 1].values, wav, wav_val)
            qual = data.quality_flag.values
            sza = szas

    return irr1, irr2, wav, qual, sza, saa


def make_irrs(file_list, wav_val):
    if wav_val is None:
        irrs = pd.DataFrame(columns=["ID", "Flag", "SZA", "SAA"])
        refl = np.zeros((len(file_list) * 2, len(wav_ori)))
        for j in range(len(file_list)):
            try:
                irr1, irr2, wav, qual, sza, saa = get_irr(file_list[j], wav_val=wav_val)
                new_row1 = pd.Series(
                    {
                        "ID": file_list[j][62:80],
                        "Flag": qual[0],
                        "SZA": sza[0],
                        "SAA": saa[0],
                    }
                )
                new_row2 = pd.Series(
                    {
                        "ID": file_list[j][62:80],
                        "Flag": qual[1],
                        "SZA": sza[1],
                        "SAA": saa[1],
                    }
                )
                irrs = pd.concat([irrs, new_row1.to_frame().T], ignore_index=True)
                irrs = pd.concat([irrs, new_row2.to_frame().T], ignore_index=True)
                refl[2 * j, :] = irr1
                refl[2 * j + 1, :] = irr2
            except Exception as e:
                print("failed due to", e)
                refl[2 * j, :] = np.ones(len(wav_ori)) * -999
                refl[2 * j + 1, :] = np.ones(len(wav_ori)) * -999
        for k in range(len(wav_ori)):
            irrs.insert(len(irrs.columns), "{}".format(k), refl[:, k])
    else:
        irrs = pd.DataFrame(columns=["ID", "Flag", "SZA", "Data"])
        for j in range(len(file_list)):
            irr1, irr2, wav, qual, sza = get_irr(file_list[j], wav_val=wav_val)
            new_row1 = pd.Series(
                {
                    "ID": file_list[j][62:80],
                    "Flag": qual[0],
                    "SZA": sza[0],
                    "Data": irr1,
                }
            )
            new_row2 = pd.Series(
                {
                    "ID": file_list[j][62:80],
                    "Flag": qual[1],
                    "SZA": sza[1],
                    "Data": irr2,
                }
            )
            irrs = pd.concat([irrs, new_row1.to_frame().T], ignore_index=True)
            irrs = pd.concat([irrs, new_row2.to_frame().T], ignore_index=True)

    irrs.to_csv(results_path + '\GHNA_2025Oct_2025Nov_irradiance.csv', index=False)
    return irrs


##running

files = glob.glob(os.path.join(data_path, "GHNA", "2025", "*", "*", "*", "*L1B_IRR*.nc"))

print("Files In")

for ii in range(len(start_tod)):
    files = data_io.filter_files_quick(
        files, start_time, stop_time, tod_start=start_tod[ii], tod_stop=stop_tod[ii]
    )
print("Files Sorted")

irrs = make_irrs(files, None)
print(irrs.iloc[1])
"""
data_cloud = 'T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\12\SEQ20240312T070125\HYPERNETS_L_GHNA_L1B_IRR_20240312T0701_20240416T2306_v2.0.nc'
data_clear = 'T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\14\SEQ20240314T070025\HYPERNETS_L_GHNA_L1B_IRR_20240314T0700_20240416T1138_v2.0.nc'

irr_clear1, irr_clear2, wav_clear, qual_clear, sza_clear = get_irr(data_clear, 550)
irr_cloud1, irr_cloud2, wav_cloud, qual_cloud, sza_cloud = get_irr(data_cloud, 550)

plt.plot(wav_clear - wav_cloud)
plt.show()
"""
