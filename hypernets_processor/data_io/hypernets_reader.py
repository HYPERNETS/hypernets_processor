"""
Module with functions and classes to read Hypernets data
"""

from hypernets_processor.version import __version__
import xarray as xr
from os import listdir, mkdir, path
from struct import unpack
from datetime import date # noqa
from sys import exit, version_info # noqa
import matplotlib.pyplot as plt


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "12/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def read_hypernets_data(filename):

    dataset = None

    return dataset


class HypernetsReader:

    # READ METADATA
    # CG - 20200331
    # includes gen2dict, extract_metadata, read_metadata
    # convert generator to dictionary 

    def gen2dict(self,lst):
        dic = {}
        for i in range(1,len(lst)):
            m=lst[i].split("=")
            dic[m[0]] = m[1]
        return(dic)

    # extract metadata from metadata and record as generator
    def extract_metadata(self,path_to_file):
        with open(path_to_file) as f:
            values = []
            for idx, line in enumerate(f):
                #if idx < 6:
                    # Ignore header lines, currently not required 31/03/2020
                #    continue
                if line.strip():
                    # Add the values in this line to the current
                    # values list.
                    line = line.strip()
                    values.extend(line.split('\t'))
                    #values.extend(xr.Dataset(line))
                else:
                    # Blank line, so output values and
                    # clear the list.
                    yield values
                    del values[:]
            # Yield the final set of values, assuming
            # the last line of the file is not blank.
            yield values

    # read metadata as a dictionnary 
    def read_metadata(self,path_to_file):
        gen=self.extract_metadata(path_to_file)
        metadic = {}
        for x in gen:
            metadic[x[0]] = self.gen2dict(x)
        return(metadic)

    # READ RAW SPE data
    # CG - 20200331
    # includes read_spectra, plot_spectra (author: A. Corrozi)
    # convert generator to dictionary      

    def read_spectra(self,spectra,FOLDER_NAME): # noqa
        with open(FOLDER_NAME+spectra, "rb") as f:
            print("="*80)
            print("Spectra name : %s" % spectra)
            print("_".join(spectra.split("_")[:5]))
            print("-"*80)

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

                    if specInfo[7]: strInfo += "VIS " # noqa
                    if specInfo[6]: strInfo += "SWIR " # noqa

                    if not specInfo[3] and not specInfo[4]: strInfo += "Dark" #noqa
                    if specInfo[3] and not specInfo[4]: strInfo += "Irr" # noqa
                    if specInfo[4] and not specInfo[3]: strInfo += "Rad" # noqa
                    if specInfo[3] and specInfo[4]: strInfo += "Error" # noqa

                    print("Spectrum Type Info : %s " % strInfo)

                print("-"*80)

            print("="*80)

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
                print("="*80)
                print("Remaining %i bytes data)" % len(end))

                if version_info > (3, 0):
                    print("%02X " * len(end) % (tuple([b for b in end])))
                else:
                    print("%02X " * len(end) % (tuple([ord(b) for b in end])))

                print("="*80)

            print("Data Spectra Length %i" % len(dataSpectra))

            # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
            # Faster method but less option
            # data = f.read(2 * int(unpackData))  # Last read data is count     #
            # dataSpectra = list(unpack('<' + 'H' * int(unpackData), data))     #
            # print(dataSpectra)
            # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX

            return dataSpectra



    def plot_spectra(self,spectra,dataSpectra):
            plt.clf()
            plt.title(spectra)
            plt.plot([i for i in range(len(dataSpectra))], dataSpectra)
            plt.show()



if __name__ == '__main__':
    pass
