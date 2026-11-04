import numpy as np
import xarray as xr
import os
import datetime
import pandas as pd

# File to read era5 data and aernonet manually downloaded from their appropriate website.
# It is noted that the current model assumes getting H2O, O3 and Pressure data from era5
# and aerosol data from aeronet, though it is possible to adjust file if other parameters are wanted from these files.
# This file currently requireds the name of the files to be inputted, but is also noted, that this code can be adapted to run from a certain directory (e.g. data file on eo server rather than a particualr file).

dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_era5_data(era5_mean, era5_spread, S2_time, lon, lat):
    """
    Function to read in the atmopsheric data form the era5 data.

    Inputs:
    era5_mean: str, path to the file containing the means of the era5 data. Currently required to be netcdf file
    era5_spread: str, path to the file containing the spread of the era5 data. Currently required to be a netcdf file
    S2_time: datetime, the time of the S2 data
    lon, lat: float, the coordinates of the hypernets site

    Outputs:
    H2O, P, O3, u_H2O, u_P, u_O3: float
    """
    # opening the data
    mean_ds = xr.open_dataset(era5_mean)
    spread_ds = xr.open_dataset(era5_spread)
    atm_lon = mean_ds.coords["longitude"].values
    atm_lat = mean_ds.coords["latitude"].values
    atm_time = mean_ds.coords["time"].values
    # Finding the closests coordinate to the point where radiance and reflectance data is measured.
    lon_min = (atm_lon - lon) ** 2
    lat_min = (atm_lat - lat) ** 2

    time_min = []
    for time in range(len(atm_time)):
        d_time = np.abs(atm_time[time] - np.datetime64(S2_time))
        time_min.append(d_time)

    lon_min_id = np.where(lon_min == np.min(lon_min))
    lat_min_id = np.where(lat_min == np.min(lat_min))
    time_min_id = np.where(time_min == np.min(time_min))
    # opening the coordinates at this point, tcwv = total column water vapour, tco3 = total column ozone, sp = surface pressure
    H2O = mean_ds["tcwv"].values[time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]]
    u_H2O = spread_ds["tcwv"].values[
        time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]
    ]
    P = (
        mean_ds["sp"].values[time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]]
        / 100
    )
    u_P = (
        spread_ds["sp"].values[time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]]
        / 100
    )
    O3 = mean_ds["tco3"].values[
        time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]
    ] / (2.1415 * 10 ** (-5))
    u_O3 = spread_ds["tco3"].values[
        time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]
    ] / (2.1415 * 10 ** (-5))
    return H2O, P, O3, u_H2O, u_P, u_O3


def read_aeronet_data(aeronet_data, S2_time):
    """
    Function to read in the atmospheric data from the aernoet data.

    Inputs:
    aeronet_data: str, path to the aernofile containing the aeronet data. Currently required to be a .txt file
    S2_time: datetime, time of the S2 passsover

    Returns:
    aerosol: float
    """
    # aeronet data is taken for location
    # finding the closest coordinate
    time_min = []
    aerosol_data = pd.read_csv(aeronet_data, on_bad_lines="skip")
    for t in range(len(aerosol_data["Time(hh:mm:ss)"])):
        date = datetime.datetime.strptime(
            aerosol_data["Date(dd:mm:yyyy)"][t], "%d:%m:%Y"
        ).date()
        time = datetime.datetime.strptime(
            aerosol_data["Time(hh:mm:ss)"][t], "%H:%M:%S"
        ).time()
        observation = datetime.datetime.combine(date, time)
        d_time = np.abs(observation - S2_time)
        time_min.append(d_time)
    time_min_id = time_min.index(min(time_min))
    # opening the data. It is noted that for aerosol data, the uncertainity is given as 0.001-0.002 for all aerosol data
    aerosol = (
        aerosol_data["AOD_500nm"][time_min_id]
        * (550 / 500) ** -aerosol_data["500-870_Angstrom_Exponent"][time_min_id]
    )
    print(
        "aod",
        aerosol,
        aerosol_data["AOD_500nm"][time_min_id],
        aerosol_data["500-870_Angstrom_Exponent"][time_min_id],
    )
    u_aerosol = 0.002
    return aerosol, u_aerosol


def read_cams_data(cams_data, S2_time, lon, lat):
    """
    Function to read in the atmospheric data from the CAMS data.

    Inputs:
    cams_data: str, path to the file containing the CAMS dta. Currently requried to  be a netcdf file
    S2_time: dattime, the time of the S2 data is recorded at.
    lon, lat: float, the coordinates of the hypernets site

    Outputs:
    aerosol, u_aerosol: float
    """
    # opening the data
    aerosol_ds = xr.open_dataset(cams_data)
    atm_lon = aerosol_ds.coords["longitude"].values
    atm_lat = aerosol_ds.coords["latitude"].values
    atm_time = aerosol_ds.coords["time"].values

    # Finding the cloest coordinate to the point where radiance and reflectance data is measured.
    lon_min = (atm_lon - lon) ** 2
    lat_min = (atm_lat - lat) ** 2

    time_min = []
    for time in range(len(atm_time)):
        d_time = np.abs(atm_time[time] - np.datetime64(S2_time))
        time_min.append(d_time)

    lon_min_id = np.where(lon_min == np.min(lon_min))
    lat_min_id = np.where(lat_min == np.min(lat_min))
    time_min_id = np.where(time_min == np.min(time_min))

    aerosol = aerosol_ds["aod550"].values[
        time_min_id[0][0], lat_min_id[0][0], lon_min_id[0][0]
    ]
    u_aerosol = aerosol * 0.1
    return aerosol, u_aerosol
