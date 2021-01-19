"""
Contains main class for orchestrating hypernets data processing jobs
"""
from datetime import datetime, timezone
from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.combine_SWIR.combine_SWIR import CombineSWIR
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
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
        self.context.set_config_value("site_abbr","OUTD")

    def run(self):
        # """
        # Runs hypernets data processing jobs
        # """


        # run L0
        # set_dir = "~/OneDrive/projects/hypernets_processor/hypernets_processor"
        # settings_file = set_dir + '/data/settings/default.txt'
        server_dir = os.path.join(this_directory_path,"data_io/tests/reader/")
        seq_id=self.context.get_config_value("sequence_id")

        # seq_dir=server_dir+"reader/SEQ20200625T095941/"
        seq_dir = self.context.get_config_value("raw_data_directory")


        calcon = CalibrationConverter(self.context)
        cal = Calibrate(self.context,MCsteps=100)
        surf = SurfaceReflectance(self.context,MCsteps=1000)

        if self.context.get_config_value("network") == "l":
            comb = CombineSWIR(self.context,MCsteps=100)
            intp = Interpolate(self.context,MCsteps=1000)

            (calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,
             calibration_data_swir_irr) = calcon.read_calib_files()
            l0_irr,l0_rad,l0_bla,l0_swir_irr,l0_swir_rad,l0_swir_bla = HypernetsReader(self.context).read_sequence(seq_dir,
                                                                               calibration_data_rad,
                                                                               calibration_data_irr,
                                                                               calibration_data_swir_rad,
                                                                               calibration_data_swir_irr)

            self.context.logger.debug("Processing to L1a...")
            print("Processing to L1a radiance...")
            t1=time.time()
            L1a_rad = cal.calibrate_l1a("radiance",l0_rad,l0_bla,calibration_data_rad)
            L1a_irr = cal.calibrate_l1a("irradiance",l0_irr,l0_bla,calibration_data_irr)
            t2=time.time()
            print(t2-t1)
            L1a_swir_rad = cal.calibrate_l1a("radiance",l0_swir_rad,l0_swir_bla,calibration_data_swir_rad,swir=True)
            L1a_swir_irr = cal.calibrate_l1a("irradiance",l0_swir_irr,l0_swir_bla,calibration_data_swir_irr,swir=True)
            t3=time.time()
            print(t3-t2)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L1b radiance...")
            print("Processing to L1b radiance...")
            L1b_rad = comb.combine("radiance",L1a_rad,L1a_swir_rad)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L1b irradiance...")
            L1b_irr = comb.combine("irradiance",L1a_irr,L1a_swir_irr)
            self.context.logger.debug("Done")

            # L1b_rad=xarray.open_dataset(r"C:\Users\pdv\PycharmProjects\hypernets_processor\hypernets_processor\out\HYPERNETS_L_OUTD_L1B_RAD_v0.1.nc")
            # L1b_irr=xarray.open_dataset(r"C:\Users\pdv\PycharmProjects\hypernets_processor\hypernets_processor\out\HYPERNETS_L_OUTD_L1B_IRR_v0.1.nc")
            self.context.logger.debug("Processing to L1c...")
            L1c = intp.interpolate_l1c(L1b_rad,L1b_irr)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L2a...")
            L2a = surf.process_l2(L1c)
            self.context.logger.debug("Done")
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
    processor_config_path= os.path.join(this_directory_path,"etc/processor_2.config")
    job_config_path= os.path.join(this_directory_path,"etc/job.config")
    processor_config = read_config_file(processor_config_path)
    job_config = read_config_file(job_config_path)
    hp = HypernetsProcessor(job_config=job_config,processor_config=processor_config)
    hp.context.set_config_value("processor_directory",this_directory_path)
    hp.run()
    pass
