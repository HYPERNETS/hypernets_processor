"""
post processing
"""
import numpy as np
import warnings
import os
import xarray as xr
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import pysolar
import datetime
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
           "half_of_uncertainties_too_big", "discontinuity_VNIR_SWIR"]
check_flags = ["single_irradiance_use"]

colors = ["red", "green", "blue", "magenta", "yellow", "cyan", "black", "orange", "navy", "gray", "brown",
          "greenyellow", "purple"]


def make_time_series_plot(
    wavs,
    times,
    measurands,
    mask,
    hour_bins,
    tag,
    sigma_thresh=3.0,
    fit_poly_n=0,
    n_max_points=0,
):
    # get a datetime that is equal to epoch
    epoch = datetime.datetime(1970, 1, 1)
    times_sec = np.array([(d - epoch).total_seconds() for d in times])
    for i in range(len(wavs)):
        measurand_wav = measurands[:, i]
        for ii in range(len(hour_bins) - 1):
            hour_ids = np.where(
                (mask == 0)
                & (
                    [
                        time_between(dt.time(), hour_bins[ii], hour_bins[ii + 1])
                        for dt in times
                    ]
                )
            )[0]
            if len(hour_ids) > 0:
                std, mean, mask_clip = sigma_clip(
                    times_sec[hour_ids],
                    measurand_wav[hour_ids],
                    tolerance=0.05,
                    median=True,
                    sigma_thresh=sigma_thresh,
                    fit_poly_n=fit_poly_n,
                    n_max_points=n_max_points,
                )
                mask[hour_ids] = mask_clip

    f = open(os.path.join(archive_path, "stats_masking.csv"), "a")
    f.write(
        "%s,%s,%s,%s,%s,%s\n"
        % (
            tag,
            len(times),
            len(times[np.where(mask == 0)[0]]),
            len(times[np.where(mask == 1)[0]]),
            len(times[np.where(mask == 2)[0]]),
            len(times[np.where(mask == 3)[0]]),
        )
    )
    f.close()
    for i in range(len(wavs)):
        measurand_wav = measurands[:, i]
        ax = plt.gca()
        for ii in range(len(hour_bins) - 1):
            hour_ids = np.where(
                ((mask == 0) | (mask == 2))
                & (
                    [
                        time_between(dt.time(), hour_bins[ii], hour_bins[ii + 1])
                        for dt in times
                    ]
                )
            )[0]
            if len(hour_ids) > 0:
                color = colors[ii]
                std, mean, mask_clip = sigma_clip(
                    times_sec[hour_ids],
                    measurand_wav[hour_ids],
                    tolerance=0.05,
                    median=True,
                    sigma_thresh=sigma_thresh,
                    fit_poly_n=fit_poly_n,
                    n_max_points=n_max_points,
                )
                print(wavs[i],"%s:00-%s:00" % (hour_bins[ii], hour_bins[ii + 1]),mean.shape, hour_ids.shape,times_sec.shape, times.shape, np.where(np.isnan(measurand_wav[hour_ids])))
                plt.plot(times[hour_ids], mean, color=color, linestyle="-")
                plt.plot(
                    times[hour_ids],
                    mean - sigma_thresh * std,
                    color=color,
                    linestyle=":",
                )
                plt.plot(
                    times[hour_ids],
                    mean + sigma_thresh * std,
                    color=color,
                    linestyle=":",
                )
                outlier_ids = np.where(
                    (mask == 2)
                    & (
                        [
                            time_between(dt.time(), hour_bins[ii], hour_bins[ii + 1])
                            for dt in times
                        ]
                    )
                )[0]
                bestdata_ids = np.where(
                    (mask == 0)
                    & (
                        [
                            time_between(dt.time(), hour_bins[ii], hour_bins[ii + 1])
                            for dt in times
                        ]
                    )
                )[0]
                plt.plot(
                    times[outlier_ids],
                    measurand_wav[outlier_ids],
                    "o",
                    color=color,
                    alpha=0.15,
                )
                plt.plot(
                    times[bestdata_ids],
                    measurand_wav[bestdata_ids],
                    "o",
                    color=color,
                    label="%s:00-%s:00" % (hour_bins[ii], hour_bins[ii + 1]),
                )

        plt.plot(
            times[np.where(mask == 1)[0]],
            measurands[np.where(mask == 1)[0], i],
            "ko",
            alpha=0.1,
            label="masked by processor",
        )
        if len(np.where(mask == 3)[0]) > 0:
            plt.plot(
                times[np.where(mask == 3)[0]],
                measurands[np.where(mask == 3)[0], i],
                "mo",
                alpha=0.1,
                label="masked by vegetation checks",
            )
        valids = measurand_wav[np.where(mask == 0)[0]]
        plt.ylim(
            [
                min(valids) - 0.3 * (max(valids) - min(valids)),
                max(1, max(valids) + 0.3 * (max(valids) - min(valids))),
            ]
        )
        plt.legend()
        plt.ylabel("reflectance")
        plt.xlabel("datetime")
        plt.savefig(os.path.join(plot_path, "qc_%s_%s.png" % (tag, wavs[i])), dpi=300)
        plt.clf()
        print("plot done ", os.path.join(plot_path, "qc_%s_%s.png" % (tag, wavs[i])))
    return mask


def time_between(time, start_hour, end_hour):
    if time < datetime.time(start_hour, 0, 0):
        return False
    elif time > datetime.time(end_hour - 1, 59, 59):
        return False
    else:
        return True


def find_files(site):
    # files=glob.glob(archive_path+r"\%s\*\*\*\*\*L2A*"%site)
    files = glob.glob(archive_path + r"/%s/*/*/*/*/*L2A*" % site)
    files = np.sort(files)
    list_ds = np.empty(len(files), dtype=object)
    for ifile, file in enumerate(files):
        list_ds[ifile] = xr.open_dataset(file)
    return files, list_ds


def extract_reflectances(files, wavs, vza, vaa, site):
    refl = np.zeros((len(files), len(wavs)))
    mask = np.ones(len(files))
    times = np.empty(len(files), dtype=datetime.datetime)
    valid = np.ones(len(files), dtype=int)
    all_ds = np.empty(len(files), dtype=object)
    for i in range(len(files)):
        ds = read_hypernets_file(
            files[i], vza=vza, vaa=vaa, filter_flags=False, max_angle_tolerance=2
        )
        if ds is None or len(ds.series)==0:
            mask[i] = 1
            times[i] = datetime.datetime.utcfromtimestamp(0)
            #print("bad angle for file:", vza, vaa, files[i])
            continue

        flagged = DatasetUtil.get_flags_mask_or(ds["quality_flag"], bad_flags)

        if len(ds.quality_flag.values) == 1:
            ids = [np.argmin(np.abs(ds.wavelength.values - wav)) for wav in wavs]
            refl[i] = ds.reflectance.values[ids, 0]
            times[i] = datetime.datetime.utcfromtimestamp(
                ds.acquisition_time.values[0],
            )

            if not flagged:
                mask[i] = 0
            else:
                print(site,times[i],ds.quality_flag.values,[DatasetUtil.get_set_flags(flag) for flag in ds["quality_flag"]],files[i])

        else:
            if not any(flagged):
                mask[i] = 0
            ids = [np.argmin(np.abs(ds.wavelength.values - wav)) for wav in wavs]
            refl[i] = np.mean(ds.reflectance.values[ids, :])
            print(ds, ds.acquisition_time.values[:])
            times[i] = datetime.datetime.utcfromtimestamp(
                np.mean(ds.acquisition_time)
            )
    return times, refl, mask

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


def sigma_clip(
    xvals,
    values,
    tolerance=0.01,
    median=True,
    sigma_thresh=3.0,
    fit_poly_n=0,
    n_max_points=0,
):
    mask = np.zeros([len(values)])

    # Remove NaNs from input values
    values = np.array(values)
    mask[np.where(np.isnan(values))]=2

    print(values.shape,xvals.shape)
    # Continue loop until result converges
    diff = 10e10
    while diff > tolerance:
        # Assess current input iteration
        # if fit_poly_n > 0:
        #     poly_coeff = np.polyfit(xvals[np.where(mask < 1)], values[np.where(mask < 1)], fit_poly_n)
        #     poly_func = np.poly1d(poly_coeff)
        #     average = poly_func(xvals)
        #     sigma_old = np.std(values[np.where(mask < 1)] - average[np.where(mask < 1)])

        if n_max_points > 0:
            average = fit_2weekbins(xvals, values, mask)
            sigma_old = np.std(values[np.where(mask < 1)] - average[np.where(mask < 1)])

        elif median == False:
            average = np.mean(values[np.where(mask < 1)]) * np.ones_like(values)
            sigma_old = np.std(values[np.where(mask < 1)])

        elif median == True:
            average = np.median(values[np.where(mask < 1)]) * np.ones_like(values)
            sigma_old = np.std(values[np.where(mask < 1)])

        # Mask those pixels that lie more than 3 stdev away from mean
        mask[np.where(values > (average + (sigma_thresh * sigma_old)))] = 2
        mask[np.where(values < (average - (sigma_thresh * sigma_old)))] = 2

        # Re-measure sigma and test for convergence
        sigma_new = np.std(values[np.where(mask < 1)] - average[np.where(mask < 1)])
        # print(sigma_old,sigma_new)
        diff = abs(sigma_old - sigma_new) / sigma_old

    return sigma_old, average, mask


def fit_binfunc(xvals, yvals, maxpoints, mask):
    nbins = int(np.ceil(len(xvals[np.where(mask < 1)]) / maxpoints))
    if nbins == 1:
        return np.mean(yvals[np.where(mask < 1)]) * np.ones_like(xvals)
    else:
        x_bin = np.zeros(nbins)
        y_bin = np.zeros(nbins)
        binpoints = int(np.ceil(len(xvals[np.where(mask < 1)]) / nbins))
        for i in range(nbins):
            x_bin[i] = np.mean(
                xvals[np.where(mask < 1)][
                    i * binpoints : min((i + 1) * binpoints, len(xvals))
                ]
            )
            y_bin[i] = np.mean(
                yvals[np.where(mask < 1)][
                    i * binpoints : min((i + 1) * binpoints, len(xvals))
                ]
            )
        return np.interp(xvals, x_bin, y_bin)


def fit_2weekbins(xvals, yvals, mask):
    week_in_sec = 604800
    x_edges = np.arange(xvals[0], xvals[-1] + 1, 2 * week_in_sec)
    x_bin = np.zeros(len(x_edges) - 1)
    y_bin = np.zeros(len(x_edges) - 1)
    for i in range(len(x_bin)):
        x_bin[i] = np.mean(
            xvals[
                np.where((mask < 1) & (xvals > x_edges[i]) & (xvals < x_edges[i + 1]))
            ]
        )
        y_bin[i] = np.mean(
            yvals[
                np.where((mask < 1) & (xvals > x_edges[i]) & (xvals < x_edges[i + 1]))
            ]
        )
    return np.interp(xvals, x_bin, y_bin)


def vegetation_checks(ds, iseries):
    b2 = ds["reflectance"].values[
        np.argmin(np.abs(ds.wavelength.values - 490)), iseries
    ]  # 490 nm
    b3 = ds["reflectance"].values[
        np.argmin(np.abs(ds.wavelength.values - 560)), iseries
    ]  # 560 nm
    b4 = ds["reflectance"].values[
        np.argmin(np.abs(ds.wavelength.values - 665)), iseries
    ]  # 665 nm
    b5 = ds["reflectance"].values[
        np.argmin(np.abs(ds.wavelength.values - 705)), iseries
    ]  # 705 nm
    b7 = ds["reflectance"].values[
        np.argmin(np.abs(ds.wavelength.values - 783)), iseries
    ]  # 783 nm
    b8 = ds["reflectance"].values[
        np.argmin(np.abs(ds.wavelength.values - 865)), iseries
    ]  # equivalent of 8a # 865 nm

    vis_test = (b2 < b3) & (b3 > b4)  # Spot the peak in the green region of the visible
    ir_test = (
        b7 > b5 * 2
    )  # reflectance in b7 must be double that of b5 ... in effect detecting the red edge?
    ndvi = (b8 - b4) / (b8 + b4)  # Calculate NDVI
    ndvi_threshold = ndvi > 0.42
    refl_threshold = b7 < 0.65 and b7 > 0.15
    # flags_combined = np.logical_and(vis_test, ir_test, ndvi_threshold)  # combine the three flags

    return vis_test and ir_test and ndvi_threshold and refl_threshold


if __name__ == "__main__":
    wavs = [500, 900, 1100, 1600]
    hour_bins = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    sites = [
        "GHNA",
        "WWUK",
        # "ATGE",
        # "BASP",
        # "PEAN1A",
        # "PEAN1B",
        # "PEAN1C",
        # "PEAN2",
        # "DEGE",
        # "IFAR",
    ]
    sites = ["WWUK"]
    sites_thresh = [2, 2, 2, 2, 2, 2, 2, 2, 3, 3]
    sites_thresh = [2]
    sites_points = [0]

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    for isite, site in enumerate(sites):
        if not os.path.exists(os.path.join(out_path, site)):
            os.makedirs(os.path.join(out_path, site))

        files, site_ds = find_files(site)
        files_nmaskedseries = np.zeros(len(files))
        for ifile in range(len(site_ds)):
            ids_wav = np.where(
                (site_ds[ifile].wavelength > 380) & (site_ds[ifile].wavelength < 1700)
            )[0]
            site_ds[ifile] = site_ds[ifile].isel(wavelength=ids_wav)
            if site == "BASP":
                ids_series = np.where((site_ds[ifile]["viewing_zenith_angle"] < 35))[0]
                site_ds[ifile] = site_ds[ifile].isel(series=ids_series)
                for vza in [5, 10]:
                    for vaa in [263, 273, 293]:
                        angledif_series = (
                            site_ds[ifile]["viewing_zenith_angle"].values - vza
                        ) ** 2 + (
                            np.abs(site_ds[ifile]["viewing_azimuth_angle"].values - vaa)
                        ) ** 2
                        ids_series = np.where(
                            angledif_series != np.min(angledif_series)
                        )[0]
                        site_ds[ifile] = site_ds[ifile].isel(series=ids_series)

        for iseries in range(len(site_ds[0].viewing_zenith_angle.values)):
            vza = round(site_ds[0].viewing_zenith_angle.values[iseries])
            vaa = round(site_ds[0].viewing_azimuth_angle.values[iseries])
            times, refl, mask = extract_reflectances(files, wavs, vza, vaa, site)
            if site == "WWUK" or site == "BASP":
                for ifile in range(len(site_ds)):
                    if not vegetation_checks(site_ds[ifile], iseries):
                        mask[ifile] = 3
            if True:
                mask2 = make_time_series_plot(
                    wavs,
                    times,
                    refl,
                    mask,
                    hour_bins,
                    "%s_%s_%s" % (site, vza, vaa),
                    n_max_points=sites_points[isite],
                    sigma_thresh=sites_thresh[isite],
                )
                for ifile in range(len(site_ds)):
                    ds_curr = site_ds[ifile]
                    ds_curr.quality_flag.attrs[
                        "flag_meanings"
                    ] = ds_curr.quality_flag.attrs["flag_meanings"].replace(
                        "placeholder1", "postprocessing_outliers"
                    )
                    if site == "WWUK":
                        ds_curr.quality_flag.attrs[
                            "flag_meanings"
                        ] = ds_curr.quality_flag.attrs["flag_meanings"].replace(
                            "placeholder1", "postprocessing_outliers"
                        )

                    if mask2[ifile] > 0:
                        ds_curr.reflectance[:, iseries] *= np.nan
                        ds_curr.u_rel_random_reflectance[:, iseries] *= np.nan
                        ds_curr.u_rel_systematic_reflectance[:, iseries] *= np.nan
                        ds_curr.std_reflectance[:, iseries] *= np.nan
                        if mask2[ifile] == 2:
                            ds_curr.quality_flag[iseries] = 16
                        files_nmaskedseries[ifile] += 1
                    site_ds[ifile] = ds_curr

            # except:
            #     print("%s_%s_%s"%(site,vza,vaa), " failed")

        f = open(os.path.join(out_path, site, site + "_sequences.csv"), "w")
        f.write("#filename, datetime, lat, lon \n")
        for ifile in range(len(site_ds)):
            if files_nmaskedseries[ifile] < len(site_ds[ifile].series) / 2:
                print(files_nmaskedseries[ifile], os.path.basename(files[ifile]))
                site_ds[ifile].to_netcdf(
                    os.path.join(out_path, site, os.path.basename(files[ifile]).replace("L2A","L2B"))
                )
                f.write(
                    "%s,%s,%s,%s \n"
                    % (
                        os.path.basename(files[ifile]),
                        times[ifile],
                        site_ds[ifile].attrs["site_latitude"],
                        site_ds[ifile].attrs["site_longitude"],
                    )
                )
                plotter.plot_series_in_sequence("reflectance", site_ds[ifile])
                # plotter.plot_series_in_sequence_vaa("reflectance", site_ds[ifile], 98)
                # plotter.plot_series_in_sequence_vza("reflectance", site_ds[ifile], 30)
        f.close()
