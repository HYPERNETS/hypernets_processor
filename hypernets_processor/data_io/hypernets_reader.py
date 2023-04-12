"""
Module with functions and classes to read Hypernets data
"""
from datetime import datetime, timezone
import os, shutil
import re  # for re.split
from configparser import ConfigParser
from struct import unpack
from sys import version_info  # noqa
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import math
from pysolar.solar import *

from hypernets_processor.data_io.format.header import HEADER_DEF
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.spectrum import Spectrum
from hypernets_processor.data_io.format.flags import FLAG_COMMON

from hypernets_processor.version import __version__
from hypernets_processor.data_io.product_name_util import ProductNameUtil
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

"""___Authorship___"""
__author__ = "ClÃ©mence Goyens"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "ClÃ©mence Goyens"
__status__ = "Development"


class HypernetsReader:
    def __init__(self, context):
        self.context = context
        self.model = self.context.get_config_value("model").split(",")
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context=context)
        self.produt = ProductNameUtil(context=context)
        cckeys = [
            "mapping_vis_a",
            "mapping_vis_b",
            "mapping_vis_c",
            "mapping_vis_d",
            "mapping_vis_e",
            "mapping_vis_f",
        ]
        ccvalues = []
        for i in range(len(cckeys)):
            ccvalues.append(self.context.get_config_value(cckeys[i]))
        self.cc_vis = dict(zip(cckeys, ccvalues))

    # READ METADATA
    # CG - 20200331
    # old functions: gen2dict, extract_metadata, read_metadata, read_metadata 2, read_spectra -> NOT USED TO REMOVE
    # CG - 20200604
    # new functions: read_header, read_data, read_footer, read_seq, read_wavelength

    def plot_spectra(self, spectra, dataSpectra):
        plt.clf()
        plt.title(spectra)
        plt.plot([i for i in range(len(dataSpectra))], dataSpectra)
        plt.show()

    # def save(self, path):
    #     with open(path, 'w') as f:
    #         f.write('Dataset length: {} bytes\n'
    #                 'Timestamp: {} ms\n'
    #                 'CRC32: {} \n'
    #                 'Entrance: {}\n'
    #                 'Radiometer: {}\n'
    #                 'Exposure time: {} ms\n'
    #                 'Sensor temperature: {} \'C\n'
    #                 'Pixel count: {}\n'
    #                 'Tilt:\n'
    #                 '\tx:{}\u00B1{}\n'
    #                 '\t y:{}\u00B1{}\n'
    #                 '\t z:{}\u00B1{}\n'.format(self.header.total_length, self.header.timestamp, hex(self.crc32[0]),
    #                                            self.header.spectrum_type.optics.name,
    #                                            self.header.spectrum_type.radiometer.name,
    #                                            self.header.exposure_time, self.header.temperature,
    #                                            self.header.pixel_count,
    #                                            self.header.accel_stats.mean_x,
    #                                            self.header.accel_stats.std_x,
    #                                            self.header.accel_stats.mean_y,
    #                                            self.header.accel_stats.std_y,
    #                                            self.header.accel_stats.mean_z,
    #                                            self.header.accel_stats.std_z))

    def read_header(self, f, headerDef):
        header = {}
        for headLen, headName, headFormat in headerDef:
            data = f.read(headLen)
            if len(data) != headLen:
                # self.context.logger.error("Spectra length not similar to header length")
                break
                continue
            # if version_info > (3, 0):
            #     print("%02X " * headLen % (tuple([b for b in data])))
            # else:
            #     print("%02X " * headLen % (tuple([ord(b) for b in data])))
            (var,) = unpack(headFormat, data)
            if headName == "Pixel Count":
                pixel_count = var
            if headName == "Spectrum Type Information":
                specInfo = format(ord(data), "#010b")
                specInfo = ["1" == a for a in reversed(specInfo[2:])]

                # bit 7 for VIS radiometer,
                # bit 6 for SWIR,
                # bit 4 for radiance,
                # bit 3 for irradiance,
                # bits 4 and 3 for dark;
                strInfo = ""

                if specInfo[7]:
                    strInfo += "VIS "  # noqa
                if specInfo[6]:
                    strInfo += "SWIR "  # noqa

                if not specInfo[3] and not specInfo[4]:
                    strInfo += "Dark"  # noqa
                if specInfo[3] and not specInfo[4]:
                    strInfo += "Irr"  # noqa
                if specInfo[4] and not specInfo[3]:
                    strInfo += "Rad"  # noqa
                if specInfo[3] and specInfo[4]:
                    strInfo += "Error"  # noqa

                self.context.logger.debug("Spectrum Type Info : %s " % strInfo)

            header[headName] = var
        return header

    def read_data(self, f, data_len):
        prev = 0
        self.context.logger.debug("Reading Data spectra ...")
        dataSpectra = []
        for i in range(int(data_len)):  # Last read data is count
            data = f.read(2)
            if len(data) != 2:
                self.context.logger.error("Warning : impossible to read 2 bytes")
                break
                continue

            # Read data as unsigned short
            (unpackData,) = unpack("<H", data)
            dataSpectra.append(unpackData)
            prev = unpackData
        return dataSpectra

    def read_footer(self, f, datalength):
        # print(f)
        self.context.logger.debug("Reading CRC32 ...")
        data = f.read(datalength)
        (unpackData,) = unpack("<I", data)

    def read_wavelength(self, pixcount, cal_data):

        pix = range(pixcount)
        wav_coef = cal_data["wavelength_coefficients"]
        wav_coef_func = np.poly1d(np.flip(wav_coef))

        wvl = wav_coef_func(pix)
        self.context.logger.debug("Wavelength range: %s -%s" % (min(wvl), max(wvl)))

        return wvl

    def read_series(
        self,
        seq_dir,
        series,
        lat,
        lon,
        metadata,
        flag,
        fileformat,
        cal_data,
        instrument_id,
        site_id,
    ):
        model_name = self.model

        # 1. Read header to create template dataset (including wvl and scan dimensions + end of file!!)
        # ----------------------------------------

        # scan dimension - to have total number of dimensions
        index_scan_total = model_name.index("scan_total")
        # series id
        # ------------------------------------------
        # added to consider concanated files
        scanDim = sum([int(re.split("_|\.", i)[index_scan_total]) for i in series])

        # ------------------------------------------
        # added to consider non concanated files
        # scanDims = [int(re.split('_|\.', i)[index_scan_total]) for i in series]
        # scanDim = sum(scanDims)

        ## rewrite series
        # baseName=["_".join(seriesname.split("_", 7)[:7]) for seriesname in series]
        # print(baseName)
        # newSeries = []
        # for i in series:
        #     # create dictionary from filename
        #     seriesAttr = re.split('_|\.', i)[:-1]  # remove spe extension
        #     model = dict(zip(model_name, seriesAttr))
        #     baseName = '_'.join(seriesAttr)
        #     nbrScans = int(model["scan_total"])
        #     n = 1
        #     while n <= nbrScans:
        #         new_fname = "{}_{}{}".format(baseName, n, '.spe')
        #         newSeries.append(new_fname)
        #         n += 1
        # series = newSeries
        # -----------------------------------------

        # wvl dimensions
        FOLDER_NAME = os.path.join(seq_dir, "RADIOMETER/")
        f = open(FOLDER_NAME + series[1], "rb")

        # Header definition with length, description and decoding format
        header = self.read_header(f, HEADER_DEF)
        self.context.logger.debug(header)
        pixCount = header["Pixel Count"]
        # if bool(header) == False:
        #     print("Data corrupt go to next line")
        #     header = self.read_header(f, HEADER_DEF)

        if pixCount == 2048:
            wvl = self.read_wavelength(pixCount, cal_data)
            # 2. Create template dataset
            # -----------------------------------
            # use template from variables and metadata in format
            ds = self.templ.l0_template_dataset(wvl, scanDim, fileformat)
        else:
            self.context.logger.error(
                "The number of wavelength pixels does not match "
                "the expected values for VNIR."
            )

        # look for the maximum number of lines to read-- maybe not an elegant way to do?
        f.seek(0, 2)  # go to end of file
        eof = f.tell()
        f.close()

        ds.attrs["sequence_id"] = str(os.path.basename(seq_dir))
        ds.attrs["instrument_id"] = str(instrument_id)
        ds.attrs["site_id"] = str(site_id)
        ds.attrs["source_file"] = str(os.path.basename(seq_dir))

        ds["wavelength"] = wvl
        # ds["bandwidth"]=wvl
        # ds["scan"] = np.linspace(0, scanDim, scanDim)

        # add auxiliary data to the L0 data
        temp, RH, pressure, lux = self.read_aux(seq_dir)
        ds.attrs["system_temperature"] = temp
        ds.attrs["system_relative_humidity"] = RH
        ds.attrs["system_pressure"] = pressure
        ds.attrs["illuminance"] = lux

        # Keep track of scan number!
        scan_number = 0

        # read all spectra (== spe files with concanated files) in a series
        for spectra in series:

            model = dict(zip(model_name, spectra.split("_")[:-1]))
            specBlock = (
                model["series_rep"]
                + "_"
                + model["series_id"]
                + "_"
                + model["vaa"]
                + "_"
                + model["azimuth_ref"]
                + "_"
                + model["vza"]
            )
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(
                acquisitionTime + "UTC", "%Y%m%dT%H%M%S%Z"
            )
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)

            # -------------------------------------
            # # account for non concanated files
            # spec = "_".join(spectra.split('_')[:-1]) + ".spe"
            # acquisitionTime = specattr[spec]
            # print(acquisitionTime)
            # acquisitionTime = datetime.datetime.strptime(acquisitionTime + "UTC", '%Y%m%dT%H%M%S%Z')
            #
            # acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            # model = dict(zip(model_name, str.split(spectra, "_")))
            # ________________________________________

            # -----------------------
            # read the file
            # -----------------------
            f = open(FOLDER_NAME + spectra, "rb")

            nextLine = True
            while nextLine:
                # if no header comment those lines
                header = self.read_header(f, HEADER_DEF)
                if bool(header) == False:
                    # self.context.logger.error("Data corrupt go to next line")
                    break
                    continue
                # -------------------------------------------------------
                pixCount = header["Pixel Count"]
                scan = self.read_data(f, pixCount)
                # should include this back again when crc32 is in the headers!
                crc32 = self.read_footer(f, 4)

                # HypernetsReader(self.context).plot_spectra(spectra, scan)

                # fill in dataset
                # maybe xarray has a better way to do - check merge, concat, ...
                series_id = model["series_id"]
                ds["series_id"][scan_number] = series_id

                # estimate time based on timestamp
                ds["acquisition_time"][scan_number] = datetime.datetime.timestamp(
                    acquisitionTime
                )
                #            #print(datetime.fromtimestamp(acquisitionTime))

                #             # didn't use acquisition time from instrument
                #             # possibility that acquisition time is time since reboot, but how to now reboot time?
                #             # if we use the metadata time header
                #             timestamp=header['acquisition_time']
                #             ts = int(timestamp)/1000

                #             date_time_str = timereboot+'UTC'
                #             print(date_time_str)
                #             date_time_obj = datetime.strptime(date_time_str, '%Y%m%dT%H%M%S%Z')
                #             print(date_time_obj)

                #             timereboot = datetime.timestamp(date_time_obj)
                #             print("timereboot =", timereboot)
                #             print(datetime.fromtimestamp(timereboot))

                #             print(datetime.fromtimestamp(int(ts+timereboot)))
                #             print(datetime.fromtimestamp(int(ts+timereboot))-date_time_obj)
                if lat is None:
                    lat = np.nan
                    lon = np.nan
                    sza = np.nan
                    saa = np.nan
                    self.context.logger.error(
                        "Lattitude is not found, using nan values instead for lat, lon, sza and saa."
                    )
                else:
                    sza = 90 - get_altitude(float(lat), float(lon), acquisitionTime)
                    saa = get_azimuth(float(lat), float(lon), acquisitionTime)

                ds.attrs["site_latitude"] = lat
                ds.attrs["site_longitude"] = lon
                ds["solar_zenith_angle"][scan_number] = sza
                ds["solar_azimuth_angle"][scan_number] = saa
                vaa_rel, vza = map(float, specattr["pt_ask"].split(";"))
                vaa = (
                    (ds["solar_azimuth_angle"][scan_number].values + vaa_rel) / 360
                    - int(
                        (ds["solar_azimuth_angle"][scan_number].values + vaa_rel) / 360
                    )
                ) * 360

                ds["quality_flag"][scan_number] = flag
                ds["integration_time"][scan_number] = header["integration_time"]
                ds["temperature"][scan_number] = header["temperature"]

                ds["viewing_azimuth_angle"][scan_number] = vaa
                ds["viewing_zenith_angle"][scan_number] = vza
                # accelaration:
                # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                # acceleration measurements respectively. These are factory-calibrated steady-state
                # reference acceleration measurements of the gravity vector when instrument is in
                # horizontal position. Due to device manufacturing tolerances, these are
                # device-specific and should be applied, when estimating tilt from the measured
                # acceleration data. Each measurement is bit count of full range Â±19.6 m sâˆ’2 .
                # Acceleration for each axis can be calculated per Eq. (4).

                a = 19.6
                b = 2**15
                ds["acceleration_x_mean"][scan_number] = (
                    header["acceleration_x_mean"] * a / b
                )
                ds["acceleration_x_std"][scan_number] = (
                    header["acceleration_x_std"] * a / b
                )
                ds["acceleration_y_mean"][scan_number] = (
                    header["acceleration_y_mean"] * a / b
                )
                ds["acceleration_y_std"][scan_number] = (
                    header["acceleration_y_std"] * a / b
                )
                ds["acceleration_z_mean"][scan_number] = (
                    header["acceleration_z_mean"] * a / b
                )
                ds["acceleration_z_std"][scan_number] = (
                    header["acceleration_z_std"] * a / b
                )
                ds["digital_number"][0:pixCount, scan_number] = scan

                scan_number += 1
                if f.tell() == eof:
                    nextLine = False

        return ds

    def read_series_L(
        self,
        seq_dir,
        series,
        lat,
        lon,
        metadata,
        flag,
        fileformat,
        cal_data,
        cal_data_swir,
        instrument_id,
        site_id,
    ):
        FOLDER_NAME = os.path.join(seq_dir, "RADIOMETER/")
        model_name = self.model

        # read all spectra (== spe files with concanated files) in a series
        vnir = []
        swir = []
        missingfiles = False
        for spectra in series:
            self.context.logger.debug("processing " + spectra)
            model = dict(zip(model_name, spectra.split("_")[:-1]))
            specBlock = (
                model["series_rep"]
                + "_"
                + model["series_id"]
                + "_"
                + model["vaa"]
                + "_"
                + model["azimuth_ref"]
                + "_"
                + model["vza"]
            )
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])
            vaa, vza = map(float, specattr["pt_ask"].split(";"))

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(
                acquisitionTime + "UTC", "%Y%m%dT%H%M%S%Z"
            )
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            # -----------------------
            # read the file
            # -----------------------
            try:
                with open(FOLDER_NAME + spectra, "rb") as f:
                    f.seek(0, 2)
                    file_size = f.tell()
                    f.seek(0)
                    byte_pointer = 0
                    chunk_size = 1
                    chunk_counter = 1
                    while file_size - byte_pointer:
                        self.context.logger.debug(
                            "Parsing chunk No {}, size {} bytes, bytes left: {}".format(
                                chunk_counter, chunk_size, file_size - byte_pointer
                            )
                        )
                        chunk_size = unpack("<H", f.read(2))[0]
                        if chunk_size == 4119:
                            chunk_size = 4131
                        f.seek(byte_pointer)
                        chunk_body = f.read(chunk_size)
                        spectrum = Spectrum.parse_raw(chunk_body)

                        if len(spectrum.body) > 500:
                            spectrum_vnir = spectrum
                            if len(vnir) == 0:
                                vnir = np.array(spectrum_vnir.body)
                            else:
                                vnir = np.vstack([vnir, spectrum_vnir.body])
                        else:
                            spectrum_swir = spectrum
                            if len(swir) == 0:
                                swir = np.array(spectrum_swir.body)
                            else:
                                swir = np.vstack([swir, spectrum_swir.body])

                        byte_pointer = f.tell()
                        chunk_counter += 1
            except:
                self.context.logger.info("%s file missing" % (spectra))
                missingfiles = True
                try:
                    vnir = np.vstack([vnir, np.nan * np.array(spectrum_vnir.body)])
                    swir = np.vstack([swir, np.nan * np.array(spectrum_swir.body)])
                except:
                    vnir.append(np.nan)
                    swir.append(np.nan)
                continue

        try:
            self.context.logger.info(
                spectrum_vnir.return_header(),
            )
        except:
            self.context.anomaly_handler.add_anomaly("b")

        # self.context.logger.info(spectrum_swir.return_header())
        print(spectrum_swir.return_header())

        if len(vnir.shape) == 1:
            vnir = vnir[None, :]
        if len(swir.shape) == 1:
            swir = swir[None, :]

        self.context.logger.debug(
            "vnir data shape in combined raw files: %s \n "
            "swir data shape in combined raw files: %s" % (vnir.shape, swir.shape)
        )

        scanDim = vnir.shape[0]
        wvl = self.read_wavelength(vnir.shape[1], cal_data)
        ds = self.templ.l0_template_dataset(wvl, scanDim, fileformat)

        ds.attrs["sequence_id"] = str(os.path.basename(seq_dir))
        ds.attrs["instrument_id"] = str(instrument_id)
        ds.attrs["site_id"] = str(site_id)
        ds.attrs["source_file"] = str(os.path.basename(seq_dir))

        scanDim = swir.shape[0]
        wvl_swir = self.read_wavelength(swir.shape[1], cal_data_swir)
        ds_swir = self.templ.l0_template_dataset(
            wvl_swir, scanDim, fileformat, swir=True
        )

        ds_swir.attrs["sequence_id"] = str(os.path.basename(seq_dir))
        ds_swir.attrs["instrument_id"] = str(instrument_id)
        ds_swir.attrs["site_id"] = str(site_id)
        ds.attrs["source_file"] = str(os.path.basename(seq_dir))

        scan_number = 0
        scan_number_swir = 0
        for spectra in series:
            model = dict(zip(model_name, spectra.split("_")[:-1]))
            specBlock = (
                model["series_rep"]
                + "_"
                + model["series_id"]
                + "_"
                + model["vaa"]
                + "_"
                + model["azimuth_ref"]
                + "_"
                + model["vza"]
            )
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(
                acquisitionTime + "UTC", "%Y%m%dT%H%M%S%Z"
            )
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            # -----------------------
            # read the file
            # -----------------------

            try:
                with open(FOLDER_NAME + spectra, "rb") as f:
                    f.seek(0, 2)
                    file_size = f.tell()
                    f.seek(0)
                    byte_pointer = 0
                    chunk_size = 1
                    chunk_counter = 1
                    while file_size - byte_pointer:
                        chunk_size = unpack("<H", f.read(2))[0]
                        if chunk_size == 4119:
                            chunk_size = 4131
                        f.seek(byte_pointer)
                        chunk_body = f.read(chunk_size)
                        spectrum = Spectrum.parse_raw(chunk_body)
                        if len(spectrum.body) > 500:
                            scan = (
                                spectrum.body
                            )  # should include this back again when crc32 is in the headers!  #crc32 = self.read_footer(f, 4)

                            # HypernetsReader(self.context).plot_spectra(spectra, scan)

                            # fill in dataset  # maybe xarray has a better way to do - check merge, concat, ...

                            ds["integration_time"][
                                scan_number
                            ] = spectrum.header.exposure_time
                            ds["temperature"][scan_number] = spectrum.header.temperature

                            # accelaration:
                            # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                            # acceleration measurements respectively. These are factory-calibrated steady-state
                            # reference acceleration measurements of the gravity vector when instrument is in
                            # horizontal position. Due to device manufacturing tolerances, these are
                            # device-specific and should be applied, when estimating tilt from the measured
                            # acceleration data. Each measurement is bit count of full range Â±19.6 m sâˆ’2 .
                            # Acceleration for each axis can be calculated per Eq. (4).

                            a = 19.6
                            b = 2**15
                            ds["acceleration_x_mean"][scan_number] = (
                                spectrum.header.accel_stats.mean_x * a / b
                            )
                            ds["acceleration_x_std"][scan_number] = (
                                spectrum.header.accel_stats.std_x * a / b
                            )
                            ds["acceleration_y_mean"][scan_number] = (
                                spectrum.header.accel_stats.mean_y * a / b
                            )
                            ds["acceleration_y_std"][scan_number] = (
                                spectrum.header.accel_stats.std_y * a / b
                            )
                            ds["acceleration_z_mean"][scan_number] = (
                                spectrum.header.accel_stats.mean_z * a / b
                            )
                            ds["acceleration_z_std"][scan_number] = (
                                spectrum.header.accel_stats.std_z * a / b
                            )
                            ds["digital_number"][:, scan_number] = scan

                            self.set_series_params(
                                ds,
                                model,
                                scan_number,
                                vaa,
                                vza,
                                acquisitionTime,
                                lat,
                                lon,
                                specattr,
                                flag,
                            )

                            scan_number += 1
                        else:
                            scan = (
                                spectrum.body
                            )  # should include this back again when crc32 is in the headers!  #crc32 = self.read_footer(f, 4)

                            # HypernetsReader(self.context).plot_spectra(spectra, scan)

                            # fill in dataset  # maybe xarray has a better way to do - check merge, concat, ...

                            if spectrum.header.exposure_time > 0:
                                ds_swir["integration_time"][
                                    scan_number_swir
                                ] = spectrum.header.exposure_time
                            else:
                                ds_swir["integration_time"][scan_number_swir] = ds[
                                    "integration_time"
                                ][0]
                            ds_swir["temperature"][
                                scan_number_swir
                            ] = spectrum.header.temperature

                            # accelaration:
                            # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                            # acceleration measurements respectively. These are factory-calibrated steady-state
                            # reference acceleration measurements of the gravity vector when instrument is in
                            # horizontal position. Due to device manufacturing tolerances, these are
                            # device-specific and should be applied, when estimating tilt from the measured
                            # acceleration data. Each measurement is bit count of full range Â±19.6 m sâˆ’2 .
                            # Acceleration for each axis can be calculated per Eq. (4).

                            a = 19.6
                            b = 2**15
                            ds_swir["acceleration_x_mean"][scan_number_swir] = (
                                spectrum.header.accel_stats.mean_x * a / b
                            )
                            ds_swir["acceleration_x_std"][scan_number_swir] = (
                                spectrum.header.accel_stats.std_x * a / b
                            )
                            ds_swir["acceleration_y_mean"][scan_number_swir] = (
                                spectrum.header.accel_stats.mean_y * a / b
                            )
                            ds_swir["acceleration_y_std"][scan_number_swir] = (
                                spectrum.header.accel_stats.std_y * a / b
                            )
                            ds_swir["acceleration_z_mean"][scan_number_swir] = (
                                spectrum.header.accel_stats.mean_z * a / b
                            )
                            ds_swir["acceleration_z_std"][scan_number_swir] = (
                                spectrum.header.accel_stats.std_z * a / b
                            )
                            ds_swir["digital_number"][:, scan_number_swir] = scan

                            self.set_series_params(
                                ds_swir,
                                model,
                                scan_number_swir,
                                vaa,
                                vza,
                                acquisitionTime,
                                lat,
                                lon,
                                specattr,
                                flag,
                            )

                            scan_number_swir += 1

                        byte_pointer = f.tell()
                        chunk_counter += 1
            except:
                self.set_series_params(
                    ds_swir,
                    model,
                    scan_number_swir,
                    vaa,
                    vza,
                    acquisitionTime,
                    lat,
                    lon,
                    specattr,
                    flag,
                )
                self.set_series_params(
                    ds,
                    model,
                    scan_number,
                    vaa,
                    vza,
                    acquisitionTime,
                    lat,
                    lon,
                    specattr,
                    flag,
                )

                scan_number += 1
                scan_number_swir += 1
                continue

        if missingfiles:
            self.context.anomaly_handler.add_anomaly("s", ds)

        return ds, ds_swir

    def set_series_params(
        self,
        ds,
        model,
        scan_number,
        vaa,
        vza,
        acquisitionTime,
        lat,
        lon,
        specattr,
        flag,
    ):
        series_id = model["series_id"]
        ds["series_id"][scan_number] = series_id
        ds["viewing_azimuth_angle"][scan_number] = vaa
        ds["viewing_zenith_angle"][scan_number] = vza

        # estimate time based on timestamp
        ds["acquisition_time"][scan_number] = datetime.datetime.timestamp(
            acquisitionTime
        )

        if lat is None:
            lat = np.nan
            lon = np.nan
            sza = np.nan
            saa = np.nan
            self.context.logger.error(
                "Lattitude is not found, using nan values instead for lat, lon, sza and saa."
            )
        else:
            sza = 90 - get_altitude(float(lat), float(lon), acquisitionTime)
            saa = get_azimuth(float(lat), float(lon), acquisitionTime)

        vaa, vza = map(float, specattr["pt_ask"].split(";"))
        if vza == -1 and vaa == -1:
            self.context.logger.warning("vza and vaa are both -1, using pt_abs instead")
            vaa, vza = map(float, specattr["pt_abs"].split(";"))
        if vza > 180:
            self.context.logger.debug(
                "vza is larger than 90degrees, changing to equivalent geometry with vza<90."
            )
            vza = 360 - vza
            vaa = vaa + 180

        if vaa > 360:
            vaa = vaa - 360

        ds.attrs["site_latitude"] = lat
        ds.attrs["site_longitude"] = lon
        ds["solar_zenith_angle"][scan_number] = sza
        ds["solar_azimuth_angle"][scan_number] = saa

        ds["quality_flag"][scan_number] = flag

        ds["viewing_azimuth_angle"][scan_number] = vaa
        ds["viewing_zenith_angle"][scan_number] = vza

    def read_metadata(self, seq_dir):
        model_name = self.model
        flag = 0
        #     Spectra name : AA_BBB_CCCC_D_EEEE_FFF_GG_HHHH_II_JJJJ.spe

        #     A : iterator over "the sequence repeat time"
        #     B : Number of the line in the sequence file (csv file)
        #     C : azimuth pointing angle
        #     D : reference for the azimuth angle
        #     E : zenith pointing angle
        #     F : mode
        #     G : action
        #     H : integration time
        #     I : number of scan in the serie
        #     J : serie time
        #     .spe : extension

        #     D (reference) :
        #     0 = abs
        #     1 = nor
        #     2 = sun

        #     F (mode) :
        #     MODE_NONE  : 0x00 (000)
        #     MODE_SWIR  : 0X40 (064)
        #     MODE_VIS   : 0x80 (128)
        #     MODE_BOTH  : 0xC0 (192)

        #     G (action) :
        #     ACTION_BLACK : 0x00   (00)
        #     ACTION_RAD   : 0x10   (16)
        #     ACTION_IRR   : 0x08   (08)
        #     ACTION_CAL   : 0x01   (01)
        #     ACTION_PIC   : 0x02   (02)
        #     ACTION_NONE  : 0x03   (03)

        metadata = ConfigParser()
        if os.path.exists(os.path.join(seq_dir, "metadata.txt")):
            metadata.read(os.path.join(seq_dir, "metadata.txt"))
            # ------------------------------
            # global attributes + wavelengths -> need to check for swir
            # ----------------------------------
            if metadata.has_section("Metadata"):
                globalattr = dict(metadata["Metadata"])
            else:
                globalattr = []

            # reboot time if we want to use acquisition time
            # timereboot=globalattr['datetime']
            # look for latitude and longitude or lat and lon , more elegant way??
            if self.context.get_config_value("use_config_latlon"):
                lat = self.context.get_config_value("lat")

            elif "latitude" in (globalattr.keys()):
                lat = float(globalattr["latitude"])
                if lat == 0.0:
                    print("Latitude is 0.0, use default or add it in metadata.txt")
                    lat = self.context.get_config_value("lat")
                    flag = flag + 2 ** FLAG_COMMON.index("lat_default")
            elif "lat" in (globalattr.keys()):
                lat = float(globalattr["lat"])
                if lat == 0.0:
                    print("Latitude is 0.0, use default or add it in metadata.txt")
                    lat = self.context.get_config_value("lat")
                    flag = flag + 2 ** FLAG_COMMON.index("lat_default")
            else:
                print("Latitude is not given, use default or add it in metadata.txt")
                lat = self.context.get_config_value("lat")
                flag = flag + 2 ** FLAG_COMMON.index("lat_default")

            if self.context.get_config_value("use_config_latlon"):
                lon = self.context.get_config_value("lon")

            elif "longitude" in (globalattr.keys()):
                lon = float(globalattr["longitude"])
                if lon == 0.0:
                    print("Latitude is 0.0, use default or add it in metadata.txt")
                    lon = self.context.get_config_value("lon")
                    flag = flag + 2 ** FLAG_COMMON.index("lon_default")
            elif "lon" in (globalattr.keys()):
                lon = float(globalattr["lon"])
                if lon == 0.0:
                    print("Longitude is 0.0, use default or add it in metadata.txt")
                    lon = self.context.get_config_value("lon")
                    flag = flag + 2 ** FLAG_COMMON.index("lon_default")
            else:
                print("Longitude is not given, use default or add it in metadata.txt")
                lon = self.context.get_config_value("lon")
                flag = flag + 2 ** FLAG_COMMON.index("lon_default")

            if "hypstar_sn" in (globalattr.keys()):
                instrument_id = int(globalattr["hypstar_sn"])
            elif "sn_hypstar" in (globalattr.keys()):
                instrument_id = int(globalattr["sn_hypstar"])
            else:
                instrument_id = self.context.get_config_value("hypstar_cal_number")
                self.context.logger.error("No SN for hypstar instrument!")
                # self.context.anomaly_handler.add_anomaly("x")
            # if 'site_name' in (globalattr.keys()):
            #     site_id = str(globalattr['site_name']).strip()
            # else:
            site_id = self.context.get_config_value("site_id")

            # 2. Estimate wavelengths - NEED TO CHANGE HERE!!!!!!
            # ----------------------
            # from 1 to 14 cause only able to read the visible wavelengths.... how to read the swir once?
            # to change!!!!

            if "cc" not in globalattr:
                cc = self.cc_vis
            else:
                cc = list(str.split(globalattr["cc"], "\n"))
                cc = {
                    k.strip(): float(v.strip())
                    for k, v in (i.split(":") for i in cc[1:14])
                }

            # 3. Read series
            # ---------------------------
            # check for radiance and irradiance series within the metadata
            series_all = metadata.sections()[1 : len(metadata)]
            seriesName = []
            seriesPict = []
            for i in series_all:
                seriesattr = dict(metadata[i])
                seriesName.extend(list(name for name in seriesattr if ".spe" in name))
                seriesPict.extend(list(name for name in seriesattr if ".jpg" in name))

            # ----------------
            # Make list per action
            # ----------------
            #     ACTION_BLACK : 0x00   (00)
            #     ACTION_RAD   : 0x10   (16)
            #     ACTION_IRR   : 0x08   (08)
            #     ACTION_CAL   : 0x01   (01)
            #     ACTION_PIC   : 0x02   (02) - NOT IN THE FILENAME!
            #     ACTION_NONE  : 0x03   (03)
            index_action = model_name.index("action")
            action = [re.split("_|\.", i)[index_action] for i in seriesName]
            # self.context.logger.info(action)

            # this is slow????
            seriesIrr = [x for x, y in zip(seriesName, action) if int(y) == 8]
            seriesBlack = [x for x, y in zip(seriesName, action) if int(y) == 0]
            seriesRad = [x for x, y in zip(seriesName, action) if int(y) == 16]

        else:
            self.context.logger.error("Metadata missing")
            self.context.anomaly_handler.add_anomaly("m")

        return (
            lat,
            lon,
            cc,
            metadata,
            seriesIrr,
            seriesRad,
            seriesBlack,
            seriesPict,
            flag,
            instrument_id,
            site_id,
        )

    def read_aux(self, seq_dir):
        if os.path.exists(os.path.join(seq_dir, "meteo.csv")):
            met = open(os.path.join(seq_dir, "meteo.csv"))
            for line in met.readlines():
                aux = pd.DataFrame(line.replace("&#039;C", "Â°C").split(";"))
                data = pd.concat(
                    [
                        pd.DataFrame(
                            aux.iloc[i].str.extract(r"(\d+.\d+)").astype("float")
                        )
                        for i in range(aux.size)
                    ],
                    axis=1,
                    ignore_index=True,
                )

            data.columns = ["temp", "RH", "pressure", "lux"]
            return data["temp"].values, data["RH"].values, data["pressure"].values, data["lux"].values

        else:
            self.context.logger.error(
                "Missing meteo file in sequence directory. No meteo data added to your output file."
            )
            self.context.anomaly_handler.add_anomaly("e")
            return None, None, None, None

    def read_sequence(
        self,
        seq_dir,
        calibration_data_rad,
        calibration_data_irr,
        calibration_data_swir_rad=None,
        calibration_data_swir_irr=None,
    ):

        # define data to return none at end of method if does not exist
        l0_irr = None
        l0_rad = None
        l0_bla = None
        l0_swir_irr = None
        l0_swir_rad = None
        l0_swir_bla = None

        (
            lat,
            lon,
            cc,
            metadata,
            seriesIrr,
            seriesRad,
            seriesBlack,
            seriesPict,
            flag,
            instrument_id,
            site_id,
        ) = self.read_metadata(seq_dir)

        if seriesIrr:
            if self.context.get_config_value("network") == "w":
                l0_irr = self.read_series(
                    seq_dir,
                    seriesIrr,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0_IRR",
                    calibration_data_irr,
                    instrument_id,
                    site_id,
                )
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_irr, overwrite=True)
            else:
                self.context.logger.info("reading irradiance, info for last scan:")
                l0_irr, l0_swir_irr = self.read_series_L(
                    seq_dir,
                    seriesIrr,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0_IRR",
                    calibration_data_irr,
                    calibration_data_swir_irr,
                    instrument_id,
                    site_id,
                )
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_irr, overwrite=True)
                    self.writer.write(l0_swir_irr, overwrite=True)

        else:
            self.context.logger.error("No irradiance data for this sequence")

        if seriesRad:
            if self.context.get_config_value("network") == "w":
                l0_rad = self.read_series(
                    seq_dir,
                    seriesRad,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0_RAD",
                    calibration_data_rad,
                    instrument_id,
                    site_id,
                )
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_rad, overwrite=True)
            else:
                self.context.logger.info("reading radiance, info for last scan:")
                l0_rad, l0_swir_rad = self.read_series_L(
                    seq_dir,
                    seriesRad,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0_RAD",
                    calibration_data_rad,
                    calibration_data_swir_rad,
                    instrument_id,
                    site_id,
                )

                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_rad, overwrite=True)
                    self.writer.write(l0_swir_rad, overwrite=True)

        else:
            self.context.logger.error("No radiance data for this sequence")

        if seriesBlack:
            if self.context.get_config_value("network") == "w":
                l0_bla = self.read_series(
                    seq_dir,
                    seriesBlack,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0_BLA",
                    calibration_data_rad,
                    instrument_id,
                    site_id,
                )
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_bla, overwrite=True)
            else:
                self.context.logger.info("reading blacks, info for last scan:")
                l0_bla, l0_swir_bla = self.read_series_L(
                    seq_dir,
                    seriesBlack,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0_BLA",
                    calibration_data_rad,
                    calibration_data_swir_rad,
                    instrument_id,
                    site_id,
                )
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_bla, overwrite=True)
                    self.writer.write(l0_swir_bla, overwrite=True)

        else:
            self.context.logger.error("No black data for this sequence")

        if seriesPict:
            for i in seriesPict:
                seriesid = (i.replace(".jpg", "")).split("_", 5)[1]
                va = (i.replace(".jpg", "")).split("_", 5)[2]
                aa = (i.replace(".jpg", "")).split("_", 5)[4]
                date_time_obj = datetime.datetime.strptime(
                    os.path.basename(seq_dir).replace("SEQ", ""), "%Y%m%dT%H%M%S"
                )
                date_time_obj = date_time_obj.replace(tzinfo=timezone.utc)

                if aa == "-001":
                    aa = get_azimuth(
                        float(lat),
                        float(lon),
                        date_time_obj,
                    )
                if va == "-001":
                    va = 90 - get_altitude(float(lat), float(lon), date_time_obj)
                angles = "{}_{}_{}".format(seriesid, round(float(aa)), round(float(va)))
                imagename = self.produt.create_product_name(
                    "IMG",
                    network=self.context.get_config_value("network"),
                    site_id=site_id,
                    time=os.path.basename(seq_dir).replace("SEQ", ""),
                    version=None,
                    swir=None,
                    angles=angles,
                )
                directory = self.writer.return_image_directory()
                if not os.path.exists(directory):
                    os.makedirs(directory)
                path = os.path.join(directory, imagename) + ".jpg"
                if os.path.exists(os.path.join(seq_dir, "RADIOMETER/" + i)):
                    shutil.copy(os.path.join(seq_dir, "RADIOMETER/" + i), path)

        else:
            self.context.logger.error("No pictures for this sequence")
        if self.context.get_config_value("network") == "w":
            return l0_irr, l0_rad, l0_bla
        else:
            return l0_irr, l0_rad, l0_bla, l0_swir_irr, l0_swir_rad, l0_swir_bla


if __name__ == "__main__":
    pass
