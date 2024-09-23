"""hypernets_brdf.subpackage_template.module_template - describe class"""

__author__ = [
    "Pieter De Vis <pieter.de.vis@npl.co.uk",
    "Morven Sinclair <morven.sinclair@npl.co.uk>",
]
__all__ = []

from brdf_model import BRDFMeasurementsSpectra

import glob
import os
import xarray as xr
from dateutil.parser import parse
import datetime
import numpy as np
from obsarray.templater.dataset_util import DatasetUtil
from typing import Optional, Union, List, Any

bad_flags=["pt_ref_invalid", "half_of_scans_masked", "not_enough_dark_scans", "not_enough_rad_scans",
           "not_enough_irr_scans", "no_clear_sky_irradiance", "variable_irradiance",
           "half_of_uncertainties_too_big", "discontinuity_VNIR_SWIR", "single_irradiance_used"]


def read_data_hypernets(
    files,
    spatial_var_percent=0,
    i=None,
    mask=True,
    vzamax=None,
    vza=None,
    vaa=None,
    filter_flags=True
) -> BRDFMeasurementsSpectra:

    """
    Function to read full HYPERNETS dataset

    :param path:
    :param start_time:
    :param stop_time:
    :return:
    """
    if i is not None:
        ds_HYP = read_hypernets_file(files[i],vza=vza,vaa=vaa,vzamax=vzamax,mask=mask,filter_flags=filter_flags)
    else:
        for ii in range(len(files)):
            ds_HYP = read_hypernets_file(files[ii],vza=vza,vaa=vaa,vzamax=vzamax,mask=mask,filter_flags=filter_flags)
            if ds_HYP is not None:
                break
    reflectance = ds_HYP["reflectance"].values
    u_rand_refl = (
        ds_HYP["u_rel_random_reflectance"].values * reflectance / 100
        + spatial_var_percent * reflectance / 100
    )
    u_syst_refl = ds_HYP["u_rel_systematic_reflectance"].values * reflectance / 100
    corr_syst_refl = ds_HYP["err_corr_systematic_reflectance"].values
    geometries = np.array(
        [
            ds_HYP["solar_zenith_angle"].values,
            ds_HYP["viewing_zenith_angle"].values,
            ds_HYP["solar_azimuth_angle"].values,
            ds_HYP["viewing_azimuth_angle"].values,
        ]
    )
    corr_reflectances_wav = np.mean([ds_HYP.unc["reflectance"][:, i].total_err_corr_matrix() for i in range(len(ds_HYP["solar_zenith_angle"].values))], axis=0)

    meas = BRDFMeasurementsSpectra(
        ds_HYP["wavelength"].values,
        geometries,
        ds_HYP["acquisition_time"].values,
        reflectance,
        u_rand_refl,
        u_syst_refl,
        corr_reflectances_wav=corr_reflectances_wav,
        ids=ds_HYP.attrs["sequence_id"]
    )

    if i is None:
        for ii in range(1, len(files)):
            ds_HYP = read_hypernets_file(files[ii], vza=vza, vaa=vaa, vzamax=vzamax, mask=mask,
                                         filter_flags=filter_flags)

            if ds_HYP is not None:
                reflectance = ds_HYP["reflectance"].values
                u_rand_refl = (
                    ds_HYP["u_rel_random_reflectance"].values * reflectance / 100
                    + spatial_var_percent * reflectance / 100
                )
                u_syst_refl = (
                    ds_HYP["u_rel_systematic_reflectance"].values * reflectance / 100
                )
                geometries = np.array(
                    [
                        ds_HYP["solar_zenith_angle"].values,
                        ds_HYP["viewing_zenith_angle"].values,
                        ds_HYP["solar_azimuth_angle"].values,
                        ds_HYP["viewing_azimuth_angle"].values,
                    ]
                )
                meas.add_measurement(
                    ds_HYP["acquisition_time"].values,
                    geometries,
                    reflectance,
                    u_rand_reflectance=u_rand_refl,
                    u_syst_reflectance=u_syst_refl,
                    id=ds_HYP.attrs["sequence_id"]
                )

    return meas

def read_hypernets_file(filepath, vza=None, vaa=None, vzamax=None, mask=True, filter_flags=True):
    ds_HYP = xr.open_dataset(filepath)
    if filter_flags:
        flagged = DatasetUtil.get_flags_mask_or(ds_HYP["quality_flag"], bad_flags)
        id_series = np.where(~flagged)[0]
        # print(len(id_series), " series selected on quality flag (out of %s total)"%len(ds.series.values))
        ds_HYP = ds_HYP.isel(series=id_series)
        if len(ds_HYP.series) == 0:
            return None

    if (vza is not None) and (vaa is not None):
        vzadiff = (ds_HYP["viewing_zenith_angle"].values - vza)
        if vza <= 2.5:
            vaadiff = (np.abs(ds_HYP["viewing_azimuth_angle"].values - vaa % 180) % 180)
        else:
            vaadiff = (np.abs(ds_HYP["viewing_azimuth_angle"].values - vaa % 360))
        angledif_series = vzadiff ** 2 + vaadiff ** 2
        id_series = np.where(angledif_series == np.min(angledif_series))[0]

    elif vza is not None:
        angledif_series = (ds_HYP["viewing_zenith_angle"].values - vza) ** 2
        id_series = np.where(angledif_series == np.min(angledif_series))[0]

    elif vaa is not None:
        angledif_series = (np.abs(ds_HYP["viewing_azimuth_angle"].values - vaa % 360)) ** 2
        id_series = np.where(angledif_series == np.min(angledif_series))[0]

    else:
        id_series = ds_HYP.series.values
    ds_HYP = ds_HYP.isel(series=id_series)

    if vzamax is not None:
        ds_HYP = ds_HYP.isel(series=np.where(ds_HYP["viewing_zenith_angle"].values < vzamax)[0])

    if mask:
        ds_HYP = mask_HYPERNETS_BRDF(ds_HYP)

    if len(ds_HYP.series)>0:
        return ds_HYP


def filter_files_start_stop(files, start_time, stop_time, tod_start=None, tod_stop=None):
    start_time = convert_datetime(start_time)
    stop_time = convert_datetime(stop_time)
    files_out = []

    if tod_start is not None:
        tod_start = datetime.datetime.strptime(tod_start, '%H%M').time()

    if tod_stop is not None:
        tod_stop = datetime.datetime.strptime(tod_stop, '%H%M').time()

    for file in files:
        ds_HYP = xr.open_dataset(file)
        times=[datetime.datetime.utcfromtimestamp(timestamp) for timestamp in ds_HYP["acquisition_time"].values]
        if (
            min(times) > start_time
            and max(times) < stop_time
        ):
            if (tod_start is None or min(times).time() > tod_start) and (tod_stop is None or max(times).time() < tod_stop):
                files_out.append(file)
    return files_out


def mask_HYPERNETS_BRDF(ds_HYP):

    # mask_boom
    mask_shadow = np.where(~((ds_HYP["viewing_azimuth_angle"].values > 345)|(ds_HYP["viewing_azimuth_angle"].values < 15)))[0]
    ds_HYP = ds_HYP.isel(series=mask_shadow)


    # mask feet and mast here using bitwise operators such as: | for or , & for and
    mask_shadow = np.where(
        ~(
            (
                (ds_HYP["viewing_azimuth_angle"].values > 225)
                | (ds_HYP["viewing_azimuth_angle"].values < 90)
            )
            & (ds_HYP["viewing_zenith_angle"].values < 15)
        )
    )[0]
    ds_HYP = ds_HYP.isel(series=mask_shadow)

    mask_shadow = np.where(
        ~(
            (
                (ds_HYP["viewing_azimuth_angle"].values > 300)
                | (ds_HYP["viewing_azimuth_angle"].values < 60)
            )
            & (ds_HYP["viewing_zenith_angle"].values < 25)
        )
    )[0]
    ds_HYP = ds_HYP.isel(series=mask_shadow)


    # mask sun shadow

    mask_shadow = np.where(
        ~(
            (
                np.abs(
                    ds_HYP["viewing_azimuth_angle"].values
                    - ds_HYP["solar_azimuth_angle"].values
                )
                < 10
            )
            & (
                ds_HYP["viewing_zenith_angle"].values
                < ds_HYP["solar_zenith_angle"].values + 5
            )
        )
    )[0]
    ds_HYP = ds_HYP.isel(series=mask_shadow)

    #additional mask for specific additional mast anomalies (AM)
    mask_shadow = np.where(
       ~(
            (
                (ds_HYP["viewing_azimuth_angle"].values > 15)
                & (ds_HYP["viewing_azimuth_angle"].values < 30)
            )
            & (ds_HYP["viewing_zenith_angle"].values < 30)
       )
    )[0]
    ds_HYP = ds_HYP.isel(series=mask_shadow)

    #additional mask for single additional high anomaly (PM)
    mask_shadow = np.where(
       ~(
            (
                (ds_HYP["viewing_azimuth_angle"].values > 285)
                & (ds_HYP["viewing_azimuth_angle"].values < 300)
            )
            & (ds_HYP["viewing_zenith_angle"].values < 15)
       )
    )[0]
    ds_HYP = ds_HYP.isel(series=mask_shadow)

    return ds_HYP


def read_data_hypernets_sequence(self, path):
    """
    Function to read single HYPERNETS sequence

    :param path:
    :return:
    """

    pass


def read_data_CIMEL(self, path, start_time, stop_time) -> BRDFMeasurementsSpectra:
    """
    Function to read CIMEL dataset

    :param path:
    :param start_time:
    :param stop_time:
    :return:
    """

    pass


def read_data_CIMEL_ASCII(self, path):
    """
    Function to read single CIMEL ASCII file

    :param path:
    :return:
    """

    pass


def convert_datetime(
    date_time: Union[datetime.datetime, datetime.date, str, float, int, np.ndarray]
) -> datetime.datetime:
    """
    Convert input datetimes to a datetime object

    :param date_time: date time to convert to a datetime object
    :return: datetime object corresponding to input date_time
    """
    if isinstance(date_time, np.ndarray):
        return np.array([convert_datetime(date_time_i) for date_time_i in date_time])
    elif isinstance(date_time, datetime.datetime):
        return date_time
    elif isinstance(date_time, datetime.date):
        return datetime.datetime.combine(date_time, datetime.time())
    elif isinstance(date_time, np.datetime64):
        unix_epoch = np.datetime64(0, "s")
        one_second = np.timedelta64(1, "s")
        seconds_since_epoch = (date_time - unix_epoch) / one_second
        return datetime.datetime.utcfromtimestamp(seconds_since_epoch)
    elif isinstance(date_time, (float, int, np.uint)):
        return datetime.datetime.utcfromtimestamp(date_time)
    else:
        if date_time[-1] == "Z":
            date_time = date_time[:-1]
        try:
            return parse(date_time, fuzzy=False)
        except ValueError:
            raise ValueError(
                "Unable to discern datetime requested: '{}'".format(date_time)
            )

if __name__ == "__main__":
    pass
