"""describe class"""

"""___Built-In Modules___"""
#import here

"""___Third-Party Modules___"""
#import here
import pickle
from dateutil.parser import parse
import datetime
import numpy as np
import xarray as xr
from typing import Optional, Union, List, Any

"""___NPL Modules___"""
#import here
import comet_maths as cm
import matheo.band_integration as bi
from brdf_model import BRDFModelFactory, BRDFParameters


"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "01/02/2021"
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class Convert_RadCalNet:
    def __init__(
        self,
        path,
        brdf_file,
        irr_file,
    ):
        self.path = path
        self.brdf_model_factory = BRDFModelFactory()
        with open(brdf_file, "rb") as f:
            self.brdf_params = pickle.load(f)
        self.irr_all = xr.open_dataset(irr_file)


    def convert(self, refl):
        # do processing
        #save file
        return refl

    def interpolate_direct_diffuse_ratio(self, datetimes, sza=None, wavelength=None):
        ds_irr_temp = self.irr_all.isel(datetime=np.where(self.irr_all["sza"] < 90)[0])
        ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values = ds_irr_temp[
                                                                       "direct_to_diffuse_irradiance_ratio"].values / np.cos(
            ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
        ds_irr_temp = ds_irr_temp.interp(datetime=datetimes, method="linear")
        if sza is not None:
            ds_irr_temp["sza"].values = sza
        ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values = ds_irr_temp[
                                                                       "direct_to_diffuse_irradiance_ratio"].values * np.cos(
            ds_irr_temp["sza"].values / 180 * np.pi)[:, None]
        if wavelength is not None:
            i_wav = np.argmin(np.abs(wavelength - ds_irr_temp.wavelength.values))
            return ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values[:, i_wav]
        else:
            return ds_irr_temp["direct_to_diffuse_irradiance_ratio"].values.T

    import pandas as pd
    from pysolar.solar import get_altitude

    __author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"

    def convert_datetime(self,
            date_time: Union[datetime.datetime, datetime.date, str, float, int, np.ndarray]
    ) -> datetime.datetime:
        """
        Convert input datetimes to a datetime object

        :param date_time: date time to convert to a datetime object
        :return: datetime object corresponding to input date_time
        """
        if isinstance(date_time, np.ndarray):
            return np.array([self.convert_datetime(date_time_i) for date_time_i in date_time])
        elif isinstance(date_time, datetime.datetime):
            return date_time
        elif isinstance(date_time, datetime.date):
            return datetime.datetime.combine(date_time, datetime.time())
        elif isinstance(date_time, np.datetime64):
            unix_epoch = np.datetime64(0, "s")
            one_second = np.timedelta64(1, "s")
            seconds_since_epoch = (date_time - unix_epoch) / one_second
            return datetime.datetime.utcfromtimestamp(seconds_since_epoch)
        elif isinstance(date_time, (float, int, np.uint, np.float32, np.float64, np.int64, np.int32, np.uint64, np.uint32)):
            return datetime.datetime.utcfromtimestamp(date_time)
        else:
            print(type(date_time))
            if date_time[-1] == "Z":
                date_time = date_time[:-1]
            try:
                return parse(date_time, fuzzy=False)
            except ValueError:
                raise ValueError(
                    "Unable to discern datetime requested: '{}'".format(date_time)
                )

    def correct_to_nadir(self, ds_hyp):
        vza = ds_hyp.viewing_zenith_angle.values
        sza = ds_hyp.solar_zenith_angle.values
        vaa = ds_hyp.viewing_azimuth_angle.values
        saa = ds_hyp.solar_azimuth_angle.values
        times = [self.convert_datetime(time) for time in ds_hyp.acquisition_time.values]

        brdf_model = self.brdf_model_factory.get_brdf_model(
            "RPV",
            sza,
            vza,
            saa,
            vaa,
            direct_to_diffuse_irr=self.interpolate_direct_diffuse_ratio(times, sza))

        HCRF_model = brdf_model.return_HCRF_for_angle(sza = sza,vza=vza, vaa=vaa, saa=saa, brdf_params = self.brdf_params.get_values().T)
        HCRF_model_nadir = brdf_model.return_HCRF_for_angle(sza = sza,vza=np.zeros_like(vza), vaa=vaa, saa=saa, brdf_params = self.brdf_params.get_values().T)
        ds_hyp.reflectance.values = ds_hyp.reflectance.values * cm.interpolate_1d(self.irr_all.wavelength.values, (HCRF_model_nadir / HCRF_model), ds_hyp.wavelength.values)
        return ds_hyp

    def spectral_processing(self,radcalnet_wavelength, hypernets_wavelengths,hypernets_reflectance,asd_wavelengths,asd_reflectances):
        # do spectral processing here

        # identify last 10nm of HN data and overlap with ASD by 10nm
        hyp_mean_last10nm=np.mean(hypernets_reflectance[np.where((hypernets_wavelengths>1670) & (hypernets_wavelengths<1680))])
        asd_mean_10nm=np.mean(asd_reflectances[np.where((asd_wavelengths>1670) & (asd_wavelengths<1680))])

        #determine correction factor from diff between the two
        correction_factor=hyp_mean_last10nm/asd_mean_10nm
        print("correction_factor = ", correction_factor)

        # add the asd dataset to the end of the HN dataset, adding correction factor to the asd data so that the join is smooth
        combined_wavelengths=np.append(hypernets_wavelengths[np.where(hypernets_wavelengths<1680)],asd_wavelengths[np.where(asd_wavelengths>1680)])
        combined_reflectances=np.append(hypernets_reflectance[np.where(hypernets_wavelengths<1680)],correction_factor*asd_reflectances[np.where(asd_wavelengths>1680)])

        # band integration using matheo to match RCN 10nm triangular format
        # https://matheo.readthedocs.io/en/latest/content/user_guide.html
        radcalnet_reflectances = bi.pixel_int(
            d=combined_reflectances,
            x=combined_wavelengths,
            x_pixel=radcalnet_wavelength,
            width_pixel=10.0*np.ones(len(radcalnet_wavelength)),
            band_shape="triangle"
        )

        #plots for sanity check
        # plt.plot(hypernets_wavelengths,hypernets_reflectance, label='GHNA Instrument')
        # plt.plot(asd_wavelengths,asd_reflectances, label='ASD')
        # plt.plot(radcalnet_wavelength,radcalnet_reflectances, label='GHNA Interpolated')
        # plt.grid()
        # plt.legend()
        # plt.title('Dataset Comparison', fontsize=20)
        # plt.xlabel('Wavelength (nm)', fontsize=20)
        # plt.ylabel('Reflectance', fontsize=20)
        # plt.savefig('comparison_%s.png'%(rcn_datetime))
        # # plt.show()
        return radcalnet_reflectances

    def time_interpolation(self, hypernets_datetime_pre, rcn_refl_pre, hypernets_datetime_aft, rcn_refl_aft, rcn_datetime):
        time_measured = np.array([hypernets_datetime_pre, hypernets_datetime_aft])
        refl_measured = np.array([rcn_refl_pre, rcn_refl_aft])
        time_target = rcn_datetime
        print(time_measured.shape,refl_measured.shape)
        refl_interpolated = cm.interpolate_1d(time_measured, refl_measured, time_target, u_y_i=None, method="linear",
                                           return_uncertainties=False, return_corr=False,interpolate_axis=0)
        return refl_interpolated