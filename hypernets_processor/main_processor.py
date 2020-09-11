"""
Contains main class for orchestrating hypernets data processing jobs
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import InterpolateL1c
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter

from hypernets_processor.test.test_functions import setup_test_context, teardown_test_context
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar

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
        ds_irr = xr.open_dataset('../examples/HYPERNETS_W_VFFR_L0_IRR_202008211547_v0.0.nc')
        ds_rad = xr.open_dataset('../examples/HYPERNETS_W_VFFR_L0_RAD_202008211547_v0.0.nc')
        ds_bla = xr.open_dataset('../examples/HYPERNETS_W_VFFR_L0_BLA_202008211547_v0.0.nc')
        #ds_bla = ds_bla.rename({"digital_number":"dark_signal"})
        #ds_bla["digital_number"].values= ds_bla["digital_number"].values/10.

        temp_name = 'test01'

        context = setup_test_context()

        cal=Calibrate(context,MCsteps=100)
        intp=InterpolateL1c(context,MCsteps=1000)
        surf=SurfaceReflectance(context,MCsteps=1000)

        calibration_data={}
        calibration_data["gains"] = np.ones(len(ds_rad["wavelength"]))
        calibration_data["temp"] = 20*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_random_gains"] = 0.1*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_random_dark_signal"] = np.zeros((len(ds_rad["wavelength"])))
        calibration_data["u_random_temp"] = 1*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_systematic_gains"] = 0.05*np.ones(len(ds_rad["wavelength"]))
        calibration_data["u_systematic_dark_signal"] = np.zeros((len(ds_rad["wavelength"])))
        calibration_data["u_systematic_temp"] = 1*np.ones(len(ds_rad["wavelength"]))

        L1a_rad = cal.calibrate_l1a("radiance",ds_rad,ds_bla,calibration_data,
                                    measurement_function='StandardMeasurementFunction')
        L1a_irr = cal.calibrate_l1a("irradiance",ds_irr,ds_bla,calibration_data,
                                   measurement_function='StandardMeasurementFunction')

        # If NAN or INF in spectra: remove spectra or assign FLAG????

        # QUALITY CHECK: TEMPORAL VARIABILITY IN ED AND LSKY -> ASSIGN FLAG
        L1a_rad=RhymerHypstar(context).qc_scan(L1a_rad,measurandstring="radiance",verbosity=10)
        L1a_irr=RhymerHypstar(context).qc_scan(L1a_irr,measurandstring="irradiance",verbosity=10)
        # QUALITY CHECK: MIN NBR OF SCANS -> ASSIGN FLAG
        L1a_uprad, L1a_downrad, L1a_irr=RhymerHypstar(context).cycleparse(L1a_rad, L1a_irr, verbosity=10)

        L1b_downrad=cal.average_l1b("radiance",L1a_downrad)
        L1b_irr=cal.average_l1b("irradiance",L1a_irr)

        #print(L1b_downrad)
        # INTERPOLATE Lsky and Ed FOR EACH Lu SCAN! Threshold in time -> ASSIGN FLAG
        L1c=intp.interpolate_l1b_w(L1a_uprad,L1b_downrad, L1b_irr,"WaterNetworkInterpolationLinear")

        # COMPUTE WATER LEAVING RADIANCE LWN, REFLECTANCE RHOW_NOSC FOR EACH Lu SCAN!

        wind=RhymerHypstar(context).retrieve_wind(L1c)
        lw_all, rhow_all, rhow_nosc_all, epsilon, fresnel_coeff = RhymerHypstar(context).fresnelrefl_qc_simil(L1c, wind)
        print(lw_all)
        print(rhow_all)
        print(fresnel_coeff)

        # average all scans to series
        # L1d

        # AVERAGE LWN, RHOW and RHOW_NOSC
        # L2a
        #print(L1b)
        # # L2a=surf.process(L1c,"LandNetworkProtocol")


        return None


if __name__ == "__main__":
    hp=HypernetsProcessor()
    hp.run()
    pass
