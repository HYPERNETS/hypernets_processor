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


def combine_direct_to_diffuse_ratio_sza(
    site,
    aod,
    irr_files_path=None,
    median_aod=False,
    tag="",
):
    files = set(glob.glob(
        os.path.join(irr_files_path, "irr_clear_sky_%s*%s.nc" % (site, tag))
    ))
    excluded = set(glob.glob(
        os.path.join(irr_files_path, "irr_clear_sky_%s*comb%s.nc" % (site, tag))
    ))

    files= sorted(files-excluded)
    direct_to_diffuse_all = [xr.open_dataset(file) for file in files]
    direct_to_diffuse_subset = [
        direct_to_diffuse.drop_vars("sza")
        for direct_to_diffuse in direct_to_diffuse_all
        if direct_to_diffuse.attrs["aod"] == aod
    ]
    szas = [
        direct_to_diffuse.attrs["sza"] for direct_to_diffuse in direct_to_diffuse_subset
    ]

    comb_ds = xr.concat(direct_to_diffuse_subset, pd.Index(szas, name="sza"))
    comb_ds.attrs["aod"] = aod
    if median_aod:
        comb_ds.to_netcdf(
            os.path.join(irr_files_path, "%s_clear_sky_medianaod%s.nc" % (site, tag))
        )
    else:
        comb_ds.to_netcdf(
            os.path.join(irr_files_path, "%s_clear_sky_aod%s%s.nc" % (site, aod, tag))
        )
    return comb_ds


def interpolate_irradiance_sza(sza, ds_irr):
    ds_irr_temp = ds_irr.copy()
    ds_irr_temp["irradiance"].values = (
        ds_irr_temp["irradiance"].values
        / np.cos(ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
    )
    ds_irr_temp = ds_irr_temp.interp(sza=sza, method="linear")
    ds_irr_temp["irradiance"].values = ds_irr_temp[
        "irradiance"
    ].values * np.cos(ds_irr_temp["sza"].values / 180 * np.pi)
    return ds_irr_temp

for site in SITE_LOCATIONS.keys():
    lat, lon = SITE_LOCATIONS[site]

    if os.path.exists(os.path.join(results_path, "atmosphere_%s_%s_%s.nc" % (site, start_time, stop_time))):
        ds_atm = xr.open_dataset(os.path.join(results_path, "atmosphere_%s_%s_%s.nc" % (site, start_time, stop_time)))
    else:
        ds = at.get_variables(
        variables=["surface_pressure", "total_column_water_vapour", "total_column_ozone", "aerosol_optical_depth"],
        roi=(lon-0.75, lat-0.75, lon+0.75,  lat+0.75),  # (lon_min, lat_min, lon_max, lat_max)
        roi_crs_epsg="EPSG:4326",  # default; roi can be given in any CRS
        time_range= (start_time, stop_time),  # (start_time, end_time)
        )
        ds_atm = ds.interp(latitude=lat, longitude=lon)
        ds_atm.to_netcdf(os.path.join(results_path, "atmosphere_%s_%s_%s.nc" % (site, start_time, stop_time)))

    if run_RT:
        ds_HYP_irr = read(
                    file_paths_irr[site],
                )
        ds_HYP_irr = ds_HYP_irr.mean(dim="series")

        ds_HYP = read(
            file_paths[site],
            subset={"angle": {"vza": {"nearest": 20, "tolerance": 1}}},
        )
        ds_HYP = ds_HYP.mean(dim="series")
       
        alt = SITE_ALTITUDE[site]

        median_aod = np.median(ds_atm.aerosol_optical_depth.values)

        for aod in [0.0, 0.1, 0.2, 0.3, median_aod]:
            for szai in np.arange(0, 90, 10):
                if os.path.exists(
                    os.path.join(
                        results_path,
                        "irr_clear_sky_%s_%s_%s%s.nc" % (site, aod, szai, tag),
                    )
                ):
                    continue
                else:
                    context = SceneForgeContext(str(yaml_path))
                    context["atmosphere"]["vertical_profiles"]["values"] = atmosphere_type[site]
                    context["atmosphere"]["aerosols"]["values"] = aerosol_type[site]

                    ds_irr = run_BOA_irradiance_simulation_basics(context, 
                                                                  ds_HYP, 
                                                                  ds_atm.total_column_water_vapour.values.mean(), 
                                                                  ds_atm.total_column_ozone.values.mean(), 
                                                                  ds_atm.surface_pressure.values.mean(), 
                                                                  aod, 
                                                                  h2o_unit=ds_atm.total_column_water_vapour.attrs["units"], 
                                                                  o3_unit=ds_atm.total_column_ozone.attrs["units"], 
                                                                  p_unit=ds_atm.surface_pressure.attrs["units"], 
                                                                  sza = szai, 
                                                                  saa = 0, 
                                                                  lat=lat, 
                                                                  lon=lon, 
                                                                  ds_SRF = ds_HYP_irr, 
                                                                  dem=alt)
    
                                     
            
                    # result.assign_coords(datetime=context["scene"]["datetime"]).expand_dims("datetime")                
                    # ds_comb = xr.concat(ds_list, dim="datetime")
                    # ds_comb.to_netcdf(os.path.join(context["output"]["output_path"],"irradiances_%s_%s.nc"%(start_time, stop_time)))
                    
                    ds_irr.attrs["h2o"] = ds_atm.total_column_water_vapour.values.mean()
                    ds_irr.attrs["O3"] = ds_atm.total_column_ozone.values.mean() / (
                        2.1415 * 10 ** (-5)
                    )
                    ds_irr.attrs["P"] = ds_atm.surface_pressure.values.mean() / 100
                    ds_irr.attrs["aod"] = aod
                    ds_irr.attrs["sza"] = szai
                    ds_irr.attrs["altitude"] = alt

                    ds_irr.to_netcdf(
                        os.path.join(
                            results_path,
                            "irr_clear_sky_%s_%s_%s%s.nc" % (site, aod, szai, tag),
                        )
                    )

            if aod == median_aod:
                comb_irr_ds = combine_direct_to_diffuse_ratio_sza(
                    site, aod, results_path, median_aod=True, tag=tag
                )
            else:
                comb_irr_ds = combine_direct_to_diffuse_ratio_sza(
                    site, aod, results_path, tag=tag
                )
            comb_irr_ds = interpolate_irradiance_sza(13.5, comb_irr_ds)
            print(comb_irr_ds)
            comb_irr_ds.to_netcdf(
                os.path.join(
                    results_path, "irr_clear_sky_%s_%s_comb%s.nc" % (site, aod, tag)
                )
            )
