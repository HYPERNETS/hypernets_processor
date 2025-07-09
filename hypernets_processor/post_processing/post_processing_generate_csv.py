import datetime

import numpy as np
import hypernets_brdf_data_io as data_io
import os
import glob
import matplotlib.pyplot as plt

# set appropriate folders (different for linux or windows) and settings

# for windows:
# data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
# results_path = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc"

# for eoserver:
data_path = r"/mnt/t/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc"

# results_path = os.path.join(results_path,brdf_model)
if not os.path.exists(results_path):
    os.mkdir(results_path)

tags = ["JSIT","GHNA_v1", "GHNA_v3", 'WWUK_2024']
sites = ["JSIT","GHNA","GHNA", 'WWUK']

start_times = ["20240409T0000","20220517T0000","20231026T0000", '20240101T0000']
stop_times = ["20250101T0000","20231018T0000","20250101T0000", '20250101T0000']

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
            "stop_date": "present",
            "HYPSTAR_SN": 222317,
            "comments": "",
        },
    ],
    "JSIT": [
        {
            "start_date": "2024-04-09",
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
    ],
    # "PEAN": [],
    "WWUK": [
        {
            "start_date": "2021-11-18",
            "stop_date": "2024-01-16",
            "HYPSTAR_SN": 220251,
            "comments": "v1 instrument",
        },
        {
            "start_date": "2024-06-26",
            "stop_date": "present",
            "HYPSTAR_SN": 222314,
            "comments": "v3 instrument",
        },
    ],
}

for site in SITE_PERIODS.keys():
    for period in SITE_PERIODS[site]:
        if site != 'GHNA':
            continue
        #if period['stop_date'] == 'present':
         #   continue
        print(site, period)
        tag = "%s_%s_%s" % (site, period["start_date"], period["stop_date"])
        start_time = period["start_date"]
        stop_time = period["stop_date"]
        if stop_time == "present":
            stop_time = datetime.datetime.now()

        files = glob.glob(os.path.join(data_path, site, "*", "*", "*", "*", "*L2A*.nc"))
        print(files)
        for ii in range(len(start_tod)):
            files = data_io.filter_files_start_stop(
                files,
                start_time,
                stop_time,
                tod_start=start_tod[ii],
                tod_stop=stop_tod[ii],
            )
            print("selected", files)
            for vza in vzas:
                for vaa in vaas:
                    # read in hypernets data (which returns object of brdf_model.BRDFMeasurements)
                    HCRFmeas = data_io.read_data_hypernets(
                        files, i=None, vza=vza, vaa=vaa, mask=False
                    )

                    HCRFmeas.export_csv(
                        os.path.join(
                            results_path,
                            "%s_%s_%s_%s_%s.csv"
                            % (tag, vza, vaa, start_tod[ii], stop_tod[ii]),
                        ),
                        wavelength,
                    )

                    fig1, ax1 = plt.subplots()
                    ax1.plot(
                        HCRFmeas.get_datetimes(),
                        HCRFmeas.get_reflectance(plot_wavelength),
                        "o",
                        label="before",
                    )
                    ax1.set_xlabel("datetime")
                    ax1.set_ylabel("reflectance")
                    ax1.legend(ncol=2)
                    ax1.set_ylim([vmin, vmax])
                    fig1.savefig(
                        os.path.join(
                            results_path,
                            "refl_calibration_diff_%s_%s_%s_%s_%s_%s.png"
                            % (
                                tag,
                                vza,
                                vaa,
                                start_tod[ii],
                                stop_tod[ii],
                                plot_wavelength,
                            ),
                        )
                    )
                    plt.clf()
