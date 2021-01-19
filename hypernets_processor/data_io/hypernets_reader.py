"""
Module with functions and classes to read Hypernets data
"""
from datetime import datetime, timezone
import os
import re  # for re.split
from configparser import ConfigParser
from struct import unpack
from sys import version_info  # noqa

import matplotlib.pyplot as plt
import numpy as np
import math
from pysolar.solar import *

from hypernets_processor.data_io.format.header import HEADER_DEF
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.spectrum import Spectrum

from hypernets_processor.version import __version__
from hypernets_processor.data_io.dataset_util import DatasetUtil as du
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

'''___Authorship___'''
__author__ = "Clémence Goyens"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Clémence Goyens"
__status__ = "Development"


class HypernetsReader:

    def __init__(self, context):
        self.context = context
        self.model = self.context.get_config_value("model").split(',')
        self.templ = DataTemplates(context)
        self.writer = HypernetsWriter(context=context)

        cckeys = ['mapping_vis_a', 'mapping_vis_b', 'mapping_vis_c', 'mapping_vis_d', 'mapping_vis_e', 'mapping_vis_f']
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
                self.context.logger.error("Spectra length not similar to header length")
                break
                continue
            # if version_info > (3, 0):
            #     print("%02X " * headLen % (tuple([b for b in data])))
            # else:
            #     print("%02X " * headLen % (tuple([ord(b) for b in data])))
            var, = unpack(headFormat, data)
            if headName == "Pixel Count": pixel_count = var
            if headName == "Spectrum Type Information":
                specInfo = format(ord(data), '#010b')
                specInfo = ['1' == a for a in reversed(specInfo[2:])]

                # bit 7 for VIS radiometer,
                # bit 6 for SWIR,
                # bit 4 for radiance,
                # bit 3 for irradiance,
                # bits 4 and 3 for dark;
                strInfo = ""

                if specInfo[7]: strInfo += "VIS "  # noqa
                if specInfo[6]: strInfo += "SWIR "  # noqa

                if not specInfo[3] and not specInfo[4]: strInfo += "Dark"  # noqa
                if specInfo[3] and not specInfo[4]: strInfo += "Irr"  # noqa
                if specInfo[4] and not specInfo[3]: strInfo += "Rad"  # noqa
                if specInfo[3] and specInfo[4]: strInfo += "Error"  # noqa

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
            unpackData, = unpack('<H', data)
            dataSpectra.append(unpackData)
            prev = unpackData
        return dataSpectra

    def read_footer(self, f, datalength):
        # print(f)
        self.context.logger.debug("Reading CRC32 ...")
        data = f.read(datalength)
        unpackData, = unpack('<I', data)

    def read_wavelength(self, pixcount, cal_data):

        pix=range(pixcount)
        wav_coef=cal_data["wavelength_coefficients"]
        wav_coef_func = np.poly1d(np.flip(wav_coef))

        wvl=wav_coef_func(pix)
        self.context.logger.debug("Wavelength range: %s -%s"%(min(wvl), max(wvl)))

        return wvl

    def read_series_L(self, seq_dir, series, lat, lon, metadata, flag, fileformat, cal_data, cal_data_swir):
        model_name = self.model

        # 1. Read header to create template dataset (including wvl and scan dimensions + end of file!!)
        # ----------------------------------------

        # scan dimension - to have total number of dimensions
        index_scan_total = model_name.index("scan_total")
        # series id
        # ------------------------------------------
        # added to consider concanated files
        scanDim = sum([int(re.split('_|\.', i)[index_scan_total]) for i in series])

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
        f = open(FOLDER_NAME + series[0], "rb")

        # Header definition with length, description and decoding format
        header = self.read_header(f, HEADER_DEF)
        self.context.logger.debug(header)
        pixCount = header['Pixel Count']
        # if bool(header) == False:
        #     print("Data corrupt go to next line")
        #     header = self.read_header(f, HEADER_DEF)

        if pixCount==2048:
            wvl = self.read_wavelength(pixCount,cal_data)
        elif pixCount==256:
            wvl = self.read_wavelength(pixCount,cal_data_swir)
        else:
            self.context.logger.error("The number of wavelength pixels does not match "
                                      "the expected values for VNIR or SWIR.")

        # look for the maximum number of lines to read-- maybe not an elegant way to do?
        f.seek(0, 2)  # go to end of file
        eof = f.tell()
        f.close()

        # 2. Create template dataset
        # -----------------------------------
        # use template from variables and metadata in format
        ds = self.templ.l0_template_dataset(wvl, scanDim, fileformat)

        # Keep track of scan number!
        scan_number = 0

        # read all spectra (== spe files with concanated files) in a series
        for spectra in series:

            model = dict(zip(model_name, spectra.split('_')[:-1]))
            specBlock = model['series_rep'] + '_' + model['series_id'] + '_' + model['vaa'] + '_' + model[
                'azimuth_ref'] + '_' + model['vza']
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(acquisitionTime + "UTC", '%Y%m%dT%H%M%S%Z')
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
            with open(FOLDER_NAME+spectra,"rb") as f:
                f.seek(0,2)
                file_size = f.tell()
                f.seek(0)
                print('file size: {}'.format(file_size))
                byte_pointer = 0
                chunk_size = 1
                chunk_counter = 1
                while file_size-byte_pointer:
                    print('Parsing chunk No {}, size {} bytes, bytes left: {}'.format(
                        chunk_counter,chunk_size,file_size-byte_pointer))
                    chunk_size = unpack('<H',f.read(2))[0]
                    if chunk_size == 4119:
                        chunk_size = 4131
                    f.seek(byte_pointer)
                    chunk_body = f.read(chunk_size)
                    spectrum = Spectrum.parse_raw(chunk_body)
                    spectrum.print_header()
                    print(spectra,scan_number,pixCount,chunk_size,len(spectrum.body))
                    byte_pointer = f.tell()
                    chunk_counter += 1

                    # if no header comment those lines
                    # header = self.read_header(f, HEADER_DEF)
                    # if bool(header) == False:
                    #     self.context.logger.error("Data corrupt go to next line")
                    #     break
                    #     continue
                    # # -------------------------------------------------------
                    #pixCount = spectrum.header.pixel_count
                    scan = spectrum.body
                    # should include this back again when crc32 is in the headers!
                    #crc32 = self.read_footer(f, 4)

                    # HypernetsReader(self.context).plot_spectra(spectra, scan)

                    # fill in dataset
                    # maybe xarray has a better way to do - check merge, concat, ...
                    series_id = model['series_id']
                    ds["series_id"][scan_number] = series_id
                    ds["viewing_azimuth_angle"][scan_number] = model['vaa']
                    ds["viewing_zenith_angle"][scan_number] = model['vza']

                    # estimate time based on timestamp
                    ds["acquisition_time"][scan_number] = datetime.datetime.timestamp(acquisitionTime)
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
                        ds.attrs["site_latitude"] = lat
                        ds.attrs["site_longitude"] = lon
                        ds["solar_zenith_angle"][scan_number] = get_altitude(float(lat), float(lon), acquisitionTime)
                        ds["solar_azimuth_angle"][scan_number] = get_azimuth(float(lat), float(lon), acquisitionTime)
                    else:
                        self.context.logger.error(
                            "Lattitude is not found, using default values instead for lat, lon, sza and saa.")
                    ds['quality_flag'][scan_number] = flag
                    ds['integration_time'][scan_number] = header['integration_time']
                    ds['temperature'][scan_number] = header['temperature']

                    # accelaration:
                    # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                    # acceleration measurements respectively. These are factory-calibrated steady-state
                    # reference acceleration measurements of the gravity vector when instrument is in
                    # horizontal position. Due to device manufacturing tolerances, these are
                    # device-specific and should be applied, when estimating tilt from the measured
                    # acceleration data. Each measurement is bit count of full range ±19.6 m s−2 .
                    # Acceleration for each axis can be calculated per Eq. (4).

                    a = 19.6
                    b = 2 ** 15
                    ds['acceleration_x_mean'][scan_number] = header['acceleration_x_mean'] * a / b
                    ds['acceleration_x_std'][scan_number] = header['acceleration_x_std'] * a / b
                    ds['acceleration_y_mean'][scan_number] = header['acceleration_y_mean'] * a / b
                    ds['acceleration_y_std'][scan_number] = header['acceleration_y_std'] * a / b
                    ds['acceleration_z_mean'][scan_number] = header['acceleration_z_mean'] * a / b
                    ds['acceleration_z_std'][scan_number] = header['acceleration_z_std'] * a / b
                    #ds['digital_number'][0:pixCount, scan_number] = scan

                    scan_number += 1
                    if f.tell() == eof:
                        nextLine = False

        return ds

    def read_series(self, seq_dir, series, lat, lon, metadata, flag, fileformat, cal_data=None, cal_data_swir=None):
        model_name = self.model

        # 1. Read header to create template dataset (including wvl and scan dimensions + end of file!!)
        # ----------------------------------------

        # scan dimension - to have total number of dimensions
        index_scan_total = model_name.index("scan_total")
        # series id
        # ------------------------------------------
        # added to consider concanated files
        scanDim = sum([int(re.split('_|\.', i)[index_scan_total]) for i in series])

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
        pixCount = header['Pixel Count']
        # if bool(header) == False:
        #     print("Data corrupt go to next line")
        #     header = self.read_header(f, HEADER_DEF)

        if pixCount == 2048:
            wvl = self.read_wavelength(pixCount,cal_data)
            # 2. Create template dataset
            # -----------------------------------
            # use template from variables and metadata in format
            ds = self.templ.l0_template_dataset(wvl, scanDim, fileformat)
        else:
            self.context.logger.error("The number of wavelength pixels does not match "
                                      "the expected values for VNIR.")

        # look for the maximum number of lines to read-- maybe not an elegant way to do?
        f.seek(0, 2)  # go to end of file
        eof = f.tell()
        f.close()


        ds.attrs["source_file"]= str(os.path.basename(seq_dir))
        ds["wavelength"] = wvl
        # ds["bandwidth"]=wvl
        ds["scan"] = np.linspace(1, scanDim, scanDim)

        # Keep track of scan number!
        scan_number = 0

        # read all spectra (== spe files with concanated files) in a series
        for spectra in series:

            model = dict(zip(model_name, spectra.split('_')[:-1]))
            specBlock = model['series_rep'] + '_' + model['series_id'] + '_' + model['vaa'] + '_' + model[
                'azimuth_ref'] + '_' + model['vza']
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(acquisitionTime + "UTC", '%Y%m%dT%H%M%S%Z')
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
                    self.context.logger.error("Data corrupt go to next line")
                    break
                    continue
                # -------------------------------------------------------
                pixCount = header['Pixel Count']
                scan = self.read_data(f, pixCount)
                # should include this back again when crc32 is in the headers!
                crc32 = self.read_footer(f, 4)

                # HypernetsReader(self.context).plot_spectra(spectra, scan)

                # fill in dataset
                # maybe xarray has a better way to do - check merge, concat, ...
                series_id = model['series_id']
                ds["series_id"][scan_number] = series_id
                ds["viewing_azimuth_angle"][scan_number] = model['vaa']
                ds["viewing_zenith_angle"][scan_number] = model['vza']

                # estimate time based on timestamp
                ds["acquisition_time"][scan_number] = datetime.datetime.timestamp(acquisitionTime)
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
                    ds.attrs["site_latitude"] = lat
                    ds.attrs["site_longitude"] = lon
                    ds["solar_zenith_angle"][scan_number] = get_altitude(float(lat), float(lon), acquisitionTime)
                    ds["solar_azimuth_angle"][scan_number] = get_azimuth(float(lat), float(lon), acquisitionTime)
                else:
                    self.context.logger.error(
                        "Lattitude is not found, using default values instead for lat, lon, sza and saa.")
                ds['quality_flag'][scan_number] = flag
                ds['integration_time'][scan_number] = header['integration_time']
                ds['temperature'][scan_number] = header['temperature']

                # accelaration:
                # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                # acceleration measurements respectively. These are factory-calibrated steady-state
                # reference acceleration measurements of the gravity vector when instrument is in
                # horizontal position. Due to device manufacturing tolerances, these are
                # device-specific and should be applied, when estimating tilt from the measured
                # acceleration data. Each measurement is bit count of full range ±19.6 m s−2 .
                # Acceleration for each axis can be calculated per Eq. (4).

                a = 19.6
                b = 2 ** 15
                ds['acceleration_x_mean'][scan_number] = header['acceleration_x_mean'] * a / b
                ds['acceleration_x_std'][scan_number] = header['acceleration_x_std'] * a / b
                ds['acceleration_y_mean'][scan_number] = header['acceleration_y_mean'] * a / b
                ds['acceleration_y_std'][scan_number] = header['acceleration_y_std'] * a / b
                ds['acceleration_z_mean'][scan_number] = header['acceleration_z_mean'] * a / b
                ds['acceleration_z_std'][scan_number] = header['acceleration_z_std'] * a / b
                ds['digital_number'][0:pixCount, scan_number] = scan

                scan_number += 1
                if f.tell() == eof:
                    nextLine = False

        return ds

    def read_series_L(self, seq_dir, series, lat, lon, metadata, flag, fileformat, cal_data, cal_data_swir):
        FOLDER_NAME = os.path.join(seq_dir, "RADIOMETER/")
        model_name = self.model

        # read all spectra (== spe files with concanated files) in a series
        vnir=[]
        swir=[]
        for spectra in series:
            self.context.logger.debug("processing "+spectra)
            model = dict(zip(model_name,spectra.split('_')[:-1]))
            specBlock = model['series_rep']+'_'+model['series_id']+'_'+model['vaa']+'_'+\
                        model['azimuth_ref']+'_'+model['vza']
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(acquisitionTime+"UTC",
                                                         '%Y%m%dT%H%M%S%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            # -----------------------
            # read the file
            # -----------------------
            with open(FOLDER_NAME+spectra,"rb") as f:
                f.seek(0,2)
                file_size = f.tell()
                f.seek(0)
                byte_pointer = 0
                chunk_size = 1
                chunk_counter = 1
                while file_size-byte_pointer:
                    self.context.logger.debug('Parsing chunk No {}, size {} bytes, bytes left: {}'.format(
                         chunk_counter,chunk_size,file_size-byte_pointer))
                    chunk_size = unpack('<H',f.read(2))[0]
                    if chunk_size == 4119:
                        chunk_size = 4131
                    f.seek(byte_pointer)
                    chunk_body = f.read(chunk_size)
                    spectrum = Spectrum.parse_raw(chunk_body)
                    #spectrum.print_header()
                    if len(spectrum.body) > 500:
                        if len(vnir)==0:
                            vnir=spectrum.body
                        else:
                            vnir = np.vstack([vnir,spectrum.body])
                    else:
                        if len(swir)==0:
                            swir=spectrum.body
                        else:
                            swir = np.vstack([swir,spectrum.body])

                    byte_pointer = f.tell()
                    chunk_counter += 1
        self.context.logger.debug("vnir data shape in combined raw files: %s \n "
                                  "swir data shape in combined raw files: %s"
                                  %(vnir.shape,swir.shape))

        scanDim=vnir.shape[0]
        wvl = self.read_wavelength(vnir.shape[1],cal_data)
        ds = self.templ.l0_template_dataset(wvl,scanDim,fileformat)

        scanDim=swir.shape[0]
        wvl = self.read_wavelength(swir.shape[1],cal_data_swir)
        ds_swir = self.templ.l0_template_dataset(wvl,scanDim,fileformat,swir=True)

        scan_number=0
        scan_number_swir=0
        for spectra in series:
            model = dict(zip(model_name,spectra.split('_')[:-1]))
            specBlock = model['series_rep']+'_'+model['series_id']+'_'+model[
                'vaa']+'_'+model['azimuth_ref']+'_'+model['vza']
            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            acquisitionTime = specattr[spectra]
            acquisitionTime = datetime.datetime.strptime(
                acquisitionTime+"UTC",'%Y%m%dT%H%M%S%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            # -----------------------
            # read the file
            # -----------------------
            with open(FOLDER_NAME+spectra,"rb") as f:
                f.seek(0,2)
                file_size = f.tell()
                f.seek(0)
                byte_pointer = 0
                chunk_size = 1
                chunk_counter = 1
                while file_size-byte_pointer:
                    chunk_size = unpack('<H',f.read(2))[0]
                    if chunk_size == 4119:
                        chunk_size = 4131
                    f.seek(byte_pointer)
                    chunk_body = f.read(chunk_size)
                    spectrum = Spectrum.parse_raw(chunk_body)
                    #spectrum.print_header()
                    if len(spectrum.body) > 500:
                        scan = spectrum.body  # should include this back again when crc32 is in the headers!  #crc32 = self.read_footer(f, 4)

                        # HypernetsReader(self.context).plot_spectra(spectra, scan)

                        # fill in dataset  # maybe xarray has a better way to do - check merge, concat, ...

                        series_id = model['series_id']
                        ds["series_id"][scan_number] = series_id
                        ds["viewing_azimuth_angle"][scan_number] = model['vaa']
                        ds["viewing_zenith_angle"][scan_number] = model['vza']

                        # estimate time based on timestamp
                        ds["acquisition_time"][
                            scan_number] = datetime.datetime.timestamp(acquisitionTime)
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
                            ds.attrs["site_latitude"] = lat
                            ds.attrs["site_longitude"] = lon
                            ds["solar_zenith_angle"][scan_number] = get_altitude(
                                float(lat),float(lon),acquisitionTime)
                            ds["solar_azimuth_angle"][scan_number] = get_azimuth(
                                float(lat),float(lon),acquisitionTime)
                        else:
                            self.context.logger.error(
                                "Lattitude is not found, using default values instead for lat, lon, sza and saa.")
                        ds['quality_flag'][scan_number] = flag
                        ds['integration_time'][scan_number] = spectrum.header.exposure_time
                        ds['temperature'][scan_number] = spectrum.header.temperature

                        # accelaration:
                        # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                        # acceleration measurements respectively. These are factory-calibrated steady-state
                        # reference acceleration measurements of the gravity vector when instrument is in
                        # horizontal position. Due to device manufacturing tolerances, these are
                        # device-specific and should be applied, when estimating tilt from the measured
                        # acceleration data. Each measurement is bit count of full range ±19.6 m s−2 .
                        # Acceleration for each axis can be calculated per Eq. (4).

                        a = 19.6
                        b = 2**15
                        ds['acceleration_x_mean'][scan_number] = spectrum.header.accel_stats.mean_x*a/b
                        ds['acceleration_x_std'][scan_number] = spectrum.header.accel_stats.std_x*a/b
                        ds['acceleration_y_mean'][scan_number] = spectrum.header.accel_stats.mean_y*a/b
                        ds['acceleration_y_std'][scan_number] = spectrum.header.accel_stats.std_y*a/b
                        ds['acceleration_z_mean'][scan_number] = spectrum.header.accel_stats.mean_z*a/b
                        ds['acceleration_z_std'][scan_number] = spectrum.header.accel_stats.std_z*a/b
                        ds['digital_number'][:,scan_number] = scan
                        scan_number += 1
                    else:
                        scan = spectrum.body  # should include this back again when crc32 is in the headers!  #crc32 = self.read_footer(f, 4)

                        # HypernetsReader(self.context).plot_spectra(spectra, scan)

                        # fill in dataset  # maybe xarray has a better way to do - check merge, concat, ...

                        series_id = model['series_id']
                        ds_swir["series_id"][scan_number_swir] = series_id
                        ds_swir["viewing_azimuth_angle"][scan_number_swir] = model['vaa']
                        ds_swir["viewing_zenith_angle"][scan_number_swir] = model['vza']

                        # estimate time based on timestamp
                        ds_swir["acquisition_time"][
                            scan_number_swir] = datetime.datetime.timestamp(acquisitionTime)
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
                            ds_swir["solar_zenith_angle"][scan_number_swir] = get_altitude(
                                float(lat),float(lon),acquisitionTime)
                            ds_swir["solar_azimuth_angle"][scan_number_swir] = get_azimuth(
                                float(lat),float(lon),acquisitionTime)
                        else:
                            self.context.logger.error(
                                "Lattitude is not found, using default values instead for lat, lon, sza and saa.")
                        ds_swir['quality_flag'][scan_number_swir] = flag
                        ds_swir['integration_time'][scan_number_swir] = spectrum.header.exposure_time
                        ds_swir['temperature'][scan_number_swir] = spectrum.header.temperature

                        # accelaration:
                        # Reference acceleration data contains 3x 16 bit signed integers with X, Y and Z
                        # acceleration measurements respectively. These are factory-calibrated steady-state
                        # reference acceleration measurements of the gravity vector when instrument is in
                        # horizontal position. Due to device manufacturing tolerances, these are
                        # device-specific and should be applied, when estimating tilt from the measured
                        # acceleration data. Each measurement is bit count of full range ±19.6 m s−2 .
                        # Acceleration for each axis can be calculated per Eq. (4).

                        a = 19.6
                        b = 2**15
                        ds_swir['acceleration_x_mean'][scan_number_swir] = spectrum.header.accel_stats.mean_x*a/b
                        ds_swir['acceleration_x_std'][scan_number_swir] = spectrum.header.accel_stats.std_x*a/b
                        ds_swir['acceleration_y_mean'][scan_number_swir] = spectrum.header.accel_stats.mean_y*a/b
                        ds_swir['acceleration_y_std'][scan_number_swir] = spectrum.header.accel_stats.std_y*a/b
                        ds_swir['acceleration_z_mean'][scan_number_swir] = spectrum.header.accel_stats.mean_z*a/b
                        ds_swir['acceleration_z_std'][scan_number_swir] = spectrum.header.accel_stats.std_z*a/b
                        ds_swir['digital_number'][:,scan_number_swir] = scan
                        scan_number_swir += 1

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
        print("seq", os.path.join(seq_dir, "metadata.txt"))
        if os.path.exists(os.path.join(seq_dir, "metadata.txt")):
            metadata.read(os.path.join(seq_dir, "metadata.txt"))
            # ------------------------------
            # global attributes + wavelengths -> need to check for swir
            # ----------------------------------
            globalattr = dict(metadata['Metadata'])
            seq = globalattr['datetime']
            # reboot time if we want to use acquisition time
            # timereboot=globalattr['datetime']
            # look for latitude and longitude or lat and lon , more elegant way??
            if 'latitude' in (globalattr.keys()):
                lat = float(globalattr['latitude'])
            elif 'lat' in (globalattr.keys()):
                lat = float(globalattr['lat'])
            else:
                # self.context.logger.error("Latitude is not given, use default")
                lat = self.context.get_config_value("lat")
                flag = flag + 2 ** self.context.get_config_value("lat_default")  # du.set_flag(flag, "lat_default") #

            if 'longitude' in (globalattr.keys()):
                lon = float(globalattr['longitude'])
            elif 'lon' in (globalattr.keys()):
                lon = float(globalattr['lon'])
            else:
                # self.context.logger.error("Longitude is not given, use default")
                lon = self.context.get_config_value("lon")
                flag = flag + 2 ** self.context.get_config_value("lon_default")  # du.set_flag(flag, "lon_default")  #

            # 2. Estimate wavelengths - NEED TO CHANGE HERE!!!!!!
            # ----------------------
            # from 1 to 14 cause only able to read the visible wavelengths.... how to read the swir once?
            # to change!!!!

            if 'cc' not in globalattr:
                cc = self.cc_vis
            else:
                cc = list(str.split(globalattr['cc'], "\n"))
                cc = {k.strip(): float(v.strip()) for k, v in (i.split(":") for i in cc[1:14])}

            # 3. Read series
            # ---------------------------
            # check for radiance and irradiance series within the metadata
            series_all = metadata.sections()[1:len(metadata)]
            seriesName = []
            seriesPict = []
            for i in series_all:
                seriesattr = dict(metadata[i])
                seriesName.extend(list(name for name in seriesattr if '.spe' in name))
                seriesPict.extend(list(name for name in seriesattr if '.jpg' in name))


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
            action = [re.split('_|\.', i)[index_action] for i in seriesName]
            # self.context.logger.info(action)

            # this is slow????
            seriesIrr = [x for x, y in zip(seriesName, action) if int(y) == 8]
            seriesBlack = [x for x, y in zip(seriesName, action) if int(y) == 0]
            seriesRad = [x for x, y in zip(seriesName, action) if int(y) == 16]

        else:
            self.context.logger.error("Missing metadata file in sequence directory - check sequence directory")
            self.context.anomaly_db.add_anomaly("s")

        return seq, lat, lon, cc, metadata, seriesIrr, seriesRad, seriesBlack, seriesPict, flag

    def read_sequence(self,seq_dir,calibration_data_rad,calibration_data_irr,
                      calibration_data_swir_rad=None,calibration_data_swir_irr=None):

        # define data to return none at end of method if does not exist
        l0_irr = None
        l0_rad = None
        l0_bla = None

        seq,lat,lon,cc,metadata,seriesIrr,seriesRad,seriesBlack,seriesPict,flag = self.read_metadata(
            seq_dir)

        if seriesIrr:
            if self.context.get_config_value("network") == "w":
                l0_irr = self.read_series(seq_dir,seriesIrr,lat,lon,metadata,flag,
                                          "L0_IRR",calibration_data_irr)
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_irr,overwrite=True)
            else:
                l0_irr,l0_swir_irr = self.read_series_L(seq_dir,seriesIrr,lat,lon,
                                                        metadata,flag,"L0_IRR",
                                                        calibration_data_irr,
                                                        calibration_data_swir_irr)
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_irr,overwrite=True)
                    self.writer.write(l0_swir_irr,overwrite=True)

        else:
            self.context.logger.error("No irradiance data for this sequence")

        if seriesRad:
            if self.context.get_config_value("network") == "w":
                l0_rad = self.read_series(seq_dir,seriesRad,lat,lon,metadata,flag,
                                          "L0_RAD",calibration_data_rad)
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_rad,overwrite=True)
            else:
                l0_rad,l0_swir_rad = self.read_series_L(seq_dir,seriesRad,lat,lon,
                                                        metadata,flag,"L0_RAD",
                                                        calibration_data_rad,
                                                        calibration_data_swir_rad)

                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_rad,overwrite=True)
                    self.writer.write(l0_swir_rad,overwrite=True)

        else:
            self.context.logger.error("No radiance data for this sequence")

        if seriesBlack:
            if self.context.get_config_value("network") == "w":
                l0_bla = self.read_series(seq_dir,seriesBlack,lat,lon,metadata,flag,
                                          "L0_BLA",calibration_data_rad)
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_bla,overwrite=True)
            else:
                l0_bla,l0_swir_bla = self.read_series_L(seq_dir,seriesBlack,lat,lon,
                                                        metadata,flag,"L0_BLA",
                                                        calibration_data_rad,
                                                        calibration_data_swir_rad)
                if self.context.get_config_value("write_l0"):
                    self.writer.write(l0_bla,overwrite=True)
                    self.writer.write(l0_swir_bla,overwrite=True)

        else:
            self.context.logger.error("No black data for this sequence")

        if seriesPict:
            print("Here we should move the pictures to some place???")
        else:
            self.context.logger.error("No pictures for this sequence")
        if self.context.get_config_value("network") == "w":
            return l0_irr,l0_rad,l0_bla
        else:
            return l0_irr,l0_rad,l0_bla,l0_swir_irr,l0_swir_rad,l0_swir_bla


if __name__ == '__main__':
    pass
