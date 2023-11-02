from punpy import MeasurementFunction

import scipy.interpolate
import numpy as np
import os.path
import comet_maths as cm
import matheo.band_integration as bi
import xarray as xr
import matplotlib.pyplot as plt

dir_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
)
refdat_path = os.path.join(dir_path, "data", "quality_comparison_data")


class InterpolationWavClearSky(MeasurementFunction):
    def setup(self, szas, network, irr_wavs):
        ref_szas = np.array([0, 10, 20, 40, 60, 70, 80])
        ref_sza = ref_szas[np.argmin(np.abs(ref_szas - np.mean(szas)))]
        self.clear_sky = xr.open_dataset(
            os.path.join(
                refdat_path,
                "solar_irradiance_hypernets_sza%s_highres_%s.nc"
                % (int(ref_sza), network),
            )
        )
        self.bandwidth = np.append(
            3.0 * np.ones_like(irr_wavs[irr_wavs < 1000]),
            10.0 * np.ones_like(irr_wavs[irr_wavs > 1000]),
        )

        self.r_pixel_irrs = bi.return_r_pixel(
            irr_wavs,
            self.bandwidth,
            self.clear_sky["wavelength"].values,
            bi.f_gaussian,
        )

        self.corr_irrs = bi.band_int(
            d=self.clear_sky["solar_irradiance_BOA"].values,
            x=self.clear_sky["wavelength"].values,
            r=self.r_pixel_irrs,
            x_r=self.clear_sky["wavelength"].values,
        ) - cm.interpolate_1d(
            self.clear_sky["wavelength"].values,
            self.clear_sky["solar_irradiance_BOA"].values,
            irr_wavs,
        )

    def meas_function(self, rad_wavs, irr_wavs, irr):
        """
        This function implements the measurement function.
        Each of the arguments can be either a scalar or a vector (1D-array).
        """
        if len(irr.shape) > 1:
            intp_highres = np.empty(
                (len(self.clear_sky["wavelength"].values), len(irr[0]))
            )
            for i in range(len(irr[0])):
                intp_highres[:, i] = cm.interpolate_1d_along_example(
                    irr_wavs,
                    irr[:, i] - self.corr_irrs,
                    self.clear_sky["wavelength"].values,
                    self.clear_sky["solar_irradiance_BOA"].values,
                    self.clear_sky["wavelength"].values,
                    relative=False,
                )
        else:
            intp_highres = cm.interpolate_1d_along_example(
                irr_wavs,
                irr - self.corr_irrs,
                self.clear_sky["wavelength"].values,
                self.clear_sky["solar_irradiance_BOA"].values,
                self.clear_sky["wavelength"].values,
                relative=False,
            )

        intp_irr = bi.band_int(
            d=intp_highres,
            x=self.clear_sky["wavelength"].values,
            r=self.r_pixel_irrs,
            x_r=self.clear_sky["wavelength"].values,
        )

        return intp_irr

    @staticmethod
    def get_name():
        return "InterpolationWavClearSky"

    def get_argument_names(self):
        return ["radiance_wavelength", "wavelength", "irradiance"]
