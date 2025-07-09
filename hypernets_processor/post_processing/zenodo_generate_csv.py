import datetime

import numpy as np
import os
import glob
import matplotlib.pyplot as plt
import xarray as xr
from hypernets_processor.utils.utils import convert_datetime
# set appropriate folders (different for linux or windows) and settings

# for windows:
# data_path = r"\\eoserver\home\data\insitu\hypernets\archive"
# results_path = r"\\eoserver\home\data\insitu\hypernets\archive"

# for eoserver:
data_path = r"/home/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/archive"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)

tags = ["JSIT","GHNA_v1", "GHNA_v3", 'WWUK_2024']
sites = ["JSIT","GHNA","GHNA", 'WWUK']

start_times = ["20240409T0000","20220517T0000","20231026T0000", '20240101T0000']
stop_times = ["20250101T0000","20231018T0000","20250101T0000", '20250101T0000']

wavelength = [415, 490, 550, 665, 675, 705, 740, 765, 842, 870, 1020, 1640]
plot_wavelength = 550

# #set minimum and maximum reflectance for colourbar plots (Set to None to let it work it out automatically)
vmin = None  # 0.18
vmax = None  # 0.28

vzas = [None]  # [20,30,40]
vaas = [None]  # [83,98,113,263,278,298]

SITE_PERIODS = {
    "GHNA": [{"start_date": "2022-05-17" , "stop_date": "2023-10-17" ,"HYPSTAR_SN": 220261, "comments": "deployment period 1: v1 instrument"},{"start_date": "2023-10-20" , "stop_date": "2024-05-23" ,"HYPSTAR_SN": 222316, "comments": "deployment period 2: v3 instrument"},{"start_date": "2024-05-24" , "stop_date": "present" ,"HYPSTAR_SN": 222316, "comments": "deployment period 3: v3 instrument cleaned and realigned but not replaced/calibrated"}]
}
with open(os.path.join(results_path,'Zenodo_L2B_sequences.csv'), 'w') as f:
    f.write("#Sequence_ID,filename,start_acquisition_time,stop_acquisition_time,latitude,longitude,period comment\n")
    for site in SITE_PERIODS.keys():
        for period in SITE_PERIODS[site]:
            tag = "%s_%s_%s" % (site, period["start_date"], period["stop_date"])
            start_time = convert_datetime(period["start_date"])
            stop_time = convert_datetime(period["stop_date"])

            files = glob.glob(os.path.join(data_path, site, "*", "*", "*", "*", "*L2B*.nc"))
            for file in files:
                ds_HYP = xr.open_dataset(file)
                dt_hyp_min = convert_datetime(ds_HYP.acquisition_time.values.min())
                dt_hyp_max = convert_datetime(ds_HYP.acquisition_time.values.max())
                if (dt_hyp_min > start_time) and (dt_hyp_max < stop_time):
                    print(ds_HYP.attrs["sequence_id"],os.path.basename(file),dt_hyp_min,dt_hyp_max, ds_HYP.attrs["site_latitude"], ds_HYP.attrs["site_longitude"], period["comments"])
                    f.write("%s,%s,%s,%s,%s,%s,%s\n"%(ds_HYP.attrs["sequence_id"],os.path.basename(file),dt_hyp_min.isoformat(),dt_hyp_max.isoformat(), ds_HYP.attrs["site_latitude"], ds_HYP.attrs["site_longitude"], period["comments"]))
