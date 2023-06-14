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
from obsarray.templater.dataset_util import DatasetUtil

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
out_path = r"/home/data/insitu/hypernets/archive_qc/best_files"


def make_time_series_plot(wavs,times, measurands, mask, hour_bins, tag, sigma_thresh=3.0, fit_poly_n=0, n_max_points=0):
    # get a datetime that is equal to epoch
    epoch = datetime.datetime(1970, 1, 1)
    times_sec=np.array([(d - epoch).total_seconds() for d in times])
    for i in range(len(wavs)):
        measurand_wav=measurands[:,i]
        for ii in range(len(hour_bins)-1):
            hour_ids=np.where((mask==0) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
            if len(hour_ids)>0:
                std, mean, mask_clip = sigma_clip(times_sec[hour_ids], measurand_wav[hour_ids], tolerance=0.05, median=True, sigma_thresh=sigma_thresh,fit_poly_n=fit_poly_n, n_max_points=n_max_points)
                mask[hour_ids]=mask_clip

    print(tag,len(times),len(times[np.where(mask==0)[0]]),len(times[np.where(mask==1)[0]]),len(times[np.where(mask==2)[0]]))
    for i in range(len(wavs)):
        measurand_wav=measurands[:,i]
        ax = plt.gca()
        for ii in range(len(hour_bins)-1):
            hour_ids=np.where(((mask==0) | (mask==2)) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
            if len(hour_ids)>0:
                color = next(ax._get_lines.prop_cycler)['color']
                std, mean, mask_clip = sigma_clip(times_sec[hour_ids], measurand_wav[hour_ids], tolerance=0.01, median=True, sigma_thresh=sigma_thresh,fit_poly_n=fit_poly_n,n_max_points=n_max_points)
                # print(wavs[i],"%s:00-%s:00" % (hour_bins[ii], hour_bins[ii + 1]),mean,std)
                plt.plot(times[hour_ids], mean, color=color, linestyle='-')
                plt.plot(times[hour_ids], mean-sigma_thresh*std, color=color, linestyle=':')
                plt.plot(times[hour_ids], mean+sigma_thresh*std, color=color, linestyle=':')
                outlier_ids=np.where((mask==2) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
                bestdata_ids=np.where((mask==0) & ([time_between(dt.time(),hour_bins[ii],hour_bins[ii+1]) for dt in times]))[0]
                plt.plot(times[outlier_ids], measurand_wav[outlier_ids], "o", color=color,
                         alpha=0.3)
                plt.plot(times[bestdata_ids], measurand_wav[bestdata_ids], "o", color=color,
                         label="%s:00-%s:00" % (hour_bins[ii], hour_bins[ii + 1]))

        plt.plot(times[np.where(mask==1)[0]],measurands[np.where(mask==1)[0],i],"ko",alpha=0.1,label="masked by processor")
        if len(np.where(mask==3)[0])>0:
            plt.plot(times[np.where(mask==3)[0]],measurands[np.where(mask==3)[0],i],"mo",alpha=0.1,label="masked by vegetation checks")
        valids=measurand_wav[np.where(mask==0)[0]]
        plt.ylim([min(valids)-0.3*(max(valids)-min(valids)),max(valids)+0.3*(max(valids)-min(valids))])
        plt.legend()
        plt.ylabel("reflectance")
        plt.xlabel("datetime")
        plt.savefig(os.path.join(archive_path,"qc_plots","qc_%s_%s.png"%(tag,wavs[i])), dpi=300)
        plt.clf()
        print("plot done ", os.path.join(archive_path,"qc_plots","qc_%s_%s.png"%(tag,wavs[i])))
    return mask

def time_between(time,start_hour,end_hour):
    if time<datetime.time(start_hour,0,0):
        return False
    elif time>datetime.time(end_hour-1,59,59):
        return False
    else:
        return True


def find_files(site):
    # files=glob.glob(archive_path+r"\%s\*\*\*\*\*L2A*"%site)
    files=glob.glob(archive_path+r"/%s/*/*/*/*/*L2A*"%site)
    files=np.sort(files)
    list_ds=np.empty(len(files),dtype=object)
    for ifile,file in enumerate(files):
        list_ds[ifile]=xr.open_dataset(file)
    return files,list_ds

def extract_reflectances(files, wavs, vza, vaa):
    refl=np.zeros((len(files),len(wavs)))
    mask=np.ones(len(files))
    times=np.empty(len(files),dtype=datetime.datetime)
    valid=np.ones(len(files),dtype=int)
    all_ds=np.empty(len(files),dtype=object)
    for i in range(len(files)):
        ds=read_hypernets_file(files[i],vza=vza, vaa=vaa, filter_flags=False,max_angle_tolerance=2)
        if ds is None:
            mask[i]=1
            print("bad angle for file:", vza, vaa, files[i])
            continue

        if len(ds.quality_flag.values)==1:
            if ds.quality_flag.values == 0:
                mask[i]=0
            else:
                print([DatasetUtil.get_set_flags(flag) for flag in ds["quality_flag"]])

            ids=[np.argmin(np.abs(ds.wavelength.values-wav)) for wav in wavs]
            refl[i]=ds.reflectance.values[ids,0]
            times[i]=datetime.datetime.fromtimestamp(ds.acquisition_time.values[0])
        else:
            if np.mean(ds.quality_flag.values) == 0:
                mask[i]=0
            ids=[np.argmin(np.abs(ds.wavelength.values-wav)) for wav in wavs]
            refl[i]=np.mean(ds.reflectance.values[ids,:])
            times[i]=datetime.datetime.fromtimestamp(np.mean(ds.acquisition_time.values[:]))
    return times, refl, mask

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
        return ds

    ds = ds.isel(series=id_series)
    #print(len(id_series), " series selected on angle (vza=%s, vaa=%s requested, vza=%s, vaa=%s found)"%(vza,vaa,ds["viewing_zenith_angle"].values,ds["viewing_azimuth_angle"].values))
    return ds

def sigma_clip(xvals, values, tolerance=0.01, median=True, sigma_thresh=3.0, fit_poly_n=0,n_max_points=0):
    # Remove NaNs from input values
    values = np.array(values)
    values = values[np.where(np.isnan(values) == False)]
    values_original = np.copy(values)

    mask = np.zeros([len(values)])

    # Continue loop until result converges
    diff = 10e10
    while diff > tolerance:
        # Assess current input iteration
        # if fit_poly_n > 0:
        #     poly_coeff = np.polyfit(xvals[np.where(mask < 1)], values[np.where(mask < 1)], fit_poly_n)
        #     poly_func = np.poly1d(poly_coeff)
        #     average = poly_func(xvals)
        #     sigma_old = np.std(values[np.where(mask < 1)] - average[np.where(mask < 1)])

        if n_max_points>0:
            average = fit_binfunc(xvals,values,n_max_points)
            sigma_old = np.std(values[np.where(mask < 1)] - average[np.where(mask < 1)])

        elif median == False:
            average = np.mean(values[np.where(mask < 1)])
            sigma_old = np.std(values[np.where(mask < 1)])

        elif median == True:
            average = np.median(values[np.where(mask < 1)])
            sigma_old = np.std(values[np.where(mask < 1)])

        # Mask those pixels that lie more than 3 stdev away from mean
        mask[np.where(values > (average + (sigma_thresh * sigma_old)))] = 2
        mask[np.where(values < (average - (sigma_thresh * sigma_old)))] = 2

        # Re-measure sigma and test for convergence
        sigma_new = np.std(values[np.where(mask < 1)]-average[np.where(mask < 1)])
        # print(sigma_old,sigma_new)
        diff = abs(sigma_old - sigma_new) / sigma_old

    return sigma_new, average, mask

def fit_binfunc(xvals,yvals,maxpoints):
    nbins=int(np.ceil(len(xvals)/maxpoints))
    if nbins==1:
        return np.mean(yvals)*np.ones_like(xvals)
    else:
        x_bin=np.zeros(nbins)
        y_bin=np.zeros(nbins)
        binpoints=int(np.ceil(len(xvals)/nbins))
        for i in range(nbins):
            x_bin[i]=np.mean(xvals[i*binpoints:min((i+1)*binpoints,len(xvals))])
            y_bin[i]=np.mean(yvals[i*binpoints:min((i+1)*binpoints,len(xvals))])
        return np.interp(xvals,x_bin,y_bin)

def vegetation_checks(ds,iseries):
    b2 = ds["reflectance"].values[np.argmin(np.abs(ds.wavelength.values-490)), iseries]  # 490 nm
    b3 = ds["reflectance"].values[np.argmin(np.abs(ds.wavelength.values-560)), iseries]  # 560 nm
    b4 = ds["reflectance"].values[np.argmin(np.abs(ds.wavelength.values-665)), iseries]  # 665 nm
    b5 = ds["reflectance"].values[np.argmin(np.abs(ds.wavelength.values-705)), iseries]  # 705 nm
    b7 = ds["reflectance"].values[np.argmin(np.abs(ds.wavelength.values-783)), iseries]  # 783 nm
    b8 = ds["reflectance"].values[np.argmin(np.abs(ds.wavelength.values-865)), iseries]  # equivalent of 8a # 865 nm

    vis_test = (b2 < b3) & (b3 > b4)  # Spot the peak in the green region of the visible
    ir_test = b7 > b5 * 2  # reflectance in b7 must be double that of b5 ... in effect detecting the red edge?
    ndvi = (b8 - b4) / (b8 + b4)  # Calculate NDVI
    ndvi_threshold = ndvi > 0.42
    refl_threshold = b7<0.65 and b7>0.15

    #flags_combined = np.logical_and(vis_test, ir_test, ndvi_threshold)  # combine the three flags

    return vis_test and ir_test and ndvi_threshold and refl_threshold

if __name__ == "__main__":

    wavs=[500,900,1100,1600]
    hour_bins=[0,6,8,10,12,14,16,18,24]

    sites=["WWUK", "PEAN1A", "PEAN1B", "PEAN2", "DEGE", "ATGE", "GHNA", "BASP", "IFAR"]
    sites_polyn=[4,2,0,4,0,0,0,0]
    sites_thresh=[2,2,2,2,2,2,2,3]
    for isite,site in enumerate(sites):
        files,site_ds=find_files(site)
        files_nmaskedseries=np.zeros(len(files))
        for ifile in range(len(site_ds)):
            ids_wav=np.where((site_ds[ifile].wavelength>380) & (site_ds[ifile].wavelength<1700))[0]
            site_ds[ifile] = site_ds[ifile].isel(wavelength=ids_wav)

        for iseries in range(len(site_ds[0].viewing_zenith_angle.values)):
            vza= round(site_ds[0].viewing_zenith_angle.values[iseries])
            vaa = round(site_ds[0].viewing_azimuth_angle.values[iseries])
            times,refl,mask=extract_reflectances(files,wavs,vza,vaa)

            if site == "WWUK":
                for ifile in range(len(site_ds)):
                    if not vegetation_checks(site_ds[ifile],iseries):
                        mask[ifile]=3
            if True:
                mask2 = make_time_series_plot(wavs,times,refl,mask,hour_bins,"%s_%s_%s"%(site,vza,vaa),fit_poly_n=sites_polyn[isite],n_max_points=30,sigma_thresh=sites_thresh[isite])
                for ifile in range(len(site_ds)):
                    ds_curr = site_ds[ifile]
                    ds_curr.quality_flag.attrs["flag_meanings"] = ds_curr.quality_flag.attrs["flag_meanings"].replace(
                        "placeholder1", "postprocessing_outliers")
                    if site == "WWUK":
                        ds_curr.quality_flag.attrs["flag_meanings"] = ds_curr.quality_flag.attrs["flag_meanings"].replace(
                        "placeholder1", "postprocessing_outliers")

                    if mask2[ifile]>0:
                        ds_curr.reflectance[:,iseries]*=np.nan
                        ds_curr.u_rel_random_reflectance[:,iseries]*=np.nan
                        ds_curr.u_rel_systematic_reflectance[:,iseries]*=np.nan
                        ds_curr.std_reflectance[:,iseries]*=np.nan
                        if mask2[ifile]==2:
                            ds_curr.quality_flag[iseries]=16
                        files_nmaskedseries[ifile]+=1
                    site_ds[ifile] = ds_curr

            # except:
            #     print("%s_%s_%s"%(site,vza,vaa), " failed")
        for ifile in range(len(site_ds)):
            if files_nmaskedseries[ifile]<len(site_ds[ifile].series)/2:
                print(files_nmaskedseries[ifile],os.path.basename(files[ifile]))
                site_ds[ifile].to_netcdf(os.path.join(out_path,site,os.path.basename(files[ifile])))
