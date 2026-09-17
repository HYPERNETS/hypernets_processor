import numpy as np
import hypernets_brdf_data_io as data_io
import os
import glob
from pysolar.solar import *
import xarray as xr
import pandas as pd
from scene_forge import run_RT, SceneForgeContext
from scene_forge.utils.helpers import run_BOA_irradiance_simulation_basics
import ancillary_tools as at
from eoio import read
import numpy as np
import xarray as xr

# for windows:
data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
results_path = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance"
results_path2 = os.path.dirname(__file__)

# for eoserver:
data_path = r"/mnt/t/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc/scene_forge_irradiance"

yaml_path = os.path.join(results_path, "example_hypernets_BOA.yaml")

if not os.path.exists(results_path):
    os.mkdir(results_path)

SITE_LOCATIONS = {
    # "ATGE": [52.466778, 12.959778],
    # # "BASP": [39.049139, -2.075917],
    # "DEGE": [53.868278, 13.268556],
    "GHNA": [-23.60153, 15.12589],
    # "IFAR": [-34.592322, -58.479017],
    "JAES": [58.281975, 27.312959],
    "JSIT": [44.874305, 11.979201],
    "LOBE": [50.551493, 4.745911],
    "PEAN": [-71.940128, 23.305260],
    "WWUK": [51.777206, -1.338494],
    "SPAR": [-33.81329, -59.88987],
}

SITE_ALTITUDE = {
    "ATGE": 0.045,
    "DEGE": 0.022,
    "GHNA": 0.510,
    "JSIT": 0,
    "JAES": 0.045,
    "IFAR": 0.021,
    "LOBE": 0.168,
    "PEAN": 1.297,
    "WWUK": 0.125,
    "SPAR": 0.031,
}

atmosphere_type = {
    "ATGE": "midlatitude_summer",
    "BASP": "midlatitude_summer",
    "DEGE": "midlatitude_summer",
    "GHNA": "midlatitude_summer",
    "IFAR": "midlatitude_summer",
    "JAES": "midlatitude_summer",
    "JSIT": "midlatitude_summer",
    "LOBE": "midlatitude_summer",
    "PEAN": "midlatitude_summer",
    "WWUK": "midlatitude_summer",
    "SPAR": "midlatitude_summer",
}

aerosol_type = {
    "ATGE": "continental_average",
    "BASP": "continental_average",
    "DEGE": "continental_average",
    "GHNA": "desert",
    "JSIT": "continental_average",
    "JAES": "continental_average",
    "IFAR": "continental_average",
    "LOBE": "continental_average",
    "PEAN": "antarctic",
    "WWUK": "continental_average",
    "SPAR": "continental_average",
}

file_paths = {
    # "ATGE": [52.466778, 12.959778],
    # "BASP": [39.049139, -2.075917],
    # "DEGE": [53.868278, 13.268556],
    "GHNA": os.path.join(
        data_path,
        "GHNA",
        "2023",
        "10",
        "28",
        "SEQ20231028T090128",
        "HYPERNETS_L_GHNA_L2A_REF_20231028T0901_20240124T1403_v2.0.nc",
    ),
    # "IFAR": [-34.592322, -58.479017],
    "JAES": os.path.join(
        data_path,
        "JAES",
        "2024",
        "08",
        "08",
        "SEQ20240808T090049",
        "HYPERNETS_L_JAES_L2A_REF_20240808T0900_20240906T0650_v2.1.nc",
    ),
    "JSIT": os.path.join(
        data_path,
        "JSIT",
        "2024",
        "08",
        "07",
        "SEQ20240807T090056",
        "HYPERNETS_L_JSIT_L2A_REF_20240807T0900_20240807T1054_v2.0.nc",
    ),
    "LOBE": os.path.join(
        data_path,
        "LOBE",
        "2024",
        "07",
        "11",
        "SEQ20240711T100125",
        "HYPERNETS_L_LOBE_L2A_REF_20240711T1001_20240711T1423_v2.0.nc",
    ),
    "PEAN": os.path.join(
        data_path,
        "PEAN",
        "2022",
        "01",
        "29",
        "SEQ20220129T070017",
        "HYPERNETS_L_PEAN_L2A_REF_20220129T0700_20240112T0725_v2.0.nc",
    ),
    "WWUK": os.path.join(
        data_path,
        "WWUK",
        "2022",
        "04",
        "26",
        "SEQ20220426T113243",
        "HYPERNETS_L_WWUK_L2A_REF_20220426T1132_20240101T1641_v2.0.nc",
    ),
    "SPAR": os.path.join(
            data_path,
            "SPAR",
            "2026",
            "05",
            "04",
            "SEQ20260504T150055",
            "HYPERNETS_L_SPAR_L2A_REF_20260504T1500_20260504T1830_v2.2.nc",
        ),
}

file_paths_irr = {
    "GHNA": os.path.join(
        data_path,
        "GHNA",
        "2023",
        "10",
        "28",
        "SEQ20231028T090128",
        "HYPERNETS_L_GHNA_L1B_IRR_20231028T0901_20240124T1403_v2.0.nc",
    ),
    # "IFAR": [-34.592322, -58.479017],
    "JAES": os.path.join(
        data_path,
        "JAES",
        "2024",
        "08",
        "08",
        "SEQ20240808T090049",
        "HYPERNETS_L_JAES_L1B_IRR_20240808T0900_20240906T0650_v2.1.nc",
    ),
    "JSIT": os.path.join(
        data_path,
        "JSIT",
        "2024",
        "08",
        "07",
        "SEQ20240807T090056",
        "HYPERNETS_L_JSIT_L1B_IRR_20240807T0900_20240807T1054_v2.0.nc",
    ),
    "LOBE": os.path.join(
        data_path,
        "LOBE",
        "2024",
        "07",
        "11",
        "SEQ20240711T100125",
        "HYPERNETS_L_LOBE_L1B_IRR_20240711T1001_20240711T1423_v2.0.nc",
    ),
    "PEAN": os.path.join(
        data_path,
        "PEAN",
        "2022",
        "01",
        "29",
        "SEQ20220129T070017",
        "HYPERNETS_L_PEAN_L1B_IRR_20220129T0700_20240112T0725_v2.0.nc",
    ),
    "WWUK": os.path.join(
        data_path,
        "WWUK",
        "2022",
        "04",
        "26",
        "SEQ20220426T113243",
        "HYPERNETS_L_WWUK_L1B_IRR_20220426T1132_20240101T1641_v2.0.nc",
    ),
    "SPAR": os.path.join(
        data_path,
        "SPAR",
        "2026",
        "05",
        "04",
        "SEQ20260504T150055",
        "HYPERNETS_L_SPAR_L1B_IRR_20260504T1500_20260504T1830_v2.2.nc",
    ),
}
start_time = "20240101T0000"
stop_time = "20251231T0000"

run_RT = True

tag = "irrwav"
tag = "_" + tag


for site in SITE_LOCATIONS.keys():
    lat, lon = SITE_LOCATIONS[site]

    if os.path.exists(os.path.join(results_path, "atmosphere_%s_%s_%s.nc" % (site, start_time, stop_time))):
        ds_atm = xr.open_dataset(os.path.join(results_path, "atmosphere_%s_%s_%s.nc" % (site, start_time, stop_time)))
        ds_atm2 = xr.open_dataset(os.path.join(results_path2, "atmosphere_%s_%s_%s.nc" % (site, start_time, stop_time)))
    
    #compare (plot) the irradiances at the different sza for the different sites
    