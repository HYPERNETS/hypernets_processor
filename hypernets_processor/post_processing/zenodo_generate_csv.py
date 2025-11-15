import datetime

import numpy as np
import os
import glob
import matplotlib.pyplot as plt
import xarray as xr
from hypernets_processor.utils.utils import convert_datetime

# set appropriate folders (different for linux or windows) and settings

local_fs=True

if local_fs:
    # for local windows machine
    data_path = r"C:\Users\pdv\data\insitu\hypernets\archive_L2B"
    results_path = r"C:\Users\pdv\data\insitu\hypernets\postprocessing\zenodo"

# for windows:
# data_path = r"\\eoserver\home\data\insitu\hypernets\archive"
# results_path = r"\\eoserver\home\data\insitu\hypernets\archive"

# for eoserver:
# data_path = r"/home/data/insitu/hypernets/archive"
# results_path = r"/mnt/t/data/insitu/hypernets/archive"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)

sites = ["LOBE", "JAES","JSIT", "GHNA", "WWUK"]

start_times = ["20220101T0000", "20220101T0000","20220101T0000","20220101T0000","20220101T0000"]
stop_times = ["20251001T0000", "20251001T0000","20251001T0000","20251001T0000","20251001T0000"]

SITE_PERIODS = {
    "ATGE": [{"start_date": "2022-10-16" , "stop_date": "2024-05-02" ,"HYPSTAR_SN": 221231, "valid": False, "comments": ""}],
    "BASP": [{"start_date": "2022-07-18" , "stop_date": "2022-07-22" ,"HYPSTAR_SN": 221233, "valid": False, "comments": "v2 instrument"}],
    "DEGE": [{"start_date": "2021-07-29" , "stop_date": "2023-10-24" ,"HYPSTAR_SN": 220241, "valid": False, "comments": ""}],
    "GHNA": [{"start_date": "2022-05-17" , "stop_date": "2023-10-17" ,"HYPSTAR_SN": 220261, "valid": True, "comments": "v1 instrument"},{"start_date": "2023-10-20" , "stop_date": "2024-05-23" ,"HYPSTAR_SN": 222316, "valid": True, "comments": "v3 instrument"},{"start_date": "2024-05-24" , "stop_date": "2025-03-27" ,"HYPSTAR_SN": 222316, "valid": True, "comments": "instrument cleaned and realigned but not replaced/calibrated"},{"start_date": "2025-03-27" , "stop_date": "2025-09-27" ,"HYPSTAR_SN": 222316, "valid": False, "comments": "Grassy period following rain event (also affected by some pan angle offset error)"}, {"start_date": "2025-10-15" , "stop_date": "present" ,"HYPSTAR_SN": 220251, "valid": False, "comments": "instrument replaced, not enough data yet for valid L2B QC"}],
    "IFAR": [{"start_date": "2022-06-17", "stop_date": "2022-10-12" ,"HYPSTAR_SN": 221211, "valid": False, "comments": ""},{"start_date": "2023-08-04" , "stop_date": "2024-08-03" ,"HYPSTAR_SN": 221211, "valid": False, "comments": "Calibration E: 2023-01-25, L: 2023-01-27"}],
    "JAES": [{"start_date": "2023-04-14", "stop_date": "2023-05-11" ,"HYPSTAR_SN": 221461, "valid": False, "comments": "invalid period for L2B due to site heterogeneity, 2023-05-20 leaves on (subjective judgement); 2023-09-19 cleaned optics; 2023-10-18 first snow, leaves off"},{"start_date": "2023-05-11", "stop_date": "2023-09-07" ,"HYPSTAR_SN": 221461, "valid": True, "comments": "2023-05-20 leaves on (subjective judgement); 2023-09-19 cleaned optics; 2023-10-18 first snow, leaves off"},{"start_date": "2023-09-07", "stop_date": "2024-05-09" ,"HYPSTAR_SN": 221461, "valid": False, "comments": "invalid period for L2B due to site heterogeneity, 2023-05-20 leaves on (subjective judgement); 2023-09-19 cleaned optics; 2023-10-18 first snow, leaves off"},{"start_date": "2024-06-05", "stop_date": "2024-09-04" ,"HYPSTAR_SN": 221461, "valid": True, "comments": "homogeneous period"}, {"start_date": "2024-09-04", "stop_date": "2024-11-13" ,"HYPSTAR_SN": 221461, "valid": False, "comments": "invalid period for cal/val due to site heterogeneity"}, {"start_date": "2024-11-13", "stop_date": "2025-05-01" ,"HYPSTAR_SN": 222317, "valid": False, "comments": "invalid period for cal/val due to site heterogeneity"},{"start_date": "2025-05-01", "stop_date": "2025-06-16" ,"HYPSTAR_SN": 222317, "valid": True, "comments": "homogeneous period"}, {"start_date": "2025-06-16", "stop_date": "2025-07-04" ,"HYPSTAR_SN": 221461, "valid": False, "comments": "invalid due to site heterogeneity, swapped radiometer (was 222317, now 221461); LED source (was 422361 (but reported 3230503), now 323051); rain sensor and monitor PD assembly"},{"start_date": "2025-07-04", "stop_date": "2025-09-03" ,"HYPSTAR_SN": 221461, "valid": True, "comments": "swapped radiometer (was 222317, now 221461); LED source (was 422361 (but reported 3230503), now 323051); rain sensor and monitor PD assembly"}, {"start_date": "2025-09-03", "stop_date": "present" ,"HYPSTAR_SN": 221461, "valid": False, "comments": "invalid due to site heterogeneity, swapped radiometer (was 222317, now 221461); LED source (was 422361 (but reported 3230503), now 323051); rain sensor and monitor PD assembly"}],
    "JSIT": [{"start_date": "2024-04-09", "stop_date": "2024-11-16" ,"HYPSTAR_SN": 222315, "valid": False, "comments": "soybean (sowing date 08/04/2023); lot of spatial variability (likely due to field disturbance during deployment) resulting in this data not being suitable for satellite validation."},{"start_date": "2024-11-27", "stop_date": "2025-03-10" ,"HYPSTAR_SN": 222315, "valid": False, "comments": "growing period, unsuitable for cal/val due to site heterogeneity, durum wheat"},{"start_date": "2025-03-10", "stop_date": "2025-07-01" ,"HYPSTAR_SN": 222315, "valid": True, "comments": "durum wheat; Anti-fungal treatments on April 2nd, 2025 between 15:00 and 15:30; Field has been affected by lodging starting from May 8th-9th, 2025"}, {"start_date": "2025-07-02", "stop_date": "2025-08-01" ,"HYPSTAR_SN": 222315, "valid": True, "comments": "fallow field with residues/weeds."}, {"start_date": "2025-08-01", "stop_date": "present" ,"HYPSTAR_SN": 222315, "valid": False, "comments": "fallow field with residues/weeds. Period too short for QC and site heterogeneous."}],
    "LOBE":  [{"start_date": "2023-05-31", "stop_date": "2023-08-11", "lat": 50.55149, "lon": 4.74591, "HYPSTAR_SN": 222312, "valid": False, "comments": "Potato crop, furrowed ground; Non-standard sequence used, all data has quality flag `vza_irradiance' raised, not enough data for L2B processing"}, {"start_date": "2024-05-17", "stop_date": "2024-07-17", "lat": 50.55151 , "lon": 4.74601,"HYPSTAR_SN": 222312, "valid": True, "comments": "Winter Wheat crop, Flat soil surface"}, {"start_date": "2024-10-05", "stop_date": "2024-11-13", "lat": 50.55151 , "lon": 4.74601,"HYPSTAR_SN": 222312, "valid": True, "comments": "Cover crop, Flat soil surface"}, {"start_date": "2025-04-15", "stop_date": "2025-05-03", "lat": 50.55151 , "lon": 4.74601,"HYPSTAR_SN": 222312, "valid": True, "comments": "Bare soil surface"}, {"start_date": "2025-05-03", "stop_date": "2025-06-03", "lat": 50.55151 , "lon": 4.74601,"HYPSTAR_SN": 222312, "valid": False, "comments": "Growing season, site heterogeneity too high for L2B processing"}, {"start_date": "2025-06-03", "stop_date": "present", "lat": 50.55151 , "lon": 4.74601,"HYPSTAR_SN": 222312, "valid": True, "comments": "Sugar beet roots, Flat soil surface"}],    
    "PEAN": [{"start_date": "2022-01-26" , "stop_date": "2022-02-08" ,"HYPSTAR_SN": 221233, "valid": False, "comments": "Disturbed surface due to deployment. A crossbar for additional stability was installed on 2022-01-31. Improvement of north orientation was attempted 2022-02-01. Powered by 10 ft container equipped with solar and backup generator, located south of the instrument (visible in S2 imagery)."},{"start_date": "2022-12-25" , "stop_date": "2023-02-02" ,"HYPSTAR_SN": 221233, "valid": False, "comments": "Natural snow surface, with small scale relief changing with wind and snow. Powered by 10 ft container equipped with solar and backup generator, located south of the instrument (visible in S2 imagery)."},{"start_date": "2023-12-30" , "stop_date": "2024-01-23" ,"HYPSTAR_SN": 222313, "valid": False, "comments": "Natural snow surface, with small scale relief changing with wind and snow. Power to the instrument was flaky in the first few days, with several measurements/days missing. More reliable measurements from 2024-01-09."}],
    "WWUK":  [{"start_date": "2021-11-18" , "stop_date": "2022-05-05" ,"HYPSTAR_SN": 220251, "valid": False, "comments": "v1 instrument, winter data too heterogenious"} ,{"start_date": "2022-05-05" , "stop_date": "2022-10-11" ,"HYPSTAR_SN": 220251, "valid": True, "comments": "v1 instrument, summer"} ,{"start_date": "2022-10-11" , "stop_date": "2023-04-29" ,"HYPSTAR_SN": 220251, "valid": False, "comments": "v1 instrument,  winter data too heterogenious"} ,{"start_date": "2023-04-29" , "stop_date": "2023-11-01" ,"HYPSTAR_SN": 220251, "valid": True, "comments": "v1 instrument, summer"}, {"start_date": "2023-11-01" , "stop_date": "2024-06-26" ,"HYPSTAR_SN": 220251, "valid": False, "comments": "v1 instrument, winter data too heterogenious"},{"start_date": "2024-06-26" , "stop_date": "present" ,"HYPSTAR_SN": 222314, "valid": False, "comments": "v3 instrument, too few clear-sky measurements for reliable QC"}],
}

for site in SITE_PERIODS.keys():
    with open(os.path.join(results_path, "Zenodo_L2B_sequences_%s.csv" % site), "w") as f:
        f.write(
        "#Sequence_ID,filename,start_acquisition_time,stop_acquisition_time,latitude,longitude,period comment\n"
        )
        for period in SITE_PERIODS[site]:
            tag = "%s_%s_%s" % (site, period["start_date"], period["stop_date"])
            start_time = convert_datetime(period["start_date"])
            stop_time = convert_datetime(period["stop_date"])

            if local_fs:
                files = glob.glob(
                    os.path.join(data_path, site, "*L2B*.nc")
                )
            else:
                files = glob.glob(
                    os.path.join(data_path, site, "*", "*", "*", "*", "*L2B*.nc")
                )
            for file in files:
                ds_HYP = xr.open_dataset(file)
                dt_hyp_min = convert_datetime(ds_HYP.acquisition_time.values.min())
                dt_hyp_max = convert_datetime(ds_HYP.acquisition_time.values.max())
                if (dt_hyp_min > start_time) and (dt_hyp_max < stop_time):
                    print(
                        ds_HYP.attrs["sequence_id"],
                        os.path.basename(file),
                        dt_hyp_min,
                        dt_hyp_max,
                        ds_HYP.attrs["site_latitude"],
                        ds_HYP.attrs["site_longitude"],
                        period["comments"],
                    )
                    f.write(
                        "%s,%s,%s,%s,%s,%s,%s\n"
                        % (
                            ds_HYP.attrs["sequence_id"],
                            os.path.basename(file),
                            dt_hyp_min.isoformat(),
                            dt_hyp_max.isoformat(),
                            ds_HYP.attrs["site_latitude"],
                            ds_HYP.attrs["site_longitude"],
                            period["comments"],
                        )
                    )
