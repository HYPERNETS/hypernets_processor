"""
Contains main class for processing sequence data
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.combine_SWIR.combine_SWIR import CombineSWIR
from hypernets_processor.data_utils.average import Average
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.data_io.data_templates import DataTemplates
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.utils.paths import parse_sequence_path
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.utils.logging import configure_logging
from hypernets_processor.utils.config import read_config_file
from hypernets_processor.context import Context
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.calibration.calibration_converter import CalibrationConverter

import os
from datetime import datetime
import time

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
        self.context.set_config_value("site_abbr","GONA")
        self.templ = DataTemplates(self.context)

    def run(self):
        """
        Processes sequence file
        """
        sequence_path="SEQ20200312T103000"
        # update context
        self.context.set_config_value("time", parse_sequence_path(sequence_path)["datetime"])
        self.context.set_config_value("sequence_path", sequence_path)
        self.context.set_config_value("sequence_name", os.path.basename(sequence_path))

        reader = HypernetsReader(self.context)
        calcon = CalibrationConverter(self.context)
        cal = Calibrate(self.context)
        surf = SurfaceReflectance(self.context)
        avg = Average(self.context,)
        rhymer=RhymerHypstar(self.context)
        writer=HypernetsWriter(self.context)


        if self.context.get_config_value("network") == "w":

            calibration_data_rad,calibration_data_irr = calcon.read_calib_files()
            # Read L0
            self.context.logger.info("Reading raw data...")
            arr = np.load(
                r"C:\Users\pdv\PycharmProjects\hypernets_processor\examples\test_radiance_and_irradiance_libradtran.npy",
                allow_pickle=True)
            N_WAVELENGTHS = len(arr[1])
            n_series = 6
            print(N_WAVELENGTHS,n_series)
            dsb = HypernetsDSBuilder(self.context)

            l0_rad = dsb.create_ds_template(
                {"wavelength":N_WAVELENGTHS,"scan":n_series*10},"L0_RAD")
            l0_irr = dsb.create_ds_template(
                {"wavelength":N_WAVELENGTHS,"scan":n_series*10},"L0_IRR")
            l0_bla = dsb.create_ds_template(
                {"wavelength":N_WAVELENGTHS,"scan":n_series*10},"L0_BLA")

            l0_rad = l0_rad.assign_coords(wavelength=arr[1])
            l0_irr = l0_irr.assign_coords(wavelength=arr[1])
            l0_bla = l0_bla.assign_coords(wavelength=arr[1])

            l0_rad["digital_number"].values = arr[7]/1000
            l0_rad["acquisition_time"].values = np.arange(30)
            l0_rad["series_id"].values = np.repeat([1,2,3],10)
            l0_rad["integration_time"].values = np.repeat(1024,30)
            l0_irr["digital_number"].values = arr[8]/1000
            l0_irr["acquisition_time"].values = np.arange(30)
            l0_irr["series_id"].values = np.repeat([1,2,3],10)
            l0_irr["integration_time"].values = np.repeat(1024,30)
            l0_bla["digital_number"].values = np.zeros(
                l0_bla["digital_number"].values.shape)
            l0_bla["acquisition_time"].values = np.arange(30)
            l0_bla["series_id"].values = np.repeat([1,2,3],10)
            l0_bla["integration_time"].values = np.repeat(1024,30)


            self.context.logger.info("Done")

            # Calibrate to L1a
            self.context.logger.info("Processing to L1a...")
            if l0_rad:
                L1a_rad = cal.calibrate_l1a("radiance",l0_rad,l0_bla,calibration_data_rad)
            if l0_irr:
                L1a_irr = cal.calibrate_l1a("irradiance",l0_irr,l0_bla,calibration_data_irr)
            self.context.logger.info("Done")

            if l0_rad and l0_irr:
                self.context.logger.info("Processing to L1b radiance...")
                L1b_rad = avg.average_l1b("radiance", L1a_rad)
                print(L1b_rad)
                if self.context.get_config_value("write_l1b"):
                    writer.write(L1b_rad, overwrite=True)
                self.context.logger.info("Done")

                self.context.logger.info("Processing to L1b irradiance...")
                L1b_irr = avg.average_l1b("irradiance", L1a_irr)
                if self.context.get_config_value("write_l1b"):
                    writer.write(L1b_irr, overwrite=True)
                self.context.logger.info("Done")

                self.context.logger.info("Processing to L1c...")
                L1c_int = rhymer.process_l1c_int(L1a_rad, L1a_irr)
                L1c = surf.process_l1c(L1c_int)
                self.context.logger.info("Done")

                self.context.logger.info("Processing to L2a...")
                L2a = surf.process_l2(L1c)
                self.context.logger.info("Done")
            else:
                self.context.logger.info("Not a standard sequence")

        elif self.context.get_config_value("network") == "l":
            comb = CombineSWIR(self.context)
            intp = Interpolate(self.context)

            # Read L0
            self.context.logger.info("Reading raw data...")
            (calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,
             calibration_data_swir_irr) = calcon.read_calib_files()
            arr = np.load(
                r"C:\Users\pdv\PycharmProjects\hypernets_processor\examples\test_radiance_and_irradiance_libradtran_vnir_FWHM.npy",
                allow_pickle=True)

            N_WAVELENGTHS = len(arr[0])
            n_series = 6
            seriesIDs = np.repeat([1,2,3,4,5,6],10)

            l0_rad = self.templ.l0_template_dataset(arr[0],len(seriesIDs),"L0_RAD")
            l0_irr = self.templ.l0_template_dataset(arr[0],len(seriesIDs),"L0_IRR")
            l0_bla = self.templ.l0_template_dataset(arr[0],len(seriesIDs),"L0_BLA")

            l0_rad["digital_number"].values = arr[1]/1000
            l0_rad["solar_zenith_angle"].values = 43.540279*np.ones(len(seriesIDs))+np.arange(0,0.1,len(seriesIDs))
            l0_rad["solar_azimuth_angle"].values = 68.016677 *np.ones(len(seriesIDs))-np.arange(0,0.1,len(seriesIDs))
            l0_rad["viewing_zenith_angle"].values = np.repeat([5,5,0,0,10,10],10)
            l0_rad["viewing_azimuth_angle"].values = np.repeat([270,280,270,280,270,280],10)

            l0_rad["acquisition_time"].values = np.arange(len(seriesIDs))
            l0_rad["series_id"].values = seriesIDs
            l0_rad["integration_time"].values = np.repeat(1024,len(seriesIDs))
            l0_irr["digital_number"].values = arr[2]/1000
            l0_irr["acquisition_time"].values = np.arange(len(seriesIDs))
            l0_irr["series_id"].values = seriesIDs
            l0_irr["integration_time"].values = np.repeat(1024,len(seriesIDs))
            l0_bla["digital_number"].values = np.zeros_like(arr[2])
            l0_bla["acquisition_time"].values = np.arange(len(seriesIDs))
            l0_bla["series_id"].values = seriesIDs
            l0_bla["integration_time"].values = np.repeat(1024,len(seriesIDs))

            arrSWIR = np.load(
                r"C:\Users\pdv\PycharmProjects\hypernets_processor\examples\test_radiance_and_irradiance_libradtran_swir_FWHM.npy",
                allow_pickle=True)
            N_WAVELENGTHS = len(arrSWIR[0])
            n_series = 6
            print(N_WAVELENGTHS,n_series)
            seriesIDs = np.repeat([1,2,3,4,5,6],10)

            l0_swir_rad = self.templ.l0_template_dataset(arrSWIR[0],len(seriesIDs),"L0_RAD")
            l0_swir_irr = self.templ.l0_template_dataset(arrSWIR[0],len(seriesIDs),"L0_IRR")
            l0_swir_bla = self.templ.l0_template_dataset(arrSWIR[0],len(seriesIDs),"L0_BLA")

            l0_swir_rad["digital_number"].values = arrSWIR[1]/1000
            l0_swir_rad["acquisition_time"].values = np.arange(len(seriesIDs))
            l0_swir_rad["series_id"].values = seriesIDs
            l0_swir_rad["integration_time"].values = np.repeat(1024,len(seriesIDs))
            l0_swir_irr["digital_number"].values = arrSWIR[2]/1000
            l0_swir_irr["acquisition_time"].values = np.arange(len(seriesIDs))
            l0_swir_irr["series_id"].values = seriesIDs
            l0_swir_irr["integration_time"].values = np.repeat(1024,len(seriesIDs))
            l0_swir_bla["digital_number"].values = np.zeros_like(arrSWIR[1])
            l0_swir_bla["acquisition_time"].values = np.arange(len(seriesIDs))
            l0_swir_bla["series_id"].values = seriesIDs
            l0_swir_bla["integration_time"].values = np.repeat(1024,len(seriesIDs))

            self.context.logger.info("Done")

            self.context.logger.info("Processing to L1a...")
            if l0_rad:
                L1a_rad = cal.calibrate_l1a("radiance",l0_rad,l0_bla,calibration_data_rad)
            if l0_irr:
                L1a_irr = cal.calibrate_l1a("irradiance",l0_irr,l0_bla,calibration_data_irr)
            if l0_swir_rad:
                L1a_swir_rad = cal.calibrate_l1a("radiance",l0_swir_rad,l0_swir_bla,
                                             calibration_data_swir_rad,swir=True)
            if l0_swir_irr:
                L1a_swir_irr = cal.calibrate_l1a("irradiance",l0_swir_irr,l0_swir_bla,
                                             calibration_data_swir_irr,swir=True)
            self.context.logger.info("Done")

            if l0_rad and l0_irr:
                self.context.logger.info("Processing to L1b radiance...")
                L1b_rad = comb.combine("radiance", L1a_rad, L1a_swir_rad)
                self.context.logger.info("Done")

                self.context.logger.info("Processing to L1b irradiance...")
                L1b_irr = comb.combine("irradiance", L1a_irr, L1a_swir_irr)
                self.context.logger.info("Done")

                self.context.logger.info("Processing to L1c...")
                L1c = intp.interpolate_l1c(L1b_rad, L1b_irr)
                self.context.logger.info("Done")

                self.context.logger.info("Processing to L2a...")
                L2a = surf.process_l2(L1c)
                self.context.logger.info("Done")
            else:
                self.context.logger.info("Not a standard sequence")

        else:
            raise NameError("Invalid network: " + self.context.get_config_value("network"))

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
