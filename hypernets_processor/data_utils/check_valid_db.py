"""
post processing
"""
import numpy as np
import warnings
import os
import xarray as xr
import matplotlib as mpl
mpl.use("Agg")
import sqlite3
import matplotlib.pyplot as plt
import pysolar
from datetime import datetime as dt
import glob
from obsarray.templater.dataset_util import DatasetUtil
from hypernets_processor.plotting.plotting import Plotting


"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
refdat_path = os.path.join(dir_path, "data", "quality_comparison_data")
# archive_path = r"\\eoserver\home\data\insitu\hypernets\archive_qc"
archive_path = r"/home/data/insitu/hypernets/archive"
out_path = r"/home/data/insitu/hypernets/archive_qc_Jan2024/best_files"
plot_path = r"/home/data/insitu/hypernets/archive_qc_Jan2024/qc_plots"
plotter = Plotting("", plot_path, ".png")

bad_flags=["pt_ref_invalid", "half_of_scans_masked", "not_enough_dark_scans", "not_enough_rad_scans",
           "not_enough_irr_scans", "no_clear_sky_irradiance", "variable_irradiance",
           "half_of_uncertainties_too_big", "discontinuity_VNIR_SWIR", "single_irradiance_used"]
check_flags = ["single_irradiance_used"]

colors = ["magenta", "yellow", "cyan", "red", "green", "blue", "black", "orange", "navy", "gray", "brown",
          "greenyellow", "purple"]



def read_db_hypernets(
    hypernets_path_db, hypernets_path, site, start_date, end_date, overwrite_product_path=True, only_passed_qc=False,
):
    archive_folder = os.path.abspath(hypernets_path_db)
    dbpath = os.path.join(archive_folder, "archive.db")
    print("dbpath:",dbpath)
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

def read_hypernets_file(
    filepath,
    vza=None,
    vaa=None,
    nearest=True,
    filter_flags=True,
    max_angle_tolerance=None,
):
    ds = xr.open_dataset(filepath)
    if filter_flags:
        id_series = np.where(ds.quality_flag.values == 0)[0]
        print(
            len(id_series),
            " series selected on quality flag (out of %s total)"
            % len(ds.series.values),
        )
        ds = ds.isel(series=id_series)

        if len(id_series) == 0:
            return None

    if (vza is not None) and (vaa is not None):
        if nearest:
            angledif_series = (ds["viewing_zenith_angle"].values - vza) ** 2 + (
                np.abs(ds["viewing_azimuth_angle"].values - vaa)
            ) ** 2
            if max_angle_tolerance is not None:
                if np.min(angledif_series) > max_angle_tolerance:
                    return None
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
        return ds

    ds = ds.isel(series=id_series)
    # print(len(id_series), " series selected on angle (vza=%s, vaa=%s requested, vza=%s, vaa=%s found)"%(vza,vaa,ds["viewing_zenith_angle"].values,ds["viewing_azimuth_angle"].values))
    return ds

if __name__ == "__main__":
    sites = [
        "GHNA",
        # "WWUK",
        # "ATGE",
        # "BASP",
        # "PEAN1A",
        # "PEAN1B",
        # "PEAN1C",
        # "PEAN",
        # "DEGE",
        # "IFAR",
    ]
    hypernets_path_db = r"\\eoserver\home\data\calvalresults\v2"
    hypernets_path = r"\\eoserver\home\data\insitu\hypernets\archive"

    archive_folder = os.path.abspath(hypernets_path_db)
    dbpath = os.path.join(archive_folder, "archive.db")
    print("dbpath:", dbpath)
    engine = sqlite3.connect(dbpath)
    cursor = engine.cursor()
    query = "select * FROM products WHERE site_id='GHNA'"
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    print(len(data))
    for i in range(len(data)):
        if i%100==0:
            print(i*100/len(data),"% complete")
        row=data[i]
        path=row[8]
        product=row[1]
        #print(os.path.join(hypernets_path,path,product))
        if os.path.exists(os.path.join(hypernets_path,path,product+".nc")):
            ds = xr.open_dataset(os.path.join(hypernets_path,path,product+".nc"))
            #print(min(ds.acquisition_time.values),max(ds.acquisition_time.values))
            query = "update products set datetime_start = '%s', datetime_end = '%s' WHERE product_name='%s'" % (dt.fromtimestamp(np.nanmin(ds["acquisition_time"].values)),dt.fromtimestamp(np.nanmax(ds["acquisition_time"].values)),product)
            cursor.execute(query)
        else:
            print("not found")
            query = "delete FROM products WHERE product_name='%s'"%(product)
            cursor.execute(query)

    engine.commit()
    engine.close()


