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
        seq_dir = server_dir + seq_id+"/"

        wavs_vis=np.genfromtxt("../examples/outdoor_test/wavs_vis.dat")
        wavs_swir=np.genfromtxt("../examples/outdoor_test/wavs_swir.dat")
        spec_vis=np.genfromtxt("../examples/outdoor_test/spec_vis.dat")
        spec_swir=np.genfromtxt("../examples/outdoor_test/spec_swir.dat")
        times_vis=np.genfromtxt("../examples/outdoor_test/spec_vis.dat",dtype="U20")
        times_swir=np.genfromtxt("../examples/outdoor_test/spec_swir.dat",dtype="U20")
        ID_vis=spec_vis[:,1]
        ID_swir=spec_swir[:,1]

        hdsb = HypernetsDSBuilder(context=self.context)
        scanDim = 320
        dim_sizes_dict = {"wavelength":len(wavs_vis),"scan":scanDim}

        # use template from variables and metadata in format
        l0_rad = hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,
                                         ds_format="L0_RAD")
        l0_rad["wavelength"] = wavs_vis
        l0_rad["scan"] = np.linspace(1,scanDim,scanDim)
        l0_rad["digital_number"].values = spec_vis[np.where(ID_vis == 1),5::][0].T
        l0_rad["acquisition_time"].values = spec_vis[np.where(ID_vis == 1),2][0]
        l0_rad["integration_time"].values = spec_vis[np.where(ID_vis == 1),3][0]
        l0_rad["series_id"].values = np.concatenate((np.ones(int(scanDim/2)),2*np.ones(int(scanDim/2))))

        for i in range(scanDim):
            acquisitionTime = times_vis[np.where(ID_vis == 1),2][0][i]
            acquisitionTime = datetime.strptime("20200821T"+acquisitionTime+"UTC",
                                                '%Y%m%dT%H:%M:%S.%f%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            l0_rad["acquisition_time"][i] = datetime.timestamp(acquisitionTime)

        scanDim = 40
        dim_sizes_dict = {"wavelength":len(wavs_vis),"scan":scanDim}
        l0_irr = hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,
                                         ds_format="L0_IRR")
        l0_irr["wavelength"] = wavs_vis
        l0_irr["scan"] = np.linspace(1,scanDim,scanDim)
        l0_irr["digital_number"].values = spec_vis[np.where(ID_vis == 2),5::][0].T
        l0_irr["acquisition_time"].values = spec_vis[np.where(ID_vis == 2),2][0]
        l0_irr["integration_time"].values = spec_vis[np.where(ID_vis == 2),3][0]
        l0_irr["series_id"].values = np.concatenate((np.ones(int(scanDim/2)),2*np.ones(int(scanDim/2))))

        for i in range(scanDim):
            acquisitionTime = times_vis[np.where(ID_vis == 2),2][0][i]
            acquisitionTime = datetime.strptime("20200821T"+acquisitionTime+"UTC",
                                                '%Y%m%dT%H:%M:%S.%f%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            l0_irr["acquisition_time"][i] = datetime.timestamp(acquisitionTime)

        scanDim = 360
        dim_sizes_dict = {"wavelength":len(wavs_vis),"scan":scanDim}
        l0_bla = hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,
                                         ds_format="L0_BLA")
        l0_bla["wavelength"] = wavs_vis
        l0_bla["scan"] = np.linspace(1,scanDim,scanDim)
        l0_bla["digital_number"].values = spec_vis[np.where(ID_vis == 0),5::][0].T
        l0_bla["acquisition_time"].values = spec_vis[np.where(ID_vis == 0),2][0]
        l0_bla["integration_time"].values = spec_vis[np.where(ID_vis == 0),3][0]
        l0_bla["series_id"].values = np.concatenate((np.ones(int(scanDim/2)),2*np.ones(int(scanDim/2))))

        for i in range(scanDim):
            acquisitionTime = times_vis[np.where(ID_vis == 0),2][0][i]
            acquisitionTime = datetime.strptime("20200821T"+acquisitionTime+"UTC",
                                                '%Y%m%dT%H:%M:%S.%f%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            l0_bla["acquisition_time"][i] = datetime.timestamp(acquisitionTime)

        scanDim = 10
        dim_sizes_dict = {"wavelength":len(wavs_swir),"scan":scanDim}

        # use template from variables and metadata in format
        l0_swir_rad = hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,ds_format="L0_RAD")
        l0_swir_rad["wavelength"] = wavs_swir
        l0_swir_rad["scan"] = np.linspace(1,scanDim,scanDim)
        l0_swir_rad["digital_number"].values = spec_swir[np.where(ID_swir == 1),5::][0].T
        l0_swir_rad["acquisition_time"].values = spec_swir[np.where(ID_swir == 1),2][0]
        l0_swir_rad["integration_time"].values = spec_swir[np.where(ID_swir == 1),3][0]
        l0_swir_rad["series_id"].values = np.concatenate((np.ones(int(scanDim/2)),2*np.ones(int(scanDim/2))))

        for i in range(scanDim):
            acquisitionTime = times_swir[np.where(ID_swir == 1),2][0][i]
            acquisitionTime = datetime.strptime("20200821T"+acquisitionTime+"UTC",
                                                '%Y%m%dT%H:%M:%S.%f%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            l0_swir_rad["acquisition_time"][i] = datetime.timestamp(acquisitionTime)

        scanDim = 10
        dim_sizes_dict = {"wavelength":len(wavs_swir),"scan":scanDim}
        l0_swir_irr = hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,ds_format="L0_IRR")
        l0_swir_irr["wavelength"] = wavs_swir
        l0_swir_irr["scan"] = np.linspace(1,scanDim,scanDim)
        l0_swir_irr["digital_number"].values = spec_swir[np.where(ID_swir == 2),5::][0].T
        l0_swir_irr["acquisition_time"].values = spec_swir[np.where(ID_swir == 2),2][0]
        l0_swir_irr["integration_time"].values = spec_swir[np.where(ID_swir == 2),3][0]
        l0_swir_irr["series_id"].values = np.concatenate((np.ones(int(scanDim/2)),2*np.ones(int(scanDim/2))))

        for i in range(scanDim):
            acquisitionTime = times_swir[np.where(ID_swir == 2),2][0][i]
            acquisitionTime = datetime.strptime("20200821T"+acquisitionTime+"UTC",
                                                '%Y%m%dT%H:%M:%S.%f%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            l0_swir_irr["acquisition_time"][i] = datetime.timestamp(acquisitionTime)
        scanDim = 20
        dim_sizes_dict = {"wavelength":len(wavs_swir),"scan":scanDim}
        l0_swir_bla = hdsb.create_ds_template(dim_sizes_dict=dim_sizes_dict,ds_format="L0_BLA")
        l0_swir_bla["wavelength"] = wavs_swir
        l0_swir_bla["scan"] = np.linspace(1,scanDim,scanDim)
        l0_swir_bla["digital_number"].values = spec_swir[np.where(ID_swir == 0),5::][0].T
        l0_swir_bla["acquisition_time"].values = spec_swir[np.where(ID_swir == 0),2][0]
        l0_swir_bla["integration_time"].values = spec_swir[np.where(ID_swir == 0),3][0]
        l0_swir_bla["series_id"].values = np.concatenate((np.ones(int(scanDim/2)),2*np.ones(int(scanDim/2))))

        for i in range(scanDim):
            acquisitionTime = times_swir[np.where(ID_swir == 0),2][0][i]
            acquisitionTime = datetime.strptime("20200821T"+acquisitionTime+"UTC",
                                                '%Y%m%dT%H:%M:%S.%f%Z')
            acquisitionTime = acquisitionTime.replace(tzinfo=timezone.utc)
            l0_swir_bla["acquisition_time"][i] = datetime.timestamp(acquisitionTime)


        reader = HypernetsReader(self.context)
        calcon = CalibrationConverter(self.context)
        cal = Calibrate(self.context,MCsteps=100)
        surf = SurfaceReflectance(self.context,MCsteps=1000)

        if self.context.get_config_value("network") == "l":
            comb = CombineSWIR(self.context,MCsteps=100)
            intp = Interpolate(self.context,MCsteps=1000)

            # Read L0
            # self.context.logger.debug("Reading raw data...")
            # l0_irr,l0_rad,l0_bla,l0_swir_irr,l0_swir_rad,l0_swir_bla = reader.read_sequence(
            #     sequence_path)
            # self.context.logger.debug("Done")

            l0_rad["digital_number"].values[:,0]=l0_rad["digital_number"].values[:,0]/1.25
            l0_irr["digital_number"].values[:,0]=l0_irr["digital_number"].values[:,0]/1.25

            #Calibrate to L1a

            (calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,
             calibration_data_swir_irr) = calcon.read_calib_files()

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
