from datetime import datetime

import xarray as xr
import pandas as pd
import numpy as np

import numpy as np
import pandas as pd
import xarray as xr

import numpy as np
import pandas as pd
import xarray as xr
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os
from scipy.stats import binned_statistic_2d
from scipy.ndimage import gaussian_filter
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator


RAA_BINS = [
    (30, 90),
    (90, 150),
    (150, 210),
    (210, 270),
    (270, 330),
    (330, 30),
]

RAA_NAMES = [
    "30_90",
    "90_150",
    "150_210",
    "210_270",
    "270_330",
    "330_30",
]


# =============================================================================
# Dataset conversion
# =============================================================================

def new_plane_fit(input_sza, input_vza, input_refl, plane_type="quad", count=None):
    x = input_sza
    y = input_vza
    z = input_refl

    if plane_type == "quad":
        popt, pcov = curve_fit(quad_plane, (x, y), z, nan_policy="omit", sigma=count)

    return popt, pcov


def quad_plane(xy, a, b, c, d, e, f):
    x, y = xy
    return a + b * x + c * y + d * x**2 + e * y**2 + f * x * y

def percentile95(array):
    return np.nanpercentile(array, 95)


def percentile5(array):
    return np.nanpercentile(array, 5)


def percentile2_5(array):
    return np.nanpercentile(array, 2.5)


def percentile97_5(array):
    return np.nanpercentile(array, 97.5)


def percentile1(array):
    return np.nanpercentile(array, 1)


def percentile99(array):
    return np.nanpercentile(array, 99)


def percentile_3sigma_min(array):
    return np.nanpercentile(array, 0.3)


def percentile_3sigma_max(array):
    return np.nanpercentile(array, 99.7)


def sza_vza_bin_and_calc(
    data, cutting_data, stat, bound, input_data=None, input_wav="550"
):
    sza = data["sza"].values
    vza = data["vza"].values
    refl = data[f"refl"].values
    cutting_refl = cutting_data[f"refl"].values
    cutting_sza = cutting_data["sza"].values
    cutting_vza = cutting_data["vza"].values

    bins = [
        0,
        2.5,
        7.5,
        12.5,
        17.5,
        22.5,
        27.5,
        32.5,
        37.5,
        42.5,
        47.5,
        52.5,
        57.5,
        62.5,
        67.5,
        72.5,
        77.5,
        82.5,
        87.5,
    ]
    bin_centers = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

    sza_bin_idx = []
    vza_bin_idx = []

    for j in range(len(cutting_sza)):
        for i in range(len(bins)):
            if bins[i] <= cutting_sza[j] < bins[i + 1]:
                sza_bin_idx.append(i)
            if bins[i] <= cutting_vza[j] < bins[i + 1]:
                vza_bin_idx.append(i)

    if stat == "median":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, "median", bins, expand_binnumbers=True
        )
    elif stat == "95th":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile95, bins, expand_binnumbers=True
        )
    elif stat == "5th":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile5, bins, expand_binnumbers=True
        )
    elif stat == "2.5th":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile2_5, bins, expand_binnumbers=True
        )
    elif stat == "97.5th":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile97_5, bins, expand_binnumbers=True
        )
    elif stat == "1st":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile1, bins, expand_binnumbers=True
        )
    elif stat == "99th":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile99, bins, expand_binnumbers=True
        )
    elif stat == "3sigma_min":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile_3sigma_min, bins, expand_binnumbers=True
        )
    elif stat == "3sigma_max":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, percentile_3sigma_max, bins, expand_binnumbers=True
        )
    elif stat == "count":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, "count", bins, expand_binnumbers=True
        )
    elif stat == "std":
        binned_data, x, y, b = binned_statistic_2d(
            sza, vza, refl, "std", bins, expand_binnumbers=True
        )
    elif stat == "median_plus_3std":
        binned_std, x, y, b = binned_statistic_2d(
            sza, vza, refl, "std", bins, expand_binnumbers=True
        )
        binned_median, x, y, b = binned_statistic_2d(
            sza, vza, refl, "median", bins, expand_binnumbers=True
        )
        binned_data = binned_median + 3 * binned_std
    elif stat == "median_minus_3std":
        binned_std, x, y, b = binned_statistic_2d(
            sza, vza, refl, "std", bins, expand_binnumbers=True
        )
        binned_median, x, y, b = binned_statistic_2d(
            sza, vza, refl, "median", bins, expand_binnumbers=True
        )
        binned_data = binned_median - 3 * binned_std
    else:
        print("stat not supported")
        binned_data, x, y, b = None, None, None, None

    if input_data is not None:
        binned_data = input_data

    refl_output = []
    sza_output = []
    vza_output = []

    if bound == "lower":
        bound_passes = [
            False if v < binned_data[sza_bin_idx[i], vza_bin_idx[i]] else True
            for i, v in enumerate(cutting_refl)
        ]
    elif bound == "upper":
        bound_passes = [
            False if v > binned_data[sza_bin_idx[i], vza_bin_idx[i]] else True
            for i, v in enumerate(cutting_refl)
        ]
    else:
        print("bound must be upper or lower")
        bound_passes = None

    for i in range(len(bin_centers)):
        for j in range(len(bin_centers)):
            if not np.isnan(binned_data[i][j]):
                refl_output.append(binned_data[i][j])
                sza_output.append(bin_centers[i])
                vza_output.append(bin_centers[j])

    return refl_output, sza_output, vza_output, bound_passes, binned_data


def ds_to_df(ds):

    df = (
        ds[
            [
                "reflectance",
                "solar_zenith_angle",
                "viewing_zenith_angle",
                "relative_azimuth_angle",
            ]
        ]
        .to_dataframe()
        .reset_index()
    )

    df = df.rename(
        columns={
            "reflectance": "refl",
            "solar_zenith_angle": "sza",
            "viewing_zenith_angle": "vza",
            "relative_azimuth_angle": "raa",
        }
    )

    df = df.dropna(
        subset=[
            "refl",
            "sza",
            "vza",
            "raa",
        ]
    )

    return df


# =============================================================================
# RAA selection
# =============================================================================

def select_raa(df, bounds):

    low, high = bounds

    if low < high:
        return df[
            (df["raa"] >= low)
            & (df["raa"] < high)
        ].copy()

    return df[
        (df["raa"] >= low)
        | (df["raa"] < high)
    ].copy()


# =============================================================================
# Bounds pass
# =============================================================================

def bounds_iteration(df):

    good_list = []
    out_list = []

    for raa_bounds in RAA_BINS:

        sub = select_raa(df, raa_bounds)

        if len(sub) < 100:
            continue

        (
            binned95,
            bin_centers_sza,
            bin_centers_vza,
            upper_passes,
            _
        ) = sza_vza_bin_and_calc(
            sub,
            sub,
            "median_plus_3std",
            "upper",
        )

        (
            binned5,
            _,
            _,
            lower_passes,
            _
        ) = sza_vza_bin_and_calc(
            sub,
            sub,
            "median_minus_3std",
            "lower",
        )

        if len(binned5) < 6:
            continue

        lower_coeffs, _ = new_plane_fit(
            bin_centers_sza,
            bin_centers_vza,
            binned5,
            plane_type="quad",
        )

        upper_coeffs, _ = new_plane_fit(
            bin_centers_sza,
            bin_centers_vza,
            binned95,
            plane_type="quad",
        )

        lower_plane = quad_plane(
            (
                sub["sza"].values,
                sub["vza"].values,
            ),
            *lower_coeffs,
        )

        upper_plane = quad_plane(
            (
                sub["sza"].values,
                sub["vza"].values,
            ),
            *upper_coeffs,
        )

        mask = (
            (sub["refl"] > lower_plane)
            &
            (sub["refl"] < upper_plane)
        )

        good_list.append(sub[mask])
        out_list.append(sub[~mask])

    good = pd.concat(good_list, ignore_index=True)
    outliers = pd.concat(out_list, ignore_index=True)

    return good, outliers


# =============================================================================
# Plane std pass
# =============================================================================

def plane_std_iteration(df, save_bounds=False):
    bounds_dict = {}
    good_list = []
    out_list = []

    bins = [
        0,
        2.5,
        7.5,
        12.5,
        17.5,
        22.5,
        27.5,
        32.5,
        37.5,
        42.5,
        47.5,
        52.5,
        57.5,
        62.5,
        67.5,
        72.5,
    ]

    bin_cents = [
        (bins[i] + bins[i + 1]) / 2
        for i in range(len(bins) - 1)
    ]

    for raa_bounds in RAA_BINS:

        sub = select_raa(df, raa_bounds)

        if len(sub) < 100:
            continue

        (
            std_vals,
            std_sza,
            std_vza,
            _,
            _
        ) = sza_vza_bin_and_calc(
            sub,
            sub,
            "std",
            "na",
        )

        (
            med_vals,
            med_sza,
            med_vza,
            _,
            _
        ) = sza_vza_bin_and_calc(
            sub,
            sub,
            "median",
            "na",
        )

        (
            count_vals,
            count_sza,
            count_vza,
            _,
            _
        ) = sza_vza_bin_and_calc(
            sub,
            sub,
            "count",
            "na",
        )

        sza_fit = []
        vza_fit = []
        std_fit = []
        med_fit = []

        valid = (
            (~np.isnan(std_vals))
            &
            (~np.isnan(med_vals))
            &
            (np.array([c for c in count_vals if c != 0]) >= 3)
        )

        sza_fit = np.array(std_sza)[valid]
        vza_fit = np.array(std_vza)[valid]
        std_fit = np.array(std_vals)[valid]
        med_fit = np.array(med_vals)[valid]

        if len(med_fit) < 6:
            print("Too few points to fit use bounds only")
            return sub, pd.DataFrame()

        # always quadratic as requested

        std_coeffs, _ = new_plane_fit(
            sza_fit,
            vza_fit,
            std_fit,
            plane_type="quad",
        )

        med_coeffs, _ = new_plane_fit(
            sza_fit,
            vza_fit,
            med_fit,
            plane_type="quad",
        )

        med_plane = quad_plane(
            (
                sub["sza"].values,
                sub["vza"].values,
            ),
            *med_coeffs,
        )

        std_plane = quad_plane(
            (
                sub["sza"].values,
                sub["vza"].values,
            ),
            *std_coeffs,
        )

        std_plane = np.where(
            std_plane < 0.03 * med_plane,
            0.03 * med_plane,
            std_plane,
        )

        upper_bound = med_plane + 3 * std_plane
        lower_bound = med_plane - 3 * std_plane

        mask = (
            (sub["refl"].values > lower_bound)
            &
            (sub["refl"].values < upper_bound)
        )

        good_data = sub.loc[mask].copy()
        bad_data = sub.loc[~mask].copy()

        good_list.append(good_data)
        out_list.append(bad_data)
        
        if save_bounds:
            sza_grid = np.arange(2.5, 87.5, 5)
            vza_grid = np.arange(2.5, 87.5, 5)

            SZA, VZA = np.meshgrid(
                sza_grid,
                vza_grid,
                indexing="ij"
            )

            med_grid = quad_plane(
                (SZA, VZA),
                *med_coeffs,
            )

            std_grid = quad_plane(
                (SZA, VZA),
                *std_coeffs,
            )

            std_grid = np.maximum(
                std_grid,
                0.03 * med_grid,
            )

            bounds_dict[str(raa_bounds)] = xr.Dataset(
                data_vars=dict(
                    lower_bound=(
                        ("sza", "vza"),
                        med_grid - 3 * std_grid,
                    ),
                    upper_bound=(
                        ("sza", "vza"),
                        med_grid + 3 * std_grid,
                    ),
                ),
                coords=dict(
                    sza=sza_grid,
                    vza=vza_grid,
                ),
            )

    if len(good_list) == 0:
        return pd.DataFrame(), pd.DataFrame()

    good_df = pd.concat(
        good_list,
        ignore_index=True,
    )

    if len(out_list):
        out_df = pd.concat(
            out_list,
            ignore_index=True,
        )
    else:
        out_df = pd.DataFrame()
        
    

    return good_df, out_df, bounds_dict


# =============================================================================
# Final plotting
# =============================================================================

def plot_final_results(good, outliers, plot_path):

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    ax.scatter(
        good["sza"],
        good["refl"],
        s=2,
        alpha=0.3,
        c="green",
        label="Good",
    )

    ax.scatter(
        outliers["sza"],
        outliers["refl"],
        s=2,
        alpha=0.3,
        c="red",
        label="Outlier",
    )

    ax.set_xlabel("SZA")
    ax.set_ylabel("Reflectance")

    ax.legend()

    plt.tight_layout()
    plt.savefig(plot_path)


# =============================================================================
# Main processing function
# =============================================================================

def run_plane_filter(ds, nc_path, plot_path):

    df = ds_to_df(ds)

    all_outliers = []

    # --------------------------------------------------
    # bounds x 3
    # --------------------------------------------------

    for iteration in range(3):

        print(
            f"Bounds iteration {iteration+1}"
        )

        df, outliers = bounds_iteration(df)

        all_outliers.append(outliers)

    # --------------------------------------------------
    # plane_std_fit x 3
    # --------------------------------------------------

    for iteration in range(3):

        print(
            f"Plane STD iteration {iteration+1}"
        )
        
        save = (iteration == 2)

        df, outliers, bounds_ds = plane_std_iteration(df, save_bounds=save)

        all_outliers.append(outliers)

    # --------------------------------------------------
    # plot ONCE at end
    # --------------------------------------------------

    all_outliers = pd.concat(
        all_outliers,
        ignore_index=True,
    )

    plot_final_results(
        df,
        all_outliers,
        plot_path
    )

    # --------------------------------------------------
    # convert back to xarray
    # --------------------------------------------------

    keep_index = pd.MultiIndex.from_frame(
        df[
            [
                "time",
                "series",
            ]
        ]
    )

    original = (
        ds.to_dataframe()
        .reset_index()
    )

    original_index = pd.MultiIndex.from_frame(
        original[
            [
                "time",
                "series",
            ]
        ]
    )

    original["keep"] = (
        original_index.isin(
            keep_index
        )
    )

    good_ds = (
        original[original["keep"]]
        .drop(columns="keep")
        .set_index(
            [
                "time",
                "series",
            ]
        )
        .to_xarray()
    )

    outlier_ds = (
        original[~original["keep"]]
        .drop(columns="keep")
        .set_index(
            [
                "time",
                "series",
            ]
        )
        .to_xarray()
    )
    
    raa_ds = []

    for raa_name, ds_bound in bounds_ds.items():

        ds_bound = ds_bound.expand_dims(
            raa=[raa_name]
        )

        raa_ds.append(ds_bound)

    xr.concat(
        raa_ds,
        dim="raa",
    ).to_netcdf(nc_path)


    return good_ds, outlier_ds, bounds_ds


data_path = "T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\meteor_reprocessing\GHNA_2025-10-15_present_None_None.nc"
print('starting to open dataset')
ds = xr.open_dataset(data_path)
irr_ds = pd.read_csv(data_path.replace("_None_None.nc", "_irradiance_analysis.csv"))
print('dataset opened')

irr = xr.Dataset({"sza": (["time"], irr_ds.SZA.values), 
                  "saa": (["time"], irr_ds.SAA.values), 
                  "irr": (["time"], irr_ds["obs_550nm"].values), 
                  "ratio": (["time"], irr_ds["ratio_550nm"].values)}, 
                 coords = {"time": [datetime.strptime(d, "%Y%m%dT%H%M") for d in irr_ds.IDs.values]})

# Unique irradiance times
irr_unique_times = pd.Index(irr.time.values).unique()

# Mapping: time -> id
time_to_id = pd.Series(
    np.arange(len(irr_unique_times)),
    index=irr_unique_times
)

# Assign ID to every irr record
irr = irr.assign_coords(
    irr_id=("time", time_to_id.loc[irr.time.values].values)
)

# Match each ds time to nearest unique irr time
nearest_ids = pd.Index(irr_unique_times).get_indexer(
    ds.time.values,
    method="nearest",
    tolerance=pd.Timedelta("15min")
)

# Assign matched irr_id to ds
ds = ds.assign_coords(
    irr_id=("time", nearest_ids)
)
'''
refl_842 = ds.sel(wavelength = 842, method = 'nearest')['reflectance']
refl_665 = ds.sel(wavelength = 665, method = 'nearest')['reflectance']
print('Calculating NDVI...')
ndvi = (refl_842 - refl_665) / (refl_842 + refl_665)

print('NDVI values:')
print(ndvi)
'''
sza_limit = 60
raa_limit = 10


ds = ds.sel(time = slice("2025-10-15", "2026-07-20"))
ds = ds.sel(wavelength = 550, method = 'nearest')
ds['relative_azimuth_angle'] = (ds['viewing_azimuth_angle'] - ds['solar_azimuth_angle'] + 360) % 360

ds = ds.where((ds['solar_zenith_angle'] < sza_limit) & ((ds['relative_azimuth_angle'] > raa_limit) & (ds['relative_azimuth_angle'] < 360 - raa_limit)), drop=True)

#cloud check
ds = ds.where(ds.irr_id.isin(np.unique(irr.where(irr.ratio > 0.9, drop = True)["irr_id"])), drop = True)

bounds_folder = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\meteor_reprocessing\bounds"
plots_folder = r"T:\ECO\EOServer\data\insitu\hypernets\post_processing_qc\meteor_reprocessing\plots"
if not os.path.exists(bounds_folder):
    os.makedirs(bounds_folder)
if not os.path.exists(plots_folder):
    os.makedirs(plots_folder)
good_ds, outlier_ds, bounds_ds = run_plane_filter(ds,
                                                  os.path.join(bounds_folder, data_path.split('\\')[-1].replace('_None_None.nc', '_bounds.nc')),
                                                  os.path.join(plots_folder, data_path.split('\\')[-1].replace('_None_None.nc', '_final_results.png')))
print(ds)

##to do

# run plane fitter on final ds
# get bounds file for config