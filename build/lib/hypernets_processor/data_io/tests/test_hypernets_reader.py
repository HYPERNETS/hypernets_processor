"""
Tests for HypernetsReader class
"""

import unittest
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.version import __version__
import os
import glob

'''___Authorship___'''
__author__ = "Clémence Goyens"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Clémence Goyens"
__status__ = "Development"

this_directory = os.path.dirname(__file__)


# class TestHypernetsReader(unittest.TestCase):
#     # def test_create_default_vector(self):
#     #     du = HypernetsReader()
#     #
#     # def test_hypernets_reader_metadata(self):
#     #     du = HypernetsReader()
#     #     file2read = os.path.join(this_directory, "reader/SEQ20200506T130443", "metadata.txt")
#     #     # create a netcdf file per spectra with global attributes and variable attributes
#     #     du.read_metadata2(file2read)
#     #
#     # def test_hypernets_reader_spe(self):
#     #     du = HypernetsReader()
#     #     radiometer_dir = os.path.join(this_directory, "reader/SEQ20200506T130443", "RADIOMETER/")
#     #     spefiles = [os.path.basename(x) for x in glob.glob(os.path.join(radiometer_dir, "*.spe"))]
#     #     print(spefiles)
#     #     print(radiometer_dir)
#     #     for spectra in spefiles:
#     #         dataspectra = du.read_spectra(spectra, radiometer_dir)
#     #         # print(dataspectra)
#     #         du.plot_spectra(spectra, dataspectra)
#
#     def test_hypernets_reader_seq(self):
#         du = HypernetsReader()
#         this_directory = "/home/cgoyens/OneDrive/BackUpThinkpadClem/Projects/HYPERNETS/NetworkDesign_D52" \
#                          "/DataProcChain/hypernets_processor/hypernets_processor/data_io/tests/"
#         seq_dir = os.path.join(this_directory, "reader/SEQ20200506T130443/")
#         print(seq_dir)
#         du.read_seq(seq_dir)



if __name__ == '__main__':
    unittest.main()
