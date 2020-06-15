"""
Module with functions and classes to read Hypernets data
"""
import os
from sys import exit, version_info  # noqa
from struct import unpack
from configparser import ConfigParser
import matplotlib.pyplot as plt
import re # for re.split
import numpy as np
from pysolar.solar import *
from datetime import datetime, timezone


from hypernets_processor.version import __version__
from hypernets_processor.data_io.format.header import HEADER_DEF
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder


'''___Authorship___'''
__author__ = "Clémence Goyens"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Clémence Goyens"
__status__ = "Development"


def read_hypernets_data(filename):
    dataset = None

    return dataset

class HypernetsReader:

    # READ METADATA
    # CG - 20200331
    # old functions: gen2dict, extract_metadata, read_metadata, read_metadata 2, read_spectra -> NOT USED TO REMOVE
    # CG - 20200604
    # new functions: read_header, read_data, read_footer, read_seq, read_wavelength

    def gen2dict(self, lst):
        dic = {}
        for i in range(1, len(lst)):
            m = lst[i].split("=")
            dic[m[0]] = m[1]
        return (dic)

    # extract metadata from metadata and record as generator
    def extract_metadata(self, path_to_file):
        with open(path_to_file) as f:
            values = []
            for idx, line in enumerate(f):
                # if idx < 6:
                # Ignore header lines, currently not required 31/03/2020
                # continue
                if line.strip():
                    # Add the values in this line to the current
                    # values list.
                    line = line.strip()
                    values.extend(line.split('\t'))
                    # values.extend(xr.Dataset(line))
                else:
                    # Blank line, so output values and
                    # clear the list.
                    yield values
                    del values[:]
            # Yield the final set of values, assuming
            # the last line of the file is not blank.
            yield values

    # read metadata as a dictionnary 
    def read_metadata(self, path_to_file):
        gen = self.extract_metadata(path_to_file)
        metadic = {}
        for x in gen:
            metadic[x[0]] = self.gen2dict(x)
        return (metadic)

    def read_metadata2(self, path_to_file):

        # Create configparser object and open the file
        metadata = ConfigParser()
        metadata.read(path_to_file)
        print(metadata.sections())
        globalmet = []
        for field, value in dict(metadata[0]).items():
            print("%s is %s" % (field, value))
            globalmet.append([field, value])
        return (globalmet)

        for i, section in enumerate(metadata.sections()):
            print("=" * 80)
            print("Section %i : %s" % (i, section))

            # Same as the case 2:
            for field, value in dict(metadata[section]).items():
                print("%s is %s" % (field, value))
                metarray.append([field, value])

        # ## Case 1 : I already know a section name and a field -------------------------
        # print("Asked pan-tilt for the image is :")
        # print(metadata["01_015_0090_2_0180"]["pt_ask"])  # type : str
        #
        # ## Case 2 : I already know a section name -------------------------------------
        # # I make a dict from the parser according to the section name :
        # headerMetadata = dict(metadata["Metadata"])
        # # Then I read the dictionary
        # for field, value in headerMetadata.items():
        #     print("%s is %s" % (field, value))

        ## Case 3 : I know nothing about the file ------------------------------------
        # Loop over the section with an iterator

        # create array to save later on in netcdf
        metarray = []

        return (metarray)

        # READ RAW SPE data
        # CG - 20200331
        # includes read_spectra, plot_spectra (author: A. Corrozi)
        # convert generator to dictionary

    def read_spectra(self, spectra, FOLDER_NAME):  # noqa
        with open(FOLDER_NAME + spectra, "rb") as f:
            print("=" * 80)
            print("Spectra name : %s" % spectra)
            print("_".join(spectra.split("_")[:5]))
            print("-" * 80)

            # Header definition with length, description and decoding format
            headerDef = [(2, "Total Dataset Length", '<H'),
                         (1, "Spectrum Type Information", '<c'),
                         (8, "Timestamp", '<Q'),
                         (2, "Exposure Time", '<H'),
                         (4, "Temperature", '<f'),
                         (2, "Pixel Count", '<H')]

            for headLen, headName, headFormat in headerDef:

                print(headName)

                data = f.read(headLen)

                if version_info > (3, 0):
                    print("%02X " * headLen % (tuple([b for b in data])))
                else:
                    print("%02X " * headLen % (tuple([ord(b) for b in data])))

                unpackData, = unpack(headFormat, data)

                print(unpackData)

                if headName == "Spectrum Type Information":

                    specInfo = format(ord(data), '#010b')
                    specInfo = ['1' == a for a in reversed(specInfo[2:])]

                    # bit 7 for VIS radiometer,
                    # bit 6 for SWIR,
                    # bit 4 for radiance,
                    # bit 3 for irradiance,
                    # bits 4 and 3 for dark;

                    print(specInfo)

                    strInfo = ""

                    if specInfo[7]: strInfo += "VIS "  # noqa
                    if specInfo[6]: strInfo += "SWIR "  # noqa

                    if not specInfo[3] and not specInfo[4]: strInfo += "Dark"  # noqa
                    if specInfo[3] and not specInfo[4]: strInfo += "Irr"  # noqa
                    if specInfo[4] and not specInfo[3]: strInfo += "Rad"  # noqa
                    if specInfo[3] and specInfo[4]: strInfo += "Error"  # noqa

                    print("Spectrum Type Info : %s " % strInfo)

                print("-" * 80)

            print("=" * 80)

            dataSpectra = []
            prev = 0
            print("Reading Data spectra ...")
            for _ in range(int(unpackData)):  # Last read data is count
                data = f.read(2)

                if len(data) != 2:
                    print("Warning : impossible to read 2 bytes")
                    continue

                # Read data as unsigned short
                unpackData, = unpack('<H', data)
                dataSpectra.append(unpackData)

                prev = unpackData

            # Read remaining data and print raw hex
            end = f.read()
            if len(end) != 0:
                print("=" * 80)
                print("Remaining %i bytes data)" % len(end))

                if version_info > (3, 0):
                    print("%02X " * len(end) % (tuple([b for b in end])))
                else:
                    print("%02X " * len(end) % (tuple([ord(b) for b in end])))

                print("=" * 80)

            print("Data Spectra Length %i" % len(dataSpectra))

            # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
            # Faster method but less option
            # data = f.read(2 * int(unpackData))  # Last read data is count     #
            # dataSpectra = list(unpack('<' + 'H' * int(unpackData), data))     #
            # print(dataSpectra)
            # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX

            return dataSpectra, specInfo

    def plot_spectra(self, spectra, dataSpectra):
        plt.clf()
        plt.title(spectra)
        plt.plot([i for i in range(len(dataSpectra))], dataSpectra)
        plt.show()

    def read_header(self, f, headerDef):

        for headLen, headName, headFormat in headerDef:
            print(headName)
            data = f.read(headLen)
            if version_info > (3, 0):
                print("%02X " * headLen % (tuple([b for b in data])))
            else:
                print("%02X " * headLen % (tuple([ord(b) for b in data])))
            data_len, = unpack(headFormat, data)
            print(data_len)
            if headName == "Pixel Count": pixel_count = data_len
            if headName == "Spectrum Type Information":
                specInfo = format(ord(data), '#010b')
                specInfo = ['1' == a for a in reversed(specInfo[2:])]

                # bit 7 for VIS radiometer,
                # bit 6 for SWIR,
                # bit 4 for radiance,
                # bit 3 for irradiance,
                # bits 4 and 3 for dark;

                print(specInfo)

                strInfo = ""

                if specInfo[7]: strInfo += "VIS "  # noqa
                if specInfo[6]: strInfo += "SWIR "  # noqa

                if not specInfo[3] and not specInfo[4]: strInfo += "Dark"  # noqa
                if specInfo[3] and not specInfo[4]: strInfo += "Irr"  # noqa
                if specInfo[4] and not specInfo[3]: strInfo += "Rad"  # noqa
                if specInfo[3] and specInfo[4]: strInfo += "Error"  # noqa

                print("Spectrum Type Info : %s " % strInfo)

            header[headName] = var
        return header

    def read_data(self, f, data_len):
        # print(f)
        prev = 0
        print("Reading Data spectra ...")
        dataSpectra = []
        print(data_len)
        for i in range(int(data_len)):  # Last read data is count
            # print(i)
            data = f.read(2)
            if len(data) != 2:
                print("Warning : impossible to read 2 bytes")
                break
                continue

            # Read data as unsigned short
            unpackData, = unpack('<H', data)
            dataSpectra.append(unpackData)
            prev = unpackData
        # print(dataSpectra)
        return dataSpectra

    def read_footer(self, f, datalength):
        # print(f)
        print("Reading CRC32 ...")
        data = f.read(datalength)
        unpackData, = unpack('<I', data)
        print(unpackData)

    def read_wavelength(self, cc, pix):
        # or rather have it estimated only once for vis and swir?
        wvl = cc['mapping_vis_a'] + pix * cc['mapping_vis_b'] + pix ** 2 * cc['mapping_vis_c']
        +pix ** 3 * cc['mapping_vis_d'] + pix ** 4 * cc['mapping_vis_e']
        +pix ** 5 * cc['mapping_vis_f']
        print("Wavelength range:", min(wvl), "-", max(wvl))
        return (wvl)

    def read_series(self, seq_dir, series, cc, lat, lon, metadata, fileformat, model_name=None):
        print(series)
        if model_name is None:
            model_name = ["seq_rep", "seq_line", "vaa", "azimuth_ref", "vza", "action", "scan_total"]

        # 1. Read header to create template dataset (including wvl and scan dimensions + end of file!!)
        # ----------------------------------------

        # scan dimension
        index_scan_total = model_name.index("scan_total")

        # scanDim=sum([int(re.split('_|\.', i)[index_scan_total]) for i in series])

        # ------------------------------------------
        # added to consider non concanated files
        scanDims = [int(re.split('_|\.', i)[index_scan_total]) for i in series]
        scanDim = sum(scanDims)

        # rewrite series
        # baseName=["_".join(seriesname.split("_", 7)[:7]) for seriesname in series]
        # print(baseName)
        newSeries = []
        for i in series:
            nbrScans = int(re.split('_|\.', i)[index_scan_total])
            baseName = "_".join(re.split("_|\.", i)[:7])
            n = 1
            while n <= nbrScans:
                new_fname = "{}_{}{}".format(baseName, n, '.spe')
                newSeries.append(new_fname)
                n += 1
        series = newSeries
        # -----------------------------------------

        # wvl dimensions
        FOLDER_NAME = os.path.join(seq_dir, "RADIOMETER/")
        f = open(FOLDER_NAME + series[1], "rb")
        # Header definition with length, description and decoding format

        header = self.read_header(f, HEADER_DEF)
        pix = np.linspace(0, header['Pixel Count'], header['Pixel Count'])
        wvl = self.read_wavelength(cc, pix)

        # look for the maximum number of lines to read-- maybe not an elegant way to do?
        f.seek(0, 2)  # go to end of file
        eof = f.tell()
        f.close()

        # 2. Create template dataset
        # -----------------------------------
        dim_sizes_dict = {"wavelength": len(wvl), "scan": scanDim}

        print("Wvl and Scan Dimensions:", len(wvl), scanDim)
        # use template from variables and metadata in format
        ds = HypernetsDSBuilder.create_ds_template(dim_sizes_dict, fileformat)
        ds["wavelength"] = wvl
        # ds["bandwidth"]=wvl
        ds["scan"] = np.linspace(1, scanDim, scanDim)

        # Keep track of scan number!
        scan_number = 0

        # read all spectra (== spe files with concanated files) in a series

        for spectra in series:

            specBlock = "_".join(spectra.split("_", 5)[:5])

            # spectra attributes from metadata file
            specattr = dict(metadata[specBlock])

            # name of spectra file
            # acquisitionTime = specattr[spectra]
            # acquisitionTime = datetime.strptime(acquisitionTime, '%Y%m%dT%H%M%S')

            # -------------------------------------
            # account for non concanated files
            spec = "_".join(spectra.split("_", 7)[:7]) + ".spe"
            acquisitionTime = specattr[spec]
            acquisitionTime = datetime.strptime(acquisitionTime + "UTC", '%Y%m%dT%H%M%S%Z')

            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            model = dict(zip(model_name, str.split(spectra, "_")))
            # ________________________________________

            # -----------------------
            # read the file
            # -----------------------
            f = open(FOLDER_NAME + spectra, "rb")

            nextLine = True
            while nextLine:
                header = self.read_header(f, HEADER_DEF)
                scan = self.read_data(f, header['Pixel Count'])
                crc32 = self.read_footer(f, 4)

                HypernetsReader().plot_spectra(spectra, scan)

                # fill in dataset
                # maybe xarray has a better way to do - check merge, concat, ...

                # ds["series_id"][scan_number] = spectra.split(".", 1)[1]
                ds["viewing_azimuth_angle"][scan_number] = model['vaa']
                ds["viewing_zenith_angle"][scan_number] = model['vza']

                # estimate time based on timestamp
                ds["acquisition_time"][scan_number] = datetime.timestamp(acquisitionTime)
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

                ds.attrs["site_latitude"] = lat
                ds.attrs["site_longitude"] = lon

                ds["solar_zenith_angle"][scan_number] = get_altitude(float(lat), float(lon), acquisitionTime)
                ds["solar_azimuth_angle"][scan_number] = get_azimuth(float(lat), float(lon), acquisitionTime)

                # ds['quality_flag']
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

                ds['digital_number'][0:header['Pixel Count'], scan_number] = scan

                scan_number += 1

                if f.tell() == eof:
                    nextLine = False

        return ds

    def read_metadata(self, seq_dir, model_name=None):
        if model_name is None:
            model_name = ["seq_rep", "seq_line", "vaa", "azimuth_ref", "vza", "action", "scan_total"]

        metadata = ConfigParser()
        metadata.read(os.path.join(seq_dir, "metadata.txt"))

        # ------------------------------
        # global attributes + wavelengths -> need to check for swir
        # ----------------------------------
        globalattr = dict(metadata['Metadata'])
        seq = globalattr['datetime']
        # reboot time if we want to use acquisition time
        # timereboot=globalattr['datetime']
        # look for latitude and longitude or lat and lon , more elegant way??
        if 'latitude' in globalattr.keys():
            lat = globalattr['latitude']
        else:
            lat = globalattr['lat']

        if 'longitude' in globalattr.keys():
            lon = globalattr['longitude']
        else:
            lon = globalattr['lon']

        # 2. Estimate wavelengths - NEED TO CHANGE HERE!!!!!!
        # ----------------------
        # from 1 to 14 cause only able to read the visible wavelengths.... how to read the swir once?
        # to change!!!!

        cc = {'mapping_vis_a': +1.6499700E+02, 'mapping_vis_b': +4.3321091E-01, 'mapping_vis_c': +3.7714483E-05,
              'mapping_vis_d': +6.6769395E-10, 'mapping_vis_e': -4.0577247E-12, 'mapping_vis_f': +0.0000000E+00}
        # cc=list(str.split(globalattr['cc'], "\n"))
        # cc={k.strip(): float(v.strip()) for k, v in (i.split(":") for i in cc[1:14])}

        # 3. Read series
        # ---------------------------
        # check for radiance and irradiance series within the metadata
        series_all = metadata.sections()[1:len(metadata)]
        seriesName = []
        for i in series_all:
            seriesattr = dict(metadata[i])
            seriesName.extend(list(name for name in seriesattr if '.spe' in name))

        # ----------------
        # Remove pictures from list of series
        # ----------------
        # this could possibly change if action for pictures is included within the filename??
        seriesPict = [name for name in seriesName if '.jpg' in name]
        # remove pictures from list
        for name in seriesPict:
            seriesName.remove(name)

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

        # this is slow????
        seriesIrr = [x for x, y in zip(seriesName, action) if int(y) == 8]
        seriesRad = [x for x, y in zip(seriesName, action) if int(y) == 16]
        seriesBlack = [x for x, y in zip(seriesName, action) if int(y) == 0]

        return seq, lat, lon, cc, metadata, seriesIrr, seriesRad, seriesBlack, seriesPict

    def read_sequence(self, seq_dir):

        # define data to return none at end of method if does not exist
        L0_IRR = None
        L0_RAD = None
        L0_BLA = None

        seq, lat, lon, cc, metadata, seriesIrr, seriesRad, seriesBlack, seriesPict = self.read_metadata(seq_dir)


        if seriesIrr:
            L0_IRR = self.read_series(seq_dir, seriesIrr, cc, lat, lon, metadata, "L0_IRR")

            # can't use this when non concatanted spectra
        #         if all([os.path.isfile(os.path.join(seq_dir,"RADIOMETER/",f)) for f in seriesIrr]):
        #             L0_IRR=read_series(seriesIrr,cc, lat, lon, metadata, "L0_IRR")
        #         else:
        #             print("Irradiance files listed but don't exist")
        else:
            print("No irradiance data for this sequence")

        if seriesRad:
            L0_RAD = self.read_series(seq_dir,seriesRad, cc, lat, lon, metadata, "L0_RAD")
        #         if all([os.path.isfile(os.path.join(seq_dir,"RADIOMETER/",f)) for f in seriesRad]):
        #             L0_RAD=read_series(seriesRad,cc, lat, lon, metadata, "L0_RAD")
        #         else:
        #             print("Radiance files listed but don't exist")
        else:
            print("No radiance data for this sequence")

            #     if seriesBlack:
        #         if all([os.path.isfile(os.path.join(seq_dir,"RADIOMETER/",f)) for f in seriesBlack]):
        #             L0_BLA=read_series(seq_dir,seriesBlack,cc,lat, lon,metadata, "L0_BLA")
        #         else:
        #             print("Black files listed but don't exist")
        #     else:
        #         print("No black data for this sequence")

        if seriesPict:
            print("Here we should move the pictures to some place???")
        else:
            print("No pictures for this sequence")

        return L0_IRR, L0_RAD, L0_BLA


if __name__ == '__main__':
    pass
