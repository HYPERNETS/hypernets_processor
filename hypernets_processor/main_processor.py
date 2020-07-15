"""
Contains main class for orchestrating hypernets data processing jobs
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

import xarray as xr
import numpy as np


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class HypernetsProcessor:
    """
    Class to orchestrate Hypernets data processing jobs

    :type logger: logging.logger
    :param logger: logger
    """

    def __init__(self, logger=None):
        """
        Constructor method
        """

        self.logger = logger

    def run(self):
        """
        Runs hypernets data processing jobs
        """
        ds_irr = xr.open_dataset('../examples/HYPERNETS_W_VFFR_L0_IRR_20200611T142927_v0.0.nc')
        ds_rad = xr.open_dataset('../examples/HYPERNETS_W_VFFR_L0_RAD_20200611T142927_v0.0.nc')
        print(ds_rad.keys)

        cal=Calibrate()
        calibration_data={}
        calibration_data["gains"] = np.ones((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["dark_signal"] = np.zeros((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["temp"] = 20*np.ones((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["u_random_gains"] = 0.1*np.ones((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["u_random_dark_signal"] = np.zeros((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["u_random_temp"] = 1*np.ones((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["u_systematic_gains"] = 0.05*np.ones((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["u_systematic_dark_signal"] = np.zeros((len(ds_rad["wavelength"]),len(ds_rad["scan"])))
        calibration_data["u_systematic_temp"] = 1*np.ones((len(ds_rad["wavelength"]),len(ds_rad["scan"])))

        L1_rad=cal.calibrate(ds_rad,calibration_data,measurement_function='StandardMeasurementFunction')
        HypernetsWriter.write(L1_rad,"../examples/test_L1rad.nc",overwrite=True)
        print(L1_rad)
        return None


if __name__ == "__main__":
    hp=HypernetsProcessor()
    hp.run()
    pass
