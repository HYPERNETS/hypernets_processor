import datetime

import numpy as np
import hypernets_processor.post_processing.L2B_postprocessing.hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib.pyplot as plt
from eoio import read_multi
import pandas as pd

def export_csv(meas, path, wavs, model_refl=None):
    if isinstance(wavs, (int, float)):
        wavs = [wavs]

    if model_refl is not None and len(model_refl) != len(wavs):
        model_refl = [model_refl]

    table = np.empty((0, len(meas.get_datetimes())))
    header = ""
    if meas.ds.ids is not None:
        header += "id, "
        table = np.vstack(
            [table, meas.ds.ids]
        )

    if meas.get_datetimes() is not None:
        header += "acquisition_time, "
        table = np.vstack(
            [table, meas.get_datetimes()]
        )

        header += "doy, "
        table = np.vstack(
            [table, [dt.strftime('%j') for dt in meas.get_datetimes()]]
        )

        header += "tod, "
        table = np.vstack(
            [table, [float(dt.strftime('%H')) + float(dt.strftime('%M')) / 60 for dt in meas.get_datetimes()]]
        )

    if meas.get_angles() is not None:
        header += "sza, vza, saa, vaa, "
        table = np.vstack(
            [table, meas.get_angles()]
        )

    for iw in range(len(wavs)):
        header += "refl_%snm, " % wavs[iw]
        table = np.vstack(
            [table, meas.get_reflectance(wavs[iw])]
        )
        if model_refl is not None:
            header += "percent_residual_%snm, " % wavs[iw]
            table = np.vstack(
                [table, (meas.get_reflectance(wavs[iw]) - model_refl[iw]) / meas.get_reflectance(wavs[iw]) * 100]
            )

    np.savetxt(path, table.T, delimiter=",", header=header[:-2], fmt='%s')


# set appropriate folders (different for linux or windows) and settings

# for windows:
# data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
# results_path = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc"

# for eoserver:
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
data_path = r"/mnt/t/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc/meteor_reprocessing"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)

# tags = ["JSIT","GHNA_v1", "GHNA_v3", 'WWUK_2024']
# sites = ["JSIT","GHNA","GHNA", 'WWUK']

# start_times = ["20240409T0000","20220517T0000","20231026T0000", '20240101T0000']
# stop_times = ["20250101T0000","20231018T0000","20250101T0000", '20250101T0000']

tags = ["GHNA_v3", "WWUK_2024"]
sites = ["GHNA", "WWUK"]

start_times = ["20231026T0000", "20240101T0000"]
stop_times = ["20250101T0000", "20250101T0000"]

wavelength = [415, 490, 550, 665, 675, 705, 740, 765, 842, 870, 1020, 1640]
plot_wavelength = 550


# start_tod = ["0900","0930","1000","1030","1100"]
# stop_tod = ["0930","1000","1030","1100","1130"]
#
# start_tod = ["0900","1000","1100"]
# stop_tod = ["1000","1100","1200"]

start_tod = [None]
stop_tod = [None]

# #set minimum and maximum reflectance for colourbar plots (Set to None to let it work it out automatically)
vmin = None  # 0.18
vmax = None  # 0.28

vzas = [None]  # [20,30,40]
vaas = [None]  # [83,98,113,263,278,298]

from hypernets_processor.post_processing.L2B_postprocessing.site_periods import SITE_PERIODS

from pathlib import Path
import pandas as pd

def get_files_for_period(base_path, site, start_date, stop_date):
    files = []

    dates = pd.date_range(start_date, stop_date, freq="D")

    for d in dates:
        day_path = (
            Path(base_path)
            / site
            / f"{d.year:04d}"
            / f"{d.month:02d}"
            / f"{d.day:02d}"
        )

        if day_path.exists():
            files.extend(day_path.rglob("*L2A*.nc"))

    return [str(f) for f in files]

for site in SITE_PERIODS.keys():
    if site == 'GHNA':
        continue
    for period in SITE_PERIODS[site]:

        print(site, period)
        tag = "%s_%s_%s" % (site, period["start_date"], period["stop_date"])
        start_time = period["start_date"]
        stop_time = period["stop_date"]
        if stop_time == "present":
            stop_time = datetime.datetime.now()

        all_files = get_files_for_period(
            data_path,
            site,
            start_time,
            stop_time
        )
        print(all_files)
        for ii in range(len(start_tod)):
            files = data_io.filter_files_quick(
                all_files,
                start_time,
                stop_time,
                tod_start=start_tod[ii],
                tod_stop=stop_tod[ii],
            )
            print("selected", files)
            for vza in vzas:
                for vaa in vaas:
                    if os.path.exists(os.path.join(results_path, f"{tag}_{vza}_{vaa}.nc")):
                        print("Already processed, skipping")
                        continue
                    # read in hypernets data (which returns object of brdf_model.BRDFMeasurements)
                    ds = read_multi(files, 
                                    vars_sel = {
                                        "meas": ["reflectance"], 
                                        "aux": ["viewing_zenith_angle", "viewing_azimuth_angle", "solar_zenith_angle", "solar_azimuth_angle", "acquisition_time"]
                                        }, 
                                    read_params = {"include_uncertainties": False}, 
                                    subset= {"wavelength": {"min": 540, "max": 850}},
                                    processors={"populate_grid": {"reference_grid": r"/mnt/t/data/insitu/hypernets/grids/viewing_angles_standard_sequence.nc"}},
                                    concat_coord = "product_datetime")
                    ds = ds.where(ds.quality_flag == 0)
                    ds = ds.assign_coords(time=pd.DatetimeIndex(ds.time.values).tz_localize(None))
                    ds = ds.drop_attrs()
                    ds.to_netcdf(os.path.join(results_path, f"{tag}_{vza}_{vaa}.nc"))