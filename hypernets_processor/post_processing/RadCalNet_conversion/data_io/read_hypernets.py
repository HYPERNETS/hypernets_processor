import os.path
import sqlite3
import xarray as xr
import numpy as np
from obsarray.templater.dataset_util import DatasetUtil

bad_flags=["pt_ref_invalid", "half_of_scans_masked", "not_enough_dark_scans", "not_enough_rad_scans",
           "not_enough_irr_scans", "no_clear_sky_irradiance", "variable_irradiance",
           "half_of_uncertainties_too_big", "discontinuity_VNIR_SWIR", "single_irradiance_used"]

def read_db_hypernets(
    hypernets_path_db, hypernets_path, site, start_date, end_date, overwrite_product_path=True, only_passed_qc=False,
):
    archive_folder = os.path.abspath(hypernets_path_db)
    dbpath = os.path.join(archive_folder, "archive.db")
    engine = sqlite3.connect(dbpath)
    cursor = engine.cursor()
    query = make_query_hypernets(
        site_id=site, date_start=start_date, date_end=end_date, product_level="L_L2A", only_passed_qc=only_passed_qc
    )
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        raise ValueError(
            "no data found between the specified dates in the hypernets database"
        )
    if overwrite_product_path:
        for i in range(len(data)):
            data[i] = list(data[i])
            data[i][-1] = os.path.join(hypernets_path, data[i][-2], data[i][-3] + ".nc")
    return np.array(data, dtype=object)


def read_hypernets_file(filepath, vza=None, vaa=None, nearest=True, filter_flags=True):
    ds = xr.open_dataset(filepath)
    if filter_flags:
        flagged = DatasetUtil.get_flags_mask_or(ds["quality_flag"], bad_flags)
        id_series = np.where(~flagged)[0]
        print(len(id_series), " series selected on quality flag (out of %s total)"%len(ds.series.values))
        ds = ds.isel(series=id_series)

        if len(id_series) == 0:
            return None

    if (vza is not None) and (vaa is not None):
        if nearest:
            angledif_series = (ds["viewing_zenith_angle"].values - vza) ** 2 + (
                np.abs(ds["viewing_azimuth_angle"].values - vaa)
            ) ** 2
            id_series = np.where(angledif_series == np.min(angledif_series))[0]
        else:
            id_series = np.where(
                (ds["viewing_zenith_angle"].values == vza)
                & (ds["viewing_azimuth_angle"].values == vaa)
            )[0]
    elif vza is not None:
        if nearest:
            angledif_series = (ds["viewing_zenith_angle"].values - vza) ** 2
            id_series = np.where(angledif_series == np.min(angledif_series))[0]
        else:
            id_series = np.where(ds["viewing_zenith_angle"].values == vza)[0]
    elif vaa is not None:
        if nearest:
            angledif_series = (np.abs(ds["viewing_azimuth_angle"].values - vaa)) ** 2
            id_series = np.where(angledif_series == np.min(angledif_series))[0]
        else:
            id_series = np.where(ds["viewing_azimuth_angle"].values == vaa)[0]
    else:
        id_series = ds.series.values

    ds = ds.isel(series=id_series)
    print(len(id_series), " series selected on angle (vza=%s, vaa=%s requested, vza=%s, vaa=%s found)"%(vza,vaa,ds["viewing_zenith_angle"].values,ds["viewing_azimuth_angle"].values))
    return ds


def make_query_hypernets(
    sequence_id=None,
    date_start=None,
    date_end=None,
    time_start=None,
    time_end=None,
    site_id=None,
    system_id=None,
    product_level=None,
    only_passed_qc=False
):
    if sequence_id:
        cond = "sequence_name = '%s'"
        args = (sequence_id,)

    else:
        if system_id:
            cond = "system_id = '%s'"
            args = (system_id,)

        elif site_id and not site_id == "all":
            cond = "site_id = '%s'"
            args = (site_id,)
        else:
            cond = ""
            args = ()

        if date_start:
            cond += " AND date(datetime_SEQ)>= '%s'"
            args += (date_start,)
        if date_end:
            cond += " AND date(datetime_SEQ)<= '%s'"
            args += (date_end,)

        if time_start:
            cond += " AND time(datetime_SEQ)>= '%s'"
            args += (time_start,)

        if time_end:
            cond += " AND time(datetime_SEQ)<= '%s'"
            args += (date_end,)

        if product_level:
            cond += " AND product_level = '%s'"
            if product_level == "L2A":
                raise ValueError("product_level should likely be L_L2A")
            args += (product_level,)

        if cond[0:4] == " AND":
            cond = cond[4:]

        if only_passed_qc:
            cond += " AND percent_zero_flags>0"

    return (
        "SELECT sequence_name,site_id,system_id,datetime_SEQ,latitude,longitude,product_name,rel_product_dir,product_path FROM products WHERE "
        + cond % args
        + " ORDER BY datetime_SEQ"
    )
