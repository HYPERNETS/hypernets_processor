"""
post processing
"""
import numpy as np
import warnings
import os
import xarray as xr
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pysolar
import datetime
import glob

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "04/11/2020"
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
refdat_path = os.path.join(dir_path, "data", "quality_comparison_data")
# archive_path = r"\\eoserver\home\data\insitu\hypernets\archive_qc"
archive_path = r"/home/data/insitu/hypernets/archive_qc"



def make_time_series_plot(wavs,times, measurands, mask, hour_bins, tag):
    for i in range(len(wavs)):
        measurand_wav=measurands[:,i]
        for ii in range(len(hour_bins)-1):
            hour_ids=np.where((mask==0) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
            std, mean =sigma_clip(measurand_wav[hour_ids], tolerance=0.01, median=True, sigma_thresh=2.0)
            ids_outliers=np.where((mask==0) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]) & ((measurand_wav>mean+2*std) | (measurand_wav<mean-2*std)))[0]
            mask[ids_outliers]=2

    print(tag,len(times),len(times[np.where(mask==0)[0]]),len(times[np.where(mask==1)[0]]),len(times[np.where(mask==2)[0]]))
    for i in range(len(wavs)):
        measurand_wav=measurands[:,i]
        ax = plt.gca()
        for ii in range(len(hour_bins)-1):
            color = next(ax._get_lines.prop_cycler)['color']
            hour_ids=np.where((mask!=1) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
            std, mean =sigma_clip(measurand_wav[hour_ids], tolerance=0.01, median=True, sigma_thresh=2.0)
            print(wavs[i],"%s:00-%s:00" % (hour_bins[ii], hour_bins[ii + 1]),mean,std)
            plt.axhline(y=mean, color=color, linestyle='-')
            plt.axhline(y=mean-2*std, color=color, linestyle=':')
            plt.axhline(y=mean+2*std, color=color, linestyle=':')
            outlier_ids=np.where((mask==2) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
            bestdata_ids=np.where((mask==0) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
            plt.plot(times[outlier_ids], measurand_wav[outlier_ids], "o", color=color,
                     alpha=0.3)
            plt.plot(times[bestdata_ids], measurand_wav[bestdata_ids], "o", color=color,
                     label="%s:00-%s:00" % (hour_bins[ii], hour_bins[ii + 1]))

        plt.plot(times[np.where(mask==1)[0]],measurands[np.where(mask==1)[0],i],"ko",alpha=0.1,label="masked by processor")
        valids=measurand_wav[np.where(mask==0)[0]]
        plt.ylim([min(valids)-0.1,max(valids)+0.1])
        plt.legend()
        plt.ylabel("reflectance")
        plt.xlabel("datetime")
        plt.savefig(os.path.join(archive_path,"qc_plots","qc_%s_%s.png"%(tag,wavs[i])), dpi=300)
        plt.clf()
        print("plot done ", os.path.join(archive_path,"qc_plots","qc_%s_%s.png"%(tag,wavs[i])))

def time_between(time,start_hour,end_hour):
    if time<datetime.time(start_hour,0,0):
        return False
    elif time>datetime.time(end_hour-1,59,59):
        return False
    else:
        return True


def extract_reflectances(site, wavs, vza, vaa):
    # files=glob.glob(archive_path+r"\%s\*\*\*\*\*L2A*"%site)
    files=glob.glob(archive_path+r"/%s/*/*/*/*/*L2A*"%site)
    refl=np.zeros((len(files),len(wavs)))
    mask=np.ones(len(files))
    times=np.empty(len(files),dtype=datetime.datetime)
    for i in range(len(files)):
        ds=read_hypernets_file(files[i],vza=vza, vaa=vaa, filter_flags=False,max_angle_tolerance=2)
        if ds is None:
            continue
        if ds.quality_flag.values == 0:
            mask[i]=0
        ids=[np.argmin(np.abs(ds.wavelength.values-wav)) for wav in wavs]
        refl[i]=ds.reflectance.values[ids,0]
        times[i]=datetime.datetime.fromtimestamp(ds.acquisition_time.values[0])
    return times[np.where(times is not None)[0]], refl[np.where(times is not None)[0]], mask[np.where(times is not None)[0]]

def read_hypernets_file(filepath, vza=None, vaa=None, nearest=True, filter_flags=True, max_angle_tolerance=None):
    ds = xr.open_dataset(filepath)
    if filter_flags:
        id_series = np.where(ds.quality_flag.values == 0)[0]
        print(len(id_series), " series selected on quality flag (out of %s total)"%len(ds.series.values))
        ds = ds.isel(series=id_series)

        if len(id_series) == 0:
            return None

    if (vza is not None) and (vaa is not None):
        if nearest:
            angledif_series = (ds["viewing_zenith_angle"].values - vza) ** 2 + (
                np.abs(ds["viewing_azimuth_angle"].values - vaa)
            ) ** 2
            if max_angle_tolerance is not None:
                if np.min(angledif_series)>max_angle_tolerance:
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
        id_series = ds.series.values

    ds = ds.isel(series=id_series)
    #print(len(id_series), " series selected on angle (vza=%s, vaa=%s requested, vza=%s, vaa=%s found)"%(vza,vaa,ds["viewing_zenith_angle"].values,ds["viewing_azimuth_angle"].values))
    return ds

def sigma_clip(values, tolerance=0.01, median=True, sigma_thresh=3.0):
    # Remove NaNs from input values
    values = np.array(values)
    values = values[np.where(np.isnan(values) == False)]
    values_original = np.copy(values)

    # Continue loop until result converges
    diff = 10e10
    while diff > tolerance:
        # Assess current input iteration
        if median == False:
            average = np.mean(values)
        elif median == True:
            average = np.median(values)
        sigma_old = np.std(values)

        # Mask those pixels that lie more than 3 stdev away from mean
        check = np.zeros([len(values)])
        check[np.where(values > (average + (sigma_thresh * sigma_old)))] = 1
        # check[ np.where( values<(average-(sigma_thresh*sigma_old)) ) ] = 1
        values = values[np.where(check < 1)]

        # Re-measure sigma and test for convergence
        sigma_new = np.std(values)
        diff = abs(sigma_old - sigma_new) / sigma_old

    # Perform final mask
    check = np.zeros([len(values)])
    check[np.where(values > (average + (sigma_thresh * sigma_old)))] = 1
    check[np.where(values < (average - (sigma_thresh * sigma_old)))] = 1
    values = values[np.where(check < 1)]

    # Return results
    return sigma_new, average


if __name__ == "__main__":
    wavs=[500,900,1100,1600]
    hour_bins=[0,10,12,14,16,24]
    vzas=[0,5,10,20,30,40,50,60]
    vaas=[83,98,113,263,278,293]
    for site in ["GHNA","BASP","WWUK","PEAN","DEGE","ATGE","IFAR"]:
        for vza in vzas:
            for vaa in vaas:
                times,refl,mask=extract_reflectances(site,wavs,vza,vaa)
                if len(times)>0:
                    make_time_series_plot(wavs,times,refl,mask,hour_bins,"%s_%s_%s"%(site,vza,vaa))
