import numpy as np
import hypernets_processor.post_processing.L2B_postprocessing.hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib
import datetime


import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

SITE_PERIODS = {
    "GHNA": [
        {
            "start_date": "2022-05-17",
            "stop_date": "2023-10-17",
            "HYPSTAR_SN": 220261,
            "comments": "v1 instrument",
        },
        {
            "start_date": "2023-10-26",
            "stop_date": "2025-10-15",
            "HYPSTAR_SN": 222316,
            "comments": "v3 instrument",
        },
        {
            "start_date": "2025-10-15",
            "stop_date": "present",
            "HYPSTAR_SN": 222316,
            "comments": "v3 instrument",
        },
    ],
    # "IFAR": [{"start_date": "2022-06-17", "stop_date": "2022-10-12" ,"HYPSTAR_SN": 221211, "comments": ""},{"start_date": "2023-08-04" , "stop_date": "2024-08-03" ,"HYPSTAR_SN": 221211, "comments": "Calibration E: 2023-01-25, L: 2023-01-27"}],
    "JAES": [
        {
            "start_date": "2023-04-14",
            "stop_date": "2024-05-09",
            "HYPSTAR_SN": 221461,
            "comments": "2023-05-20 leaves on (subjective judgement); 2023-09-19 cleaned optics; 2023-10-18 first snow, leaves off",
        },
        {
            "start_date": "2024-06-05",
            "stop_date": "2024-11-13",
            "HYPSTAR_SN": 221461,
            "comments": "",
        },
        {
            "start_date": "2024-11-13",
            "stop_date": "2025-06-16",
            "HYPSTAR_SN": 222317,
            "comments": "",
        },
        {
            "start_date": "2025-06-16",
            "stop_date": "2025-09-03",
            "HYPSTAR_SN": 222317,
            "comments": "",
        },
        {
            "start_date": "2025-09-03",
            "stop_date": "present",
            "HYPSTAR_SN": 222317,
            "comments": "",
        },
    ],
    "JSIT": [
        {
            "start_date": "2024-04-09",
            "stop_date": "2025-01-01",
            "HYPSTAR_SN": 222315,
            "comments": "2024 soybean (sowing date 08/04/2023); 2024/2025 durum wheat",
        },
        {
            "start_date": "2025-01-01",
            "stop_date": "2025-07-01",
            "HYPSTAR_SN": 222315,
            "comments": "2024 soybean (sowing date 08/04/2023); 2024/2025 durum wheat",
        },
        {
            "start_date": "2025-07-01",
            "stop_date": "present",
            "HYPSTAR_SN": 222315,
            "comments": "2024 soybean (sowing date 08/04/2023); 2024/2025 durum wheat",
        }
    ],
    "LOBE": [
        {
            "start_date": "2023-05-31",
            "stop_date": "2023-08-11",
            "lat": 50.55149,
            "lon": 4.74591,
            "HYPSTAR_SN": 222312,
            "comments": "Potato crop, furrowed ground; Non-standard sequence used, all data has quality flag `vza_irradiance' raised",
        },
        {
            "start_date": "2024-05-17",
            "stop_date": "2024-07-17",
            "lat": 50.55151,
            "lon": 4.74601,
            "HYPSTAR_SN": 222312,
            "comments": "Winter Wheat crop, Flat soil surface",
        },
        {
            "start_date": "2024-10-01",
            "stop_date": "2024-11-13",
            "lat": 50.55151,
            "lon": 4.74601,
            "HYPSTAR_SN": 222312,
            "comments": "Cover crop, Flat soil surface",
        },
        {
            "start_date": "2025-04-15",
            "stop_date": "2025-12-14",
            "lat": 50.55151,
            "lon": 4.74601,
            "HYPSTAR_SN": 222312,
            "comments": "Sugar beet roots, Flat soil surface",
        },
        {
            "start_date": "2025-12-15",
            "stop_date": "2026-03-24",
            "lat": 50.55151,
            "lon": 4.74601,
            "HYPSTAR_SN": 222312,
            "valid": False,
            "comments": "Site is fallow with flat soil surface",
        }
    ],
     "PEAN": [
         {
            "start_date": "2022-01-26",
            "stop_date": "2022-02-08",
            "HYPSTAR_SN": 221233,
            "comments": "v1 instrument",
        },
         {
            "start_date": "2022-12-25",
            "stop_date": "2023-02-02",
            "HYPSTAR_SN": 221233,
            "comments": "v1 instrument",
        },
         {
            "start_date": "2023-12-30",
            "stop_date": "2024-01-23",
            "HYPSTAR_SN": 222313,
            "comments": "v1 instrument",
        },
         ],
    "WWUK": [
        {
            "start_date": "2021-11-18",
            "stop_date": "2024-01-16",
            "HYPSTAR_SN": 220251,
            "comments": "v1 instrument",
        },
        {
            "start_date": "2024-06-26",
            "stop_date": "2024-12-31",
            "HYPSTAR_SN": 222314,
            "comments": "v3 instrument",
        },
        {
            "start_date": "2025-01-01",
            "stop_date": "present",
            "HYPSTAR_SN": 222314,
            "comments": "v3 instrument",
        },  
    ],
    "SPAR": [
        {
            "start_date": "2026-01-28",
            "stop_date": "present",
            "HYPSTAR_SN": 221211,
            "valid": False,
            "comments": "Site installed in San Pedro, Argentina, waiting for grass to regrow",
        },
    ],
}

# set appropriate folders (different for linux or windows) and settings
data_path = r"/mnt/t/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc/meteor_reprocessing"
site = "SPAR"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)
start_time = "20260128T0000"
stop_time = "20260501T0000"
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
    "/mnt/t/data/insitu/hypernets/archive/SPAR/2026/03/04/SEQ20260304T173050/HYPERNETS_L_SPAR_L1B_IRR_20260304T1730_20260304T1802_v2.2.nc")
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


def make_irrs(file_list, wav_val, tag, wav_ori):
    if wav_val is None:
        irrs = pd.DataFrame(columns=["ID", "Flag", "SZA", "SAA"])
        refl = np.zeros((len(file_list) * 2, len(wav_ori)))
        for j in range(len(file_list)):
            try:
                irr1, irr2, wav, qual, sza, saa = get_irr(file_list[j], wav_val=wav_val)
                new_row1 = pd.Series(
                    {
                        "ID": file_list[j].split("/")[-1].split("_")[-3],
                        "Flag": qual[0],
                        "SZA": sza[0],
                        "SAA": saa[0],
                    }
                )
                new_row2 = pd.Series(
                    {
                        "ID": file_list[j].split("/")[-1].split("_")[-3],
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
                    "ID": file_list[j].split("/")[-1].split("_")[-3],
                    "Flag": qual[0],
                    "SZA": sza[0],
                    "Data": irr1,
                }
            )
            new_row2 = pd.Series(
                {
                    "ID": file_list[j].split("/")[-1].split("_")[-3],
                    "Flag": qual[1],
                    "SZA": sza[1],
                    "Data": irr2,
                }
            )
            irrs = pd.concat([irrs, new_row1.to_frame().T], ignore_index=True)
            irrs = pd.concat([irrs, new_row2.to_frame().T], ignore_index=True)

    irrs.to_csv(results_path + "/%s_irradiance.csv" % tag, index=False)
    return irrs


##running

for site in SITE_PERIODS.keys():
    if site == "GHNA":
        continue
    for period in SITE_PERIODS[site]:
        print(site, period)
        tag = "%s_%s_%s" % (site, period["start_date"], period["stop_date"])
        if os.path.exists(os.path.join(results_path, f"{tag}_irradiance.csv")):
            continue
        start_time = period["start_date"]
        stop_time = period["stop_date"]
        if stop_time == "present":
            stop_time = datetime.datetime.now()

        files = glob.glob(os.path.join(data_path, f"{site}", "*", "*", "*", "*", "*L1B_IRR*.nc"))

        print("Files In")

        for ii in range(len(start_tod)):
            files = data_io.filter_files_quick(
                files, start_time, stop_time, tod_start=start_tod[ii], tod_stop=stop_tod[ii]
            )
        print("Files Sorted")

        data_clear = xr.open_dataset(files[0])
        wav_ori = data_clear.wavelength.values
        print("Got wavelengths")

        irrs = make_irrs(files, None, tag, wav_ori)
"""
data_cloud = 'T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\12\SEQ20240312T070125\HYPERNETS_L_GHNA_L1B_IRR_20240312T0701_20240416T2306_v2.0.nc'
data_clear = 'T:\ECO\EOServer\data\insitu\hypernets\\archive\GHNA\\2024\\03\\14\SEQ20240314T070025\HYPERNETS_L_GHNA_L1B_IRR_20240314T0700_20240416T1138_v2.0.nc'

irr_clear1, irr_clear2, wav_clear, qual_clear, sza_clear = get_irr(data_clear, 550)
irr_cloud1, irr_cloud2, wav_cloud, qual_cloud, sza_cloud = get_irr(data_cloud, 550)

plt.plot(wav_clear - wav_cloud)
plt.show()
"""
