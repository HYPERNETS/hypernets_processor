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
from hypernets_processor.data_io.normalize_360 import normalizedeg
from hypernets_processor.data_utils.quality_checks import QualityChecks

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
        self.qual = QualityChecks(context)
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
                self.context.logger.warning("Warning : impossible to read 2 bytes")
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

    def read_angles(
        self, ds, scan_number, specattr, offset_pan, offset_tilt, angle2use, land=False
    ):

        paa_ask, vza_ask = map(float, specattr["pt_ask"].split(";"))
        paa_abs, vza_abs = map(float, specattr["pt_abs"].split(";"))
        if specattr.get("pt_ref"):
            paa_ref, vza_ref = map(float, specattr["pt_ref"].split(";"))
        else:
            paa_ref, vza_ref = -999999, -999999

        vza_ask = normalizedeg(float(vza_ask), 0, 360)
        vza_abs = normalizedeg(float(vza_abs), 0, 360)
        if vza_ref > -999:
            vza_ref = normalizedeg(float(vza_ref), 0, 360)

        paa_ask = normalizedeg(float(paa_ask), 0, 360)
        paa_abs = normalizedeg(float(paa_abs), 0, 360)

        if paa_ref > -999:
            paa_ref = normalizedeg(float(paa_ref), 0, 360)

        # perform quality checks
        self.qual.perform_quality_check_angles(
            ds, scan_number, vza_abs, vza_ref, paa_abs, paa_ref
        )

        if (
            ((offset_pan is None) or (offset_tilt is None))
            & (angle2use == "pt_ask")
            & (not land)
        ):
            paa = normalizedeg(
                float(paa_ask) + ds["solar_azimuth_angle"][scan_number], 0, 360
            )
            vza = vza_ask
        elif (
            ((offset_pan is None) or (offset_tilt is None))
            & (angle2use == "pt_ask")
            & (land)
        ):
            paa = normalizedeg(float(paa_ask), 0, 360)
            vza = vza_ask
        elif ((offset_pan is None) or (offset_tilt is None)) & (angle2use == "pt_ref"):
            paa = normalizedeg(float(paa_ref), 0, 360)
            vza = vza_ref
        else:
            paa = normalizedeg(float(paa_ref) + float(offset_pan), 0, 360)
            vza = normalizedeg(float(vza_ref) + float(offset_tilt), 0, 360)

        if vza > 180:
            self.context.logger.debug(
                "tilt is larger than 180 degrees, changing to equivalent geometry with tilt<180."
            )
            vza = 360 - vza
            paa = paa + 180

            vza_ref = 360 - vza_ref
            paa_ref = paa_ref + 180

            vza_abs = 360 - vza_abs
            paa_abs = paa_abs + 180

            vza_ask = 360 - vza_ask
            paa_ask = paa_ask + 180

        ds["paa_ref"][scan_number] = normalizedeg(float(paa_ref), 0, 360)
        ds["paa_ask"][scan_number] = normalizedeg(float(paa_ask), 0, 360)
        ds["paa_abs"][scan_number] = normalizedeg(float(paa_abs), 0, 360)

        # convert from pointing azimuth angle to viewing azimuth angle
        vaa = normalizedeg(paa - 180, 0, 360)

        ds["pointing_azimuth_angle"][scan_number] = paa
        ds["viewing_azimuth_angle"][scan_number] = vaa
        ds["viewing_zenith_angle"][scan_number] = vza

        return ds

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
        azimuth_switch,
        offset_tilt,
        offset_pan,
        angle2use,
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
        print(FOLDER_NAME)
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
            ds = self.templ.l0a_template_dataset(wvl, scanDim, fileformat)
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
        ds["bandwidth"].values = 3 * np.ones_like(wvl)
        ds["scan"] = np.linspace(1, scanDim, scanDim)

        # add auxiliary data to the L0 data
        temp, RH, pressure, lux = self.read_aux(seq_dir)
        ds.attrs["system_temperature"] = temp.values
        ds.attrs["system_relative_humidity"] = RH.values
        ds.attrs["system_pressure"] = pressure.values
        ds.attrs["illuminance"] = lux.values

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
                if lat is not None:
                    ds.attrs["site_latitude"] = lat
                    ds.attrs["site_longitude"] = lon
                    ds["solar_zenith_angle"][scan_number] = 90 - get_altitude(
                        float(lat), float(lon), acquisitionTime
                    )
                    ds["solar_azimuth_angle"][scan_number] = get_azimuth(
                        float(lat), float(lon), acquisitionTime
                    )

                    ds = self.read_angles(
                        ds,
                        scan_number,
                        specattr,
                        offset_pan,
                        offset_tilt,
                        angle2use,
                        land=False,
                    )

                else:
                    self.context.logger.warning(
                        "Latitude is not found, using default values instead for lat, lon, sza and saa."
                    )

                ds["quality_flag"][scan_number] = flag
                ds["integration_time"][scan_number] = header["integration_time"]
                ds["temperature"][scan_number] = header["temperature"]

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
        offset_tilt,
        offset_pan,
        angle2use,
    ):
        FOLDER_NAME = os.path.join(seq_dir, "RADIOMETER/")
        model_name = self.model

        # read all spectra (== spe files with concanated files) in a series
        vnir = []
        swir = []
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

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(
                acquisitionTime + "UTC", "%Y%m%dT%H%M%S%Z"
            )
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            # -----------------------
            # read the file
            # -----------------------
            if os.path.exists(FOLDER_NAME + spectra):
                with open(FOLDER_NAME + spectra, "rb") as f:
                    f.seek(0, 2)
                    file_size = f.tell()
                    f.seek(0)
                    byte_pointer = 0
                    chunk_size = 1
                    chunk_counter = 1
                    while file_size - byte_pointer:
                        try:
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
                                if len(vnir) == 0:
                                    vnir = np.array(spectrum.body)
                                else:
                                    vnir = np.vstack([vnir, spectrum.body])
                            else:
                                if len(swir) == 0:
                                    swir = np.array(spectrum.body)
                                else:
                                    swir = np.vstack([swir, spectrum.body])
                        except:
                            self.context.logger.warning("reading of spectrum failed")

                        byte_pointer = f.tell()
                        chunk_counter += 1
            else:
                self.context.logger.warning(
                    "A file (%s) listed in the metadata.txt is missing." % (spectra)
                )

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
        ds = self.templ.l0a_template_dataset(wvl, scanDim, fileformat)

        ds.attrs["sequence_id"] = str(os.path.basename(seq_dir))
        ds.attrs["instrument_id"] = str(instrument_id)
        ds.attrs["site_id"] = str(site_id)
        ds.attrs["source_file"] = str(os.path.basename(seq_dir))
        ds["bandwidth"].values = 3 * np.ones_like(wvl)

        scanDim = swir.shape[0]
        wvl_swir = self.read_wavelength(swir.shape[1], cal_data_swir)
        ds_swir = self.templ.l0a_template_dataset(
            wvl_swir, scanDim, fileformat, swir=True
        )

        ds_swir.attrs["sequence_id"] = str(os.path.basename(seq_dir))
        ds_swir.attrs["instrument_id"] = str(instrument_id)
        ds_swir.attrs["site_id"] = str(site_id)
        ds_swir.attrs["source_file"] = str(os.path.basename(seq_dir))
        ds_swir["bandwidth"].values = 10 * np.ones_like(wvl_swir)

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
            if os.path.exists(FOLDER_NAME + spectra):
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
                        try:
                            spectrum = Spectrum.parse_raw(chunk_body)

                            if len(spectrum.body) > 500:
                                if scan_number == 0:
                                    print(spectrum.return_header())
                                scan = (
                                    spectrum.body
                                )  # should include this back again when crc32 is in the headers!  #crc32 = self.read_footer(f, 4)

                                series_id = model["series_id"]
                                ds["series_id"][scan_number] = series_id

                                # estimate time based on timestamp
                                ds["acquisition_time"][
                                    scan_number
                                ] = datetime.datetime.timestamp(acquisitionTime)
                                if lat is not None:
                                    ds.attrs["site_latitude"] = lat
                                    ds.attrs["site_longitude"] = lon
                                    ds["solar_zenith_angle"][
                                        scan_number
                                    ] = 90 - get_altitude(
                                        float(lat), float(lon), acquisitionTime
                                    )
                                    ds["solar_azimuth_angle"][
                                        scan_number
                                    ] = get_azimuth(
                                        float(lat), float(lon), acquisitionTime
                                    )
                                elif scan_number == 0:
                                    self.context.logger.warning(
                                        "Lattitude is not found, using default values instead for lat, lon, sza and saa."
                                    )
                                ds["quality_flag"][scan_number] = flag
                                ds["integration_time"][
                                    scan_number
                                ] = spectrum.header.exposure_time
                                ds["temperature"][
                                    scan_number
                                ] = spectrum.header.temperature

                                ds = self.read_angles(
                                    ds,
                                    scan_number,
                                    specattr,
                                    offset_pan,
                                    offset_tilt,
                                    angle2use,
                                    land=True,
                                )

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
                                scan_number += 1

                            else:
                                if scan_number_swir == 0:
                                    print(spectrum.return_header())

                                scan = (
                                    spectrum.body
                                )  # should include this back again when crc32 is in the headers!  #crc32 = self.read_footer(f, 4)

                                series_id = model["series_id"]
                                ds_swir["series_id"][scan_number_swir] = series_id

                                # estimate time based on timestamp
                                ds_swir["acquisition_time"][
                                    scan_number_swir
                                ] = datetime.datetime.timestamp(acquisitionTime)
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
                                if lat is not None:
                                    ds_swir.attrs["site_latitude"] = lat
                                    ds_swir.attrs["site_longitude"] = lon
                                    ds_swir["solar_zenith_angle"][
                                        scan_number_swir
                                    ] = 90 - get_altitude(
                                        float(lat), float(lon), acquisitionTime
                                    )
                                    ds_swir["solar_azimuth_angle"][
                                        scan_number_swir
                                    ] = get_azimuth(
                                        float(lat), float(lon), acquisitionTime
                                    )

                                elif scan_number_swir == 0:
                                    self.context.logger.warning(
                                        "Latitude is not found, using default values instead for lat, lon, sza and saa."
                                    )
                                ds_swir["quality_flag"][scan_number_swir] = flag
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

                                ds_swir = self.read_angles(
                                    ds_swir,
                                    scan_number_swir,
                                    specattr,
                                    offset_pan,
                                    offset_tilt,
                                    angle2use,
                                    land=True,
                                )

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
                                scan_number_swir += 1
                        except:
                            self.context.logger.warning(
                                "reading of spectrum for series %s failed" % series_id
                            )

                        byte_pointer = f.tell()
                        chunk_counter += 1
        return ds, ds_swir

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

            # first retrieve site name to get site specific attributes, if any

            if self.context.get_config_value("site_id") != "TEST":
                site_id = self.context.get_config_value("site_id")
            elif "site_id" in (globalattr.keys()):
                site_id = str(globalattr["site_id"]).strip()
                self.context.set_config_value("site_id", site_id)
            elif "site_name" in (globalattr.keys()):
                site_id = str(globalattr["site_name"]).strip()
                self.context.set_config_value("site_id", site_id)
            else:
                self.context.error("site_id not found. Using default TEST instead.")

            # need to check which angle to use as a reference to calculate vaa (~azimuth swith, offset, ...)
            angle2use = self.context.get_config_value("angle2use")

            sitespec = ConfigParser()
            path_ = os.path.abspath(os.path.join(__file__, "../../.."))
            sitespec_ = os.path.join(
                path_, "data", "site_specific_parameters", "{}.csv".format(site_id)
            )
            sitespecattr = None

            if os.path.exists(sitespec_):
                sitespec.read(sitespec_)
                if sitespec.has_section("Metadata"):
                    sitespecattr = dict(sitespec["Metadata"])
                    angle2use = str(sitespecattr["angle2use"]).strip()

            print("angle used to evaluated azimuth:{}".format(angle2use))

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

            if "azimuth_switch" in (globalattr.keys()):
                azimuth_switch = float(globalattr["azimuth_switch"])
            elif sitespecattr and "azimuth_switch" in (sitespecattr.keys()):
                azimuth_switch = float(sitespecattr["azimuth_switch"])
            else:
                azimuth_switch = None

            if "offset_pan" in (globalattr.keys()):
                offset_pan = float(globalattr["offset_pan"])
            elif sitespecattr and "offset_pan" in (sitespecattr.keys()):
                offset_pan = float(sitespecattr["offset_pan"])
            else:
                offset_pan = None

            if "offset_tilt" in (globalattr.keys()):
                offset_tilt = float(globalattr["offset_tilt"])
            elif sitespecattr and "offset_tilt" in (sitespecattr.keys()):
                offset_tilt = float(sitespecattr["offset_tilt"])
            else:
                offset_tilt = None

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
            azimuth_switch,
            offset_tilt,
            offset_pan,
            angle2use,
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

            # aux = pd.read_csv(os.path.join(seq_dir, "meteo.csv"), sep=";", header=None)
            # data = pd.concat(
            #     [pd.DataFrame(aux.iloc[:, i].str.extract(r'(\d+.\d+)').astype('float')) for i in range(aux.size)],
            #     axis=1, ignore_index=True)
            data.columns = ["temp", "RH", "pressure", "lux"]
        else:
            self.context.logger.warning(
                "Missing meteo file in sequence directory. No meteo data added to your output file."
            )
            self.context.anomaly_handler.add_anomaly("s")

        return data["temp"], data["RH"], data["pressure"], data["lux"]

    def read_sequence(
        self,
        seq_dir,
        calibration_data_rad,
        calibration_data_irr,
        calibration_data_swir_rad=None,
        calibration_data_swir_irr=None,
        single_series=None,
    ):

        # define data to return none at end of method if does not exist
        l0a_irr = None
        l0a_rad = None
        l0a_bla = None
        l0a_swir_irr = None
        l0a_swir_rad = None
        l0a_swir_bla = None

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
            azimuth_switch,
            offset_tilt,
            offset_pan,
            angle2use,
        ) = self.read_metadata(seq_dir)

        if single_series is not None:
            if single_series in seriesIrr:
                seriesIrr = [single_series]
            else:
                seriesIrr = None
            if single_series in seriesRad:
                seriesRad = [single_series]
            else:
                seriesRad = None
            if single_series in seriesBlack:
                seriesBlack = [single_series]
            else:
                seriesBlack = None
            if single_series in seriesPict:
                seriesPict = [single_series]
            else:
                seriesPict = None

        if seriesIrr:
            if self.context.get_config_value("network") == "w":
                l0a_irr = self.read_series(
                    seq_dir,
                    seriesIrr,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0A_IRR",
                    calibration_data_irr,
                    instrument_id,
                    site_id,
                    azimuth_switch,
                    offset_tilt,
                    offset_pan,
                    angle2use,
                )
                if self.context.get_config_value("write_l0a"):
                    self.writer.write(l0a_irr, overwrite=True)
            else:
                l0a_irr, l0a_swir_irr = self.read_series_L(
                    seq_dir,
                    seriesIrr,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0A_IRR",
                    calibration_data_irr,
                    calibration_data_swir_irr,
                    instrument_id,
                    site_id,
                    offset_tilt,
                    offset_pan,
                    angle2use,
                )
                if self.context.get_config_value("write_l0a"):
                    self.writer.write(l0a_irr, overwrite=True)
                    self.writer.write(l0a_swir_irr, overwrite=True)

        else:
            self.context.logger.error("No irradiance data for this sequence")

        if seriesRad:
            if self.context.get_config_value("network") == "w":
                l0a_rad = self.read_series(
                    seq_dir,
                    seriesRad,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0A_RAD",
                    calibration_data_rad,
                    instrument_id,
                    site_id,
                    azimuth_switch,
                    offset_tilt,
                    offset_pan,
                    angle2use,
                )
                if self.context.get_config_value("write_l0a"):
                    self.writer.write(l0a_rad, overwrite=True)
            else:
                l0a_rad, l0a_swir_rad = self.read_series_L(
                    seq_dir,
                    seriesRad,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0A_RAD",
                    calibration_data_rad,
                    calibration_data_swir_rad,
                    instrument_id,
                    site_id,
                    offset_tilt,
                    offset_pan,
                    angle2use,
                )

                if self.context.get_config_value("write_l0a"):
                    self.writer.write(l0a_rad, overwrite=True)
                    self.writer.write(l0a_swir_rad, overwrite=True)

        else:
            self.context.logger.error("No radiance data for this sequence")

        if seriesBlack:
            if self.context.get_config_value("network") == "w":
                l0a_bla = self.read_series(
                    seq_dir,
                    seriesBlack,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0A_BLA",
                    calibration_data_rad,
                    instrument_id,
                    site_id,
                    azimuth_switch,
                    offset_tilt,
                    offset_pan,
                    angle2use,
                )
                if self.context.get_config_value("write_l0a"):
                    self.writer.write(l0a_bla, overwrite=True)
            else:
                l0a_bla, l0a_swir_bla = self.read_series_L(
                    seq_dir,
                    seriesBlack,
                    lat,
                    lon,
                    metadata,
                    flag,
                    "L0A_BLA",
                    calibration_data_rad,
                    calibration_data_swir_rad,
                    instrument_id,
                    site_id,
                    offset_tilt,
                    offset_pan,
                    angle2use,
                )
                if self.context.get_config_value("write_l0a"):
                    self.writer.write(l0a_bla, overwrite=True)
                    self.writer.write(l0a_swir_bla, overwrite=True)

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
            self.context.logger.warning("No pictures for this sequence")
        if self.context.get_config_value("network") == "w":
            return l0a_irr, l0a_rad, l0a_bla
        else:
            return l0a_irr, l0a_rad, l0a_bla, l0a_swir_irr, l0a_swir_rad, l0a_swir_bla


if __name__ == "__main__":
    pass
