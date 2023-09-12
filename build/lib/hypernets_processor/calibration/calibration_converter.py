from hypernets_processor.version import __version__
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.test.test_functions import (
    setup_test_context,
    teardown_test_context,
)
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.utils.paths import parse_sequence_path

import numpy as np
import os.path
import glob
import comet_maths as cm
import xarray
from configparser import ConfigParser
from datetime import datetime

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "27/11/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "Pieter.De.Vis@npl.co.uk"
__status__ = "Development"


class CalibrationConverter:
    def __init__(self, context):
        dir_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        )
        self.path_ascii = os.path.join(
            dir_path, "data", "calibration_files_ascii", "HYPSTAR_cal"
        )
        self.path_netcdf = os.path.join(
            dir_path, "hypernets_processor/calibration/calibration_files", "HYPSTAR_cal"
        )
        context.set_config_value("product_format", "netcdf")
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context)
        self.context = context
        self.version = self.context.get_config_value("version")
        if self.version == 0.0:
            self.version = input(
                "Enter hypernets_processor version for which you are generating calib files:"
            )

    def read_calib_files(self, sequence_path):

        metadata = ConfigParser()
        if os.path.exists(os.path.join(sequence_path, "metadata.txt")):
            metadata.read(os.path.join(sequence_path, "metadata.txt"))
            # ------------------------------
            # global attributes + wavelengths -> need to check for swir
            # ----------------------------------
            globalattr = dict(metadata["Metadata"])
            if "hypstar_sn" in (globalattr.keys()):
                instrument_id = int(globalattr["hypstar_sn"])
            elif "sn_hypstar" in (globalattr.keys()):
                instrument_id = int(globalattr["sn_hypstar"])
            else:
                instrument_id = self.context.get_config_value("hypstar_cal_number")
                self.context.logger.error(
                    "No SN set for hypstar instrument! using hypstar_cal_number from config file instead."
                )
        else:
            self.context.logger.error("Metadata missing")
            self.context.anomaly_handler.add_anomaly("m")

        hypstar = "hypstar_" + str(
            instrument_id
        )  # self.context.get_config_value("hypstar_cal_number"))
        hypstar_path = os.path.join(self.path_netcdf, hypstar)
        name = "HYPERNETS_CAL_" + hypstar.upper() + "_RAD_v" + str(self.version) + ".nc"

        # print("using calibration file:", name)

        if os.path.exists(os.path.join(hypstar_path, name)):
            calibration_data_rad = xarray.open_dataset(os.path.join(hypstar_path, name))
        else:
            raise IOError(
                os.path.join(hypstar_path, name) + " calibration file does not exist"
            )

        name = "HYPERNETS_CAL_" + hypstar.upper() + "_IRR_v" + str(self.version) + ".nc"

        if os.path.exists(os.path.join(hypstar_path, name)):
            calibration_data_irr = xarray.open_dataset(os.path.join(hypstar_path, name))
        else:
            raise IOError(
                os.path.join(hypstar_path, name) + " calibration file does not exist"
            )

        sequence_datetime=parse_sequence_path(sequence_path)["datetime"]

        calibration_data_times = calibration_data_rad["calibrationdates"].values
        nonlin_times = calibration_data_rad["nonlineardates"].values
        wav_times = calibration_data_rad["wavdates"].values

        # print(nonlin_times)
        #
        #
        # calib_i=[x for x, date in enumerate(calibration_data_times)
        #            if datetime.strptime(date,"%y%m%dT%H%M%S") < sequence_datetime][-1]
        #
        # if len(nonlin_times)==1:
        #     nlin_i=0
        # else:
        #     nlin_i=[x for x, date in enumerate(nonlin_times) if datetime.strptime(date,"%y%m%dT%H%M%S") < sequence_datetime][-1]

        print(enumerate(nonlin_times))

        calib_i=[x for x, date in enumerate(calibration_data_times)
                   if datetime.strptime(date,"%y%m%dT%H%M%S") < sequence_datetime][-1]
        if len(nonlin_times) == 1:
            nlin_i = 0
        else:
            nlin_i=[x for x, date in enumerate(nonlin_times)
                   if datetime.strptime(date,"%y%m%dT%H%M%S") < sequence_datetime][-1]

        wav_i=[x for x, date in enumerate(wav_times)
                   if datetime.strptime(date,"%y%m%dT%H%M%S") < sequence_datetime][-1]

        calibration_data_rad = calibration_data_rad.sel(
            calibrationdates=calibration_data_times[calib_i]
        )
        calibration_data_rad = calibration_data_rad.sel(nonlineardates=nonlin_times[nlin_i])
        calibration_data_rad = calibration_data_rad.sel(wavdates=wav_times[wav_i])

        calibration_data_times_irr = calibration_data_irr["calibrationdates"].values
        nonlin_times_irr = calibration_data_irr["nonlineardates"].values
        wav_times_irr = calibration_data_irr["wavdates"].values

        calib_i_irr = [x for x, date in enumerate(calibration_data_times_irr)
                   if datetime.strptime(date, "%y%m%dT%H%M%S") < sequence_datetime][-1]

        # if len(nonlin_times)==1:
        #     nlin_i_irr=0
        # else:
        #     nlin_i_irr=[x for x, date in enumerate(nonlin_times) if datetime.strptime(date,"%y%m%dT%H%M%S") < sequence_datetime][-1]
        #
        if len(nonlin_times) == 1:
            nlin_i_irr = 0
        else:
            nlin_i_irr = [x for x, date in enumerate(nonlin_times_irr)
                  if datetime.strptime(date, "%y%m%dT%H%M%S") < sequence_datetime][-1]

        wav_i_irr = [x for x, date in enumerate(wav_times_irr)
                 if datetime.strptime(date, "%y%m%dT%H%M%S") < sequence_datetime][-1]


        calibration_data_irr = calibration_data_irr.sel(
            calibrationdates=calibration_data_times_irr[calib_i_irr]
        )
        calibration_data_irr = calibration_data_irr.sel(nonlineardates=nonlin_times_irr[nlin_i_irr])
        calibration_data_irr = calibration_data_irr.sel(wavdates=wav_times_irr[wav_i_irr])

        if self.context.get_config_value("network") == "l":
            name = (
                "HYPERNETS_CAL_"
                + hypstar.upper()
                + "_RAD_SWIR_v"
                + str(self.version)
                + ".nc"
            )
            if os.path.exists(os.path.join(hypstar_path, name)):
                calibration_data_rad_swir = xarray.open_dataset(
                    os.path.join(hypstar_path, name)
                )
            else:
                raise IOError(
                    os.path.join(hypstar_path, name)
                    + " calibration file does not exist"
                )

            name = (
                "HYPERNETS_CAL_"
                + hypstar.upper()
                + "_IRR_SWIR_v"
                + str(self.version)
                + ".nc"
            )
            if os.path.exists(os.path.join(hypstar_path, name)):
                calibration_data_irr_swir = xarray.open_dataset(
                    os.path.join(hypstar_path, name)
                )
            else:
                raise IOError(
                    os.path.join(hypstar_path, name)
                    + " calibration file does not exist"
                )

            calibration_data_times = calibration_data_rad_swir[
                "calibrationdates"
            ].values
            nonlin_times = calibration_data_rad_swir["nonlineardates"].values
            calibration_data_rad_swir = calibration_data_rad_swir.sel(
                calibrationdates=calibration_data_times[calib_i]
            )
            calibration_data_rad_swir = calibration_data_rad_swir.sel(
                nonlineardates=nonlin_times[nlin_i]
            )
            calibration_data_rad_swir = calibration_data_rad_swir.sel(
                wavdates=wav_times[wav_i]
            )
            calibration_data_irr_swir = calibration_data_irr_swir.sel(
                calibrationdates=calibration_data_times_irr[calib_i_irr]
            )
            calibration_data_irr_swir = calibration_data_irr_swir.sel(
                nonlineardates=nonlin_times_irr[nlin_i_irr]
            )
            calibration_data_irr_swir = calibration_data_irr_swir.sel(
                wavdates=wav_times_irr[wav_i_irr]
            )

            return (
                calibration_data_rad,
                calibration_data_irr,
                calibration_data_rad_swir,
                calibration_data_irr_swir,
            )

        else:
            return calibration_data_rad, calibration_data_irr

    def convert_all_calibration_data(self):
        measurandstrings = ["radiance", "irradiance"]
        hypstars = [
            os.path.basename(path)
            for path in glob.glob(os.path.join(self.path_ascii, "hypstar_*"))
        ]
        for hypstar in hypstars:
            print("processing " + hypstar)
            hypstar_path = os.path.join(self.path_netcdf, hypstar)
            if not os.path.exists(hypstar_path):
                os.makedirs(hypstar_path)

            for measurandstring in measurandstrings:
                if measurandstring == "radiance":
                    tag = "_RAD_"
                else:
                    tag = "_IRR_"

                calib_data = self.prepare_calibration_data(
                    measurandstring, hypstar=hypstar[8::]
                )
                calib_data.attrs["product_name"] = (
                    "HYPERNETS_CAL_" + hypstar.upper() + tag + "v" + str(self.version)
                )
                self.writer.write(
                    calib_data,
                    directory=hypstar_path,
                    overwrite=True,
                    encodefloat32=False,
                )
                if hypstar[8] == "2":
                    tag = tag + "SWIR_"
                    calib_data = self.prepare_calibration_data(
                        measurandstring, hypstar=hypstar[8::], swir=True
                    )
                    calib_data.attrs["product_name"] = (
                        "HYPERNETS_CAL_"
                        + hypstar.upper()
                        + tag
                        + "v"
                        + str(self.version)
                    )
                    self.writer.write(
                        calib_data,
                        directory=hypstar_path,
                        overwrite=True,
                        encodefloat32=False,
                    )

    def prepare_calibration_data(self, measurandstring, hypstar, swir=False):
        if swir:
            sensortag = "swir"
        else:
            sensortag = "vnir"

        directory = self.path_ascii
        caldatepaths = [
            path
            for path in glob.glob(
                os.path.join(directory, "hypstar_" + str(hypstar), "radiometric", "*")
            )
            if ".pdf" not in path
        ]
        caldates = []
        gains=np.zeros(9999)
        minwav=350
        for caldatepath in caldatepaths:
            if measurandstring == "radiance":
                calpath = glob.glob(
                    os.path.join(
                        caldatepath,
                        "hypstar_"
                        + str(hypstar) +
                        "_radcal_L_*_%s.dat" % (sensortag),
                    )
                )[0]
                caldate = calpath[-15:-9]
                print(os.path.basename(caldatepath))
                if ("b" in os.path.basename(caldatepath)) or ("10C" in os.path.basename(caldatepath)):
                    caldate += "T235959"
                elif "a" in os.path.basename(caldatepath):
                    caldate += "T000000"
                else:
                    caldate += "T120000"
                print(caldate)
            else:
                calpath = glob.glob(
                    os.path.join(
                        caldatepath,
                        "hypstar_"
                        + str(hypstar) +
                        "_radcal_E_*_%s.dat" % (sensortag)
                    )
                )[0]
                caldate = calpath[-15:-9]
                if ("b" in os.path.basename(caldatepath)) or ("10C" in os.path.basename(caldatepath)):
                    caldate += "T235959"
                elif "a" in os.path.basename(caldatepath):
                    caldate += "T000000"
                else:
                    caldate += "T120000"

            if os.path.exists(calpath):
                caldates = np.append(caldates, caldate)
                gains_temp = np.genfromtxt(calpath)
                wavs_temp = gains_temp[:, 1]
                gains_temp = gains_temp[np.where(wavs_temp > minwav)[0]]
                if len(gains_temp)<len(gains):
                    gains=gains_temp
                    wavs = gains[:, 1]

        lincaldatepaths = [
            path
            for path in glob.glob(
                os.path.join(directory, "hypstar_" + str(hypstar),"linearity","*")
            )
        ]

        if len(lincaldatepaths)==0:
            lincaldatepaths = [
                path
                for path in glob.glob(
                    os.path.join(directory, "hypstar_" + str(hypstar), "radiometric", "*")
                ) if len(glob.glob(
                    os.path.join(
                        path,
                        "hypstar_"
                        + str(hypstar)
                        + "_nonlin_corr_coefs_*.dat",
                    )
                ))>0
            ]

        nonlindates = []
        for lincaldatepath in lincaldatepaths:
            nonlinpath = glob.glob(
                    os.path.join(
                        lincaldatepath,
                        "hypstar_"
                        + str(hypstar)
                        + "_nonlin_corr_coefs_*.dat",
                    )
                )[0]
            lincaldate=nonlinpath[-10:-4]
            if ("b" in os.path.basename(lincaldatepath)) or ("10C" in os.path.basename(lincaldatepath)):
                lincaldate += "T235959"
            elif "a" in os.path.basename(lincaldatepath):
                lincaldate += "T000000"
            else:
                lincaldate += "T120000"

            if os.path.exists(nonlinpath):
                nonlindates = np.append(nonlindates, lincaldate)
                if swir:
                    non_linear_cals = np.genfromtxt(nonlinpath)[:, 1]
                else:
                    non_linear_cals = np.genfromtxt(nonlinpath)[:, 0]

        wavcaldatepaths = [
            path
            for path in glob.glob(
                os.path.join(directory, "hypstar_" + str(hypstar), "wavelength", "*")
            )
            if ".pdf" not in path
        ]
        wavcaldates = []

        for wavcaldatepath in wavcaldatepaths:
            wavcalpath = glob.glob(
                os.path.join(
                    wavcaldatepath,
                    "hypstar_"+ str(hypstar)
                    + "_wl_coefs_*.dat",
                )
            )[0]
            wavcaldate = wavcalpath[-10:-4]
            if ("b" in os.path.basename(wavcaldatepath)) or ("10C" in os.path.basename(wavcaldatepath)):
                wavcaldate += "T235959"
            elif "a" in os.path.basename(wavcaldatepath):
                wavcaldate += "T000000"
            else:
                wavcaldate += "T120000"

            if os.path.exists(wavcalpath):
                wavcaldates = np.append(wavcaldates, wavcaldate)
                wav_cals = np.genfromtxt(wavcalpath)[:, 0]

        calibration_data = self.templ.calibration_dataset(
            wavs, non_linear_cals, wav_cals, caldates, nonlindates, wavcaldates
        )
        i_nonlin = 0
        # todo remove [-1] and use all calibrations and interpolate?
        for lincaldatepath in lincaldatepaths:
            nonlinpath = glob.glob(
                os.path.join(
                    lincaldatepath,
                    "hypstar_"
                    + str(hypstar)
                    + "_nonlin_corr_coefs_*.dat",
                )
            )[0]
            if os.path.exists(nonlinpath):
                if swir:
                    non_linear_cals = np.genfromtxt(nonlinpath)[:, 1]
                    with open(nonlinpath, "r") as fp:
                        for i, line in enumerate(fp):
                            if i == 5:
                                nonlin_unc = (
                                    float(line.strip()[8::]) / 2
                                )  # reading in from comments in non_lin files, and convert to k=1
                else:
                    non_linear_cals = np.genfromtxt(nonlinpath)[:, 0]
                    with open(nonlinpath, "r") as fp:
                        for i, line in enumerate(fp):
                            if i == 4:
                                nonlin_unc = (
                                    float(line.strip()[8::]) / 2
                                )  # reading in from comments in non_lin files, and convert to k=1


                calibration_data["non_linearity_coefficients"].values[
                    i_nonlin
                ] = np.pad(non_linear_cals,(0,13-len(non_linear_cals)),'constant', constant_values=(0,0))
                i_nonlin += 1

        i_wavcoef = 0
        for wavcaldatepath in wavcaldatepaths:
            wavcaldate = wavcaldatepath
            wavcalpath = glob.glob(
                os.path.join(
                    wavcaldatepath,
                    "hypstar_"
                    + str(hypstar)
                    + "_wl_coefs_*.dat",
                )
            )[0]
            if os.path.exists(wavcalpath):
                wav_cals = np.genfromtxt(wavcalpath)
                if measurandstring == "radiance" and not swir:
                    wav_cals = wav_cals[:, 0]
                if measurandstring == "irradiance" and not swir:
                    wav_cals = wav_cals[:, 1]
                if measurandstring == "radiance" and swir:
                    wav_cals = wav_cals[:, 2]
                if measurandstring == "irradiance" and swir:
                    wav_cals = wav_cals[:, 3]
                calibration_data["wavelength_coefficients"].values[i_wavcoef] = wav_cals
                i_wavcoef += 1

        i_cal = 0
        for caldatepath in caldatepaths:
            # print(caldatepath,)
            if measurandstring == "radiance":
                calpath = glob.glob(
                    os.path.join(
                        caldatepath,
                        "hypstar_"
                        + str(hypstar)
                        + "_radcal_L_*_%s.dat" % (sensortag),
                    )
                )[0]
            else:
                calpath = glob.glob(
                    os.path.join(
                        caldatepath,
                        "hypstar_"
                        + str(hypstar)
                        + "_radcal_E_*_%s.dat" % (sensortag),
                    )
                )[0]

            if os.path.exists(calpath):
                caldates = np.append(caldates, caldate)
                gains = np.genfromtxt(calpath)
                wavs = gains[:, 1]
                gains = gains[np.where(wavs > 350)[0]]
                wavs = wavs[np.where(wavs > 350)[0]]
                placeholder_unc = 2
                gainlen=len(calibration_data["wavpix"].values[i_cal,:])
                if True:
                    # calibration_data["wavelength"].values = gains[:, 1]
                    calibration_data["wavpix"].values[i_cal,:] = gains[:gainlen, 0]
                    calibration_data["gains"].values[i_cal,:] = gains[:gainlen, 2]
                    # calibration_data["u_rel_random_gains"].values = None

                    calibration_data["u_rel_systematic_indep_gains"].values[i_cal,:] = ((
                        gains[:, 6] ** 2
                        + gains[:, 7] ** 2
                        + gains[:, 8] ** 2
                        + gains[:, 9] ** 2
                        + gains[:, 10] ** 2
                        + gains[:, 11] ** 2
                        + gains[:, 12] ** 2
                        + gains[:, 13] ** 2
                        + gains[:, 14] ** 2
                        + gains[:, 15] ** 2
                        + gains[:, 16] ** 2
                        + gains[:, 17] ** 2
                        + gains[:, 19] ** 2
                        + nonlin_unc**2
                        + placeholder_unc**2
                    ) ** 0.5)[:gainlen]

                    cov_diag = cm.convert_corr_to_cov(
                        np.eye(len(gains[:, 2])), gains[:, 2] * (gains[:, 19])
                    )

                    cov_other = cm.convert_corr_to_cov(
                        np.eye(len(gains[:, 2])),
                        gains[:, 2]
                        * (
                            gains[:, 8] ** 2
                            + gains[:, 10] ** 2
                            + gains[:, 11] ** 2
                            + gains[:, 16] ** 2
                            + gains[:, 17] ** 2
                            + nonlin_unc**2
                        )
                        ** 0.5,
                    )

                    cov_full = cm.convert_corr_to_cov(
                        np.ones((len(gains[:, 2]), len(gains[:, 2]))),
                        gains[:, 2]
                        * (
                            gains[:, 7] ** 2
                            + gains[:, 9] ** 2
                            + gains[:, 12] ** 2
                            + gains[:, 13] ** 2
                            + gains[:, 14] ** 2
                            + gains[:, 15] ** 2
                            + placeholder_unc**2
                        )
                        ** 0.5,
                    )

                    cov_filament = cm.convert_corr_to_cov(
                        np.ones((len(gains[:, 2]), len(gains[:, 2]))),
                        gains[:, 2] * (gains[:, 6] ** 2) ** 0.5,
                    )

                    calibration_data["err_corr_systematic_indep_gains"].values[
                        i_cal,:,:
                    ] = cm.correlation_from_covariance(
                        cov_diag + cov_other + cov_full + cov_filament
                    )[:gainlen,:gainlen]

                    calibration_data["u_rel_systematic_corr_rad_irr_gains"].values[
                        i_cal,:
                    ] = ((gains[:, 4] ** 2 + gains[:, 5] ** 2 + gains[:, 18] ** 2) ** 0.5)[:gainlen]

                    cov_other = cm.convert_corr_to_cov(
                        np.eye(len(gains[:, 2])),
                        gains[:, 2] * (gains[:, 4] ** 2 + gains[:, 18] ** 2) ** 0.5,
                    )

                    cov_filament = cm.convert_corr_to_cov(
                        np.ones((len(gains[:, 2]), len(gains[:, 2]))),
                        gains[:, 2] * (gains[:, 5] ** 2) ** 0.5,
                    )

                    calibration_data["err_corr_systematic_corr_rad_irr_gains"].values[
                        i_cal,:,:
                    ] = cm.correlation_from_covariance(cov_other + cov_filament)[:gainlen,:gainlen]
                # except:
                #     print(caldatepath, " failed")
            i_cal += 1

        return calibration_data


if __name__ == "__main__":
    context = setup_test_context()
    calcov = CalibrationConverter(context)
    calcov.convert_all_calibration_data()
    teardown_test_context(context)