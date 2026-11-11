import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os

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


def interpolate_irradiance_sza(sza, ds_irr, variable):
    ds_irr_temp = ds_irr.copy()
    ds_irr_temp[variable].values = (
        ds_irr_temp[variable].values
        / np.cos(np.float64(ds_irr_temp["sza"].values) / 180 * np.pi)[:, None]
    )
    ds_irr_temp = ds_irr_temp.interp(sza=sza, wavelength=wav, method="linear")
    ds_irr_temp[variable].values = ds_irr_temp[variable].values * np.cos(
        np.float64(ds_irr_temp["sza"].values) / 180 * np.pi
    )
    return ds_irr_temp[variable].values


def modelled_data_read_and_interp(sza, mod_data, variable):
    sza = float(sza)
    interp_mod_data = interpolate_irradiance_sza(sza, mod_data, variable)
    return interp_mod_data



def write_irr_analysis_files(
    filename, wavelengths
):
    site = filename.split("\\")[-1].split("_")[0]
    irradiance = pd.read_csv(filename)
    szas = irradiance["SZA"]
    IDs = irradiance["ID"]
    saas = irradiance["SAA"]
    clear_sky_model = xr.open_dataset(
                    "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance\{}_clear_sky_medianaod.nc".format(
                        site
                    )
                )
    data = np.zeros((irradiance.shape[0], len(irradiance.columns) - 4))
    for j in range(irradiance.shape[0]):
        for i in range(len(irradiance.columns) - 4):
            data[j, i] = irradiance["{}".format(i)][j]

    output_data = pd.DataFrame(
        {
            "IDs": IDs,
            "SZA": szas,
            "SAA": saas,
            "Time": [x[9:14] for x in IDs],
            "Date": [x[0:8] for x in IDs],
            "Flag": irradiance["Flag"],
        }
    )
    for wv in wavelengths:
        model = np.zeros(output_data.shape[0])
        observ = np.zeros(output_data.shape[0])
        dir_to_diff = np.zeros(output_data.shape[0])

        for i in range(output_data.shape[0]):
            model[i] = find_nearest_to_wav(
                modelled_data_read_and_interp(
                    szas[i], clear_sky_model, "solar_irradiance_BOA"
                ),
                wav,
                wv,
            )
        
            observ[i] = find_nearest_to_wav(data[i, :], wav, wv)
            dir_to_diff[i] = find_nearest_to_wav(
                modelled_data_read_and_interp(
                    szas[i],
                    clear_sky_model,
                    "direct_to_diffuse_irradiance_ratio",
                ),
                wav,
                wv,
            )

        output_data[f"model_{wv}nm"] = model
        output_data[f"obs_{wv}nm"] = observ
        output_data[f"dir_diff_ratio_{wv}nm"] = dir_to_diff
        output_data[f"ratio_{wv}nm"] = model / observ

        fig, ax = plt.subplots(
            1,
            1,
        )
        ax.scatter(output_data['Date'], output_data.where(output_data['Flag'] != 0)[f'ratio_{wv}nm'], color = 'r', alpha = 0.3)
        ax.scatter(output_data['Date'], output_data.where(output_data['Flag'] == 0)[f'ratio_{wv}nm'], color = 'g', alpha = 0.5)
        fig.savefig(
            r"T:\ECO\EOServer\joe\hypernets_plots\meteor_processing\{}_irr_ratio_{}.png".format(
                site, wv
            )
        )
        plt.close()
        fig, ax = plt.subplots(
                    1,
                    1,
                )
        ax.scatter(output_data['Date'], output_data.where(output_data['Flag'] == 0)[f'ratio_{wv}nm'], color = 'g', alpha = 0.5)
        fig.savefig(
            r"T:\ECO\EOServer\joe\hypernets_plots\meteor_processing\{}_irr_ratio_pass_{}.png".format(
                site, wv
            )
        )
        plt.close()

    output_data = output_data.where(output_data['Flag'] == 0).dropna()
    output_data.to_csv(filename.replace(".csv", "_analysis.csv"))

data_folder = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\meteor_reprocessing"

for filename in os.listdir(data_folder):
    if filename.endswith("irradiance.csv"):
        print(f"Processing file: {filename}")
        if filename.replace(".csv", "_analysis.csv") in os.listdir(data_folder):
            print(f"Analysis file already exists for {filename}, skipping...")
            continue
        write_irr_analysis_files(
            os.path.join(data_folder, filename),
            [415, 490, 550, 665, 675, 705, 740, 765, 842, 870, 1020, 1640],
        )
