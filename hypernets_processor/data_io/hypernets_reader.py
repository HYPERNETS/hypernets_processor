"""
Module with functions and classes to read Hypernets data
"""
import os
from datetime import date  # noqa
from sys import exit, version_info  # noqa
from sys import exit, version_info  # noqa
from struct import unpack
from configparser import ConfigParser
import matplotlib.pyplot as plt

from hypernets_processor.version import __version__

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
    # new functions: read_header, read_data, read_footer, read_seq

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
        return(globalmet)

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
        return (dataSpectra)

    def read_header(self, f, headerDef):

        header = {}
        for headLen, headName, headFormat in headerDef:
            print(headName)
            data = f.read(headLen)
            if version_info > (3, 0):
                print("%02X " * headLen % (tuple([b for b in data])))
            else:
                print("%02X " * headLen % (tuple([ord(b) for b in data])))
            var, = unpack(headFormat, data)
            print(var)
            if headName == "Pixel Count": pixel_count = var
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
        return (header)

    def read_footer(self, f, datalength):
        # print(f)
        print("Reading CRC32 ...")
        data = f.read(datalength)
        unpackData, = unpack('<I', data)
        print(unpackData)
        return(unpackData)

    def read_seq(self, seq_dir):
        # Create configparser object and open the file
        metadata = ConfigParser()
        metadata.read(os.path.join(seq_dir, "metadata.txt"))

        # all scans within a sequence - change it!!!!
        spectras = metadata.sections()[1:len(metadata)]
        print(spectras)

        FOLDER_NAME = os.path.join(seq_dir, "RADIOMETER/")

        for spectra in spectras:
            print("=" * 80)
            # there is possibly another way to do this, i.e. dict.keys() ?
            specattr_names = list(metadata[spectra])
            print(specattr_names[0])
            specattr = dict(metadata[spectra])

            model_name = ["seq_rep", "seq_line", "vaa", "azimuth_ref", "vza", "mode", "action", "it", "scan_total",
                          "series_time"]

            # remove extension
            filename = os.path.splitext(specattr_names[0])[0]
            filetype = os.path.splitext(specattr_names[0])[1]
            if filetype == ".spe":
                # create dict
                model = dict(zip(model_name, str.split(filename, "_")))
                print(model)

                # read the spectra
                f = open(FOLDER_NAME + specattr_names[0], "rb")

                # look for the maximum number of lines to read-- maybe not an elegant way to do?
                f.seek(0, 2)  # go to end of file
                eof = f.tell()
                print(eof)
                # get end-of-file position
                f.seek(0, 0)  # go back to start of file
                nextLine = True

                print("=" * 80)
                print("Spectra name : %s" % specattr_names[0])
                print("_".join(spectra.split("_")[:5]))
                print("-" * 80)

                # Header definition with length, description and decoding format
                headerDef = [(2, "Total Dataset Length", '<H'),
                             (1, "Spectrum Type Information", '<c'),
                             (8, "Timestamp", '<Q'),
                             (2, "Exposure Time", '<H'),
                             (4, "Temperature", '<f'),
                             (2, "Pixel Count", '<H'),
                             (2, "Acceleration mean X", '<h'),
                             (2, "Acceleration std X", '<h'),
                             (2, "Acceleration mean Y", '<h'),
                             (2, "Acceleration std Y", '<h'),
                             (2, "Acceleration mean Z", '<h'),
                             (2, "Acceleration std Z", '<h')]

                while nextLine:
                    dataset_len = self.read_header(f, headerDef)
                    scan = self.read_data(f, dataset_len)
                    crc32 = self.read_footer(f, 4)
                    self.plot_spectra(spectra, scan)
                    if f.tell() == eof:
                        nextLine = False

                f.close()

            elif filetype == ".jpg":
                print("image - no processing")


if __name__ == '__main__':
    pass
