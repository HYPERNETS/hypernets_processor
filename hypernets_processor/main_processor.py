"""
Contains main class for orchestrating hypernets data processing jobs
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.plotting.plotting import Plotting
from hypernets_processor.utils.logging import configure_logging
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.context import Context
from hypernets_processor.test.test_functions import setup_test_context, teardown_test_context
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.data_io.product_name_util import ProductNameUtil
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.data_io.calibration_converter import CalibrationConverter

import xarray
import os
import matplotlib.pyplot as plt
from datetime import datetime
from configparser import ConfigParser
import time

import xarray as xr
import numpy as np

'''___Authorship___'''
__author__ = "Pieter De Vis"
__created__ = "15/9/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class HypernetsProcessor:
    """
    Class to orchestrate Hypernets data processing jobs

    :type logger: logging.logger
    :param logger: logger
    """

    def __init__(self,job_config=None,processor_config=None,logger=None):
        """
        Constructor method
        """
        if "job_name" in job_config["Job"].keys():
            name = job_config["Job"]["job_name"]

        logger = configure_logging(config=job_config,name=name)
        self.context = Context(job_config,processor_config,logger)


    def run(self):
        # """
        # Runs hypernets data processing jobs
        # """


        # run L0
        # set_dir = "~/OneDrive/projects/hypernets_processor/hypernets_processor"
        # settings_file = set_dir + '/data/settings/default.txt'
        server_dir = os.path.join(this_directory_path,"data_io/tests/reader/")
        seq_id=self.context.get_config_value("sequence_id")
        print(self.context.get_config_value("write_l0"))

        # seq_dir=server_dir+"reader/SEQ20200625T095941/"
        seq_dir = server_dir + seq_id+"/"


        calcon = CalibrationConverter(self.context)
        cal = Calibrate(self.context, MCsteps=1000)
        intp = Interpolate(self.context, MCsteps=1000)
        surf = SurfaceReflectance(self.context, MCsteps=1000)
        rhymer = RhymerHypstar(self.context)

        calibration_data_rad,calibration_data_irr = calcon.read_calib_files()

        l0_irr,l0_rad,l0_bla = HypernetsReader(self.context).read_sequence(seq_dir,calibration_data_rad,calibration_data_irr)
        #l0_bla["digital_number"].values=l0_bla["digital_number"].values/10.
        l0_irr["integration_time"].values = 1024*np.ones(len(l0_irr["integration_time"]))
        l0_rad["integration_time"].values = 1024*np.ones(len(l0_rad["integration_time"]))
        l0_bla["integration_time"].values = 1024*np.ones(len(l0_bla["integration_time"]))
        FOLDER_NAME = os.path.join(seq_dir,"RADIOMETER/")
        seq_id = os.path.basename(os.path.normpath(seq_dir)).replace("SEQ","")
        print(seq_id)

        print("L1a")
        t1=time.time()
        L1a_rad = cal.calibrate_l1a("radiance", l0_rad, l0_bla, calibration_data_rad)
        L1a_irr = cal.calibrate_l1a("irradiance", l0_irr, l0_bla, calibration_data_irr)
        print("L1a took: ",t1-time.time())


        print("L1b")

        L1b=rhymer.process_l1b(L1a_rad, L1a_irr)
        #
        # print(L1b["corr_systematic_corr_rad_irr_irradiance"])
        # panic
        L1c=rhymer.process_l1c(L1b)
        #L1d_irr = cal.average_l1b("irradiance", L1c)
        L1d= surf.process_l1d(L1c)

        L2a = surf.process_l2(L1d)
        # COMPUTE WATER LEAVING RADIANCE LWN, REFLECTANCE RHOW_NOSC FOR EACH Lu SCAN!

        # wind=RhymerHypstar(context).retrieve_wind(L1c)
        # lw_all, rhow_all, rhow_nosc_all, epsilon, fresnel_coeff = RhymerHypstar(context).fresnelrefl_qc_simil(L1c, wind)
        # print(lw_all)
        # print(rhow_all)
        # print(fresnel_coeff)
        # L1c=
        # average all scans to series
        # L1d

        # AVERAGE LWN, RHOW and RHOW_NOSC
        # L2a
        # print(L1b)
        # # L2a=surf.process(L1c,"LandNetworkProtocol")
        self.context.logger.info("all done!")
        print("all done!")
        return None


if __name__ == "__main__":
    this_directory_path = os.path.abspath(os.path.dirname(__file__))
    processor_config_path= os.path.join(this_directory_path,"etc/processor.config")
    job_config_path= os.path.join(this_directory_path,"etc/job.config")
    processor_config = read_config_file(processor_config_path)
    job_config = read_config_file(job_config_path)
    hp = HypernetsProcessor(job_config=job_config,processor_config=processor_config)
    hp.context.set_config_value("processor_directory",this_directory_path)
    hp.run()
    pass
