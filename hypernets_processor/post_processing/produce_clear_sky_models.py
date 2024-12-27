import numpy as np
from brdf_model import BRDFModelFactory
import hypernets_brdf_data_io as data_io
from brdf_model import Comparisons
from curepy import MCMCRetrieval, plot_trace, plot_corner
import os
import glob
import matplotlib.pyplot as plt
from pysolar.solar import *
from forts.utils.produce_example_1d import ProduceExample1D
import pytz
import xarray as xr
import pandas as pd
from scrappi.interface import (
    set_credentials,
    perform_query,
    make_query_with_tolerance,
    download_product,
    list_satellite_products_api,
    make_fs,
    generate_bounding_lat_lon
)

from scrappi.utils.download_utils import (download_and_read_ERA5, download_and_read_CAMS)

#for windows:
# data_path = r"T:\ECO\EOServer\data\insitu\hypernets\archive"
# results_path = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\irradiance"

# for eoserver:
data_path = r"/mnt/t/data/insitu/hypernets/archive"
results_path = r"/mnt/t/data/insitu/hypernets/post_processing_qc/irradiance"

if not os.path.exists(results_path):
    os.mkdir(results_path)

SITE_LOCATIONS = {
    # "ATGE": [52.466778, 12.959778],
    # "BASP": [39.049139, -2.075917],
    # "DEGE": [53.868278, 13.268556],
    "GHNA": [-23.60153, 15.12589],
    # "IFAR": [-34.592322, -58.479017],
    # "JAES": [58.281975, 27.312959],
    "JSIT": [44.874305, 11.979201],
    # "LOBE": [50.551493, 4.745911],
    # "PEAN": [-71.940128, 23.305260],
    # "WWUK": [51.777206,-1.338494],
}

SITE_ALTITUDE = {
    "GHNA": 510,
    "JSIT": 0,
}

atmosphere_type = {
    # "ATGE": "midlatitude_summer",
    # "BASP": "midlatitude_summer",
    # "DEGE": "midlatitude_summer",
    "GHNA": "midlatitude_summer",
    "IFAR": "midlatitude_summer",
    # "JAES": "midlatitude_summer",
    # "JSIT": "midlatitude_summer",
    # "LOBE": "midlatitude_summer",
    # "PEAN": "midlatitude_summer",
    # "WWUK": "midlatitude_summer",
}

aerosol_type = {
    # "ATGE": "desert",
    # "BASP": "desert",
    # "DEGE": "desert",
    "GHNA": "desert",
    "IFAR": "urban",
    # "JAES": "desert",
    # "JSIT": "desert",
    # "LOBE": "desert",
    # "PEAN": "desert",
    # "WWUK": "desert",
}

file_paths = {
    # "ATGE": [52.466778, 12.959778],
    # "BASP": [39.049139, -2.075917],
    # "DEGE": [53.868278, 13.268556],
    "GHNA": os.path.join(data_path, "GHNA", "2023", "10", "28", "SEQ20231028T090128",
                     "HYPERNETS_L_GHNA_L2A_REF_20231028T0901_20240124T1403_v2.0.nc"),
    # "IFAR": [-34.592322, -58.479017],
    # "JAES": [58.281975, 27.312959],
    "JSIT": os.path.join(data_path, "JSIT", "2024", "08", "07", "SEQ20240807T090056",
                     "HYPERNETS_L_JSIT_L2A_REF_20240807T0900_20240807T1054_v2.0.nc"),
    # "LOBE": [50.551493, 4.745911],
    # "PEAN": [-71.940128, 23.305260],
    # "WWUK": [51.777206,-1.338494],
}

start_time = "20220101T0000"
stop_time = "20230101T0000"

def combine_direct_to_diffuse_ratio_sza(site, aod, irr_files_path=None):
    files = glob.glob(os.path.join(irr_files_path,"irr_clear_%s*.nc"%site))
    files.sort()
    direct_to_diffuse_all = [xr.open_dataset(file) for file in files]
    direct_to_diffuse_subset = [direct_to_diffuse for direct_to_diffuse in direct_to_diffuse_all if direct_to_diffuse.attrs["aod"]==aod]
    szas = [direct_to_diffuse.attrs["sza"] for direct_to_diffuse in direct_to_diffuse_subset]
    comb_ds=xr.concat(direct_to_diffuse_subset,pd.Index(szas, name="sza"))
    comb_ds.to_netcdf(os.path.join(irr_files_path,"%s_clear_sky_aod%s.nc"%(site,aod)))
    return comb_ds

def interpolate_irradiance_sza(sza,ds_irr):
    ds_irr_temp = ds_irr.copy()
    ds_irr_temp["solar_irradiance_BOA"].values = ds_irr_temp["solar_irradiance_BOA"].values / np.cos(
        ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
    ds_irr_temp = ds_irr_temp.interp(sza=sza, method="linear")
    ds_irr_temp["solar_irradiance_BOA"].values = ds_irr_temp["solar_irradiance_BOA"].values * np.cos(
        ds_irr_temp["sza"].values / 180 * np.pi)
    return ds_irr_temp["solar_irradiance_BOA"].values




for site in SITE_LOCATIONS.keys():
    atmosphere_ex = {}
    atmosphere_ex["shape"] = None
    atmosphere_ex["atmosphere_type"] = atmosphere_type[site]
    atmosphere_ex["aerosol_type"] = aerosol_type[site]  # by default aerosol type is urban
    atmosphere_ex["AOD"] = -99  # by default aerosol type is urban
    atmosphere_ex["H2O"] = -99  # by default aerosol type is urban
    atmosphere_ex["O3"] = -99  # by default aerosol type is urban
    atmosphere_ex["CH4"] = -99  # by default aerosol type is urban
    atmosphere_ex["CO2"] = -99  # by default aerosol type is urban
    atmosphere_ex["P"] = -99  # by default aerosol type is urban

    lat , lon = SITE_LOCATIONS[site]

    # query = {
    #     "collections": ["COP_DEM_GLO30_DTED"],
    #     "geom": [lat - 0.25, lon - 0.25, lat + 0.25, lon + 0.25],
    #     # making sure there are at least 2 grid points in query
    # }
    #
    # products = perform_query(
    #     "eodag",
    #     query,
    #     config_dict={"config_file_path": os.path.join(results_path, "eodag.yml")},
    # )
    #
    # products.set_fs("t-drive")

    # path = download_product(
    #     "eodag",
    #     products,
    #     config_dict={"config_file_path": os.path.join(results_path, "eodag.yml")},
    # )
    # print(path)

    alt=SITE_ALTITUDE[site]

    path_era5=os.path.join(results_path, "ds_era5_%s_%s_%s.nc"%(site,start_time,stop_time))
    if os.path.exists(path_era5):
        ds_era5=xr.open_dataset(path_era5)
    else:
        ds_era5 = download_and_read_ERA5(start_time, stop_time, lat, lon, config_path=os.path.join(results_path, "eodag.yml"))

        ds_era5.to_netcdf(path_era5)

    path_cams=os.path.join(results_path, "ds_cams_%s_%s_%s.nc"%(site,start_time,stop_time))
    if os.path.exists(path_cams):
        ds_cams = xr.open_dataset(path_cams)
    else:
        ds_cams = download_and_read_CAMS(start_time, stop_time, lat, lon,
                                         config_path=os.path.join(results_path, "eodag.yml"))
        ds_cams.to_netcdf(path_cams)

    ds_HYP = data_io.read_hypernets_file(file_paths[site],
        vza=20,
    )
    ds_HYP = ds_HYP.mean(dim="series")

    forts_prod = ProduceExample1D(resolution="coarse", atmosphere=atmosphere_ex)

    for szai in np.arange(0, 90, 10):
        for aod in [0.0,0.1,0.2,0.3]:
            if os.path.exists(os.path.join(results_path, "irr_clear_sky_%s_%s_%s.nc" % (site,aod,szai))):
                continue
            else:
                ds_irr = forts_prod.produce_solar_irradiance_hypernets(
                    ds_HYP,
                    szai,
                    aod=aod,
                    h2o=ds_era5.tcwv.values.mean(),
                    O3=ds_era5.tco3.values.mean()/(2.1415*10**(-5)),
                    P=ds_era5.sp.values.mean()/100,
                    altitude=alt,
                )
                ds_irr.attrs["h2o"] = ds_era5.tcwv.values.mean()
                ds_irr.attrs["O3"] = ds_era5.tco3.values.mean()/(2.1415*10**(-5))
                ds_irr.attrs["P"] = ds_era5.sp.values.mean()/100
                ds_irr.attrs["aod"] = aod
                ds_irr.attrs["sza"] = szai
                ds_irr.attrs["altitude"] = alt

                ds_irr.to_netcdf(os.path.join(results_path, "irr_clear_sky_%s_%s_%s.nc" % (site,aod,szai)))

    for aod in [0.0, 0.1, 0.2, 0.3]:
        comb_irr_ds = combine_direct_to_diffuse_ratio_sza(site,aod,results_path)
        interpolate_irradiance_sza(13.5,comb_irr_ds)

