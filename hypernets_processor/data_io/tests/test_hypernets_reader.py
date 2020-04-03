"""
Tests for HypernetsReader class
"""

import unittest
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.version import __version__
import os
import glob 

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/2/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


PATH_NAME='../../../data/tests/reader/SEQ20200101T090000/'
print(PATH_NAME)        


class TestHypernetsReader(unittest.TestCase):
    def test_create_default_vector(self):
        du = HypernetsReader()


    def test_hypernets_reader_metadata(self):
        du = HypernetsReader()
        file2read=os.path.join(PATH_NAME, "metadata.txt")
        md=du.read_metadata(file2read)
        print(md)
        
    def test_hypernets_reader_spe(self):
        du = HypernetsReader()
        radiometer_dir = os.path.join(PATH_NAME,"RADIOMETER/")
        spefiles = [os.path.basename(x) for x in glob.glob(os.path.join(radiometer_dir,"*.spe"))]
        print(spefiles)
        print(radiometer_dir)
        for spectra in spefiles:
            dataspectra=du.read_spectra(spectra, radiometer_dir)
#             sp.plot(os.path.join(pathfile, spectra),dataspectra)

if __name__ == '__main__':
    unittest.main()
