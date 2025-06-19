"""
Contains main class for processing sequence data
"""
import glob
import xarray as xr

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import (
    SurfaceReflectance,
)
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.combine_SWIR.combine_SWIR import CombineSWIR
from hypernets_processor.data_utils.average import Average
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.utils.paths import parse_sequence_path
from hypernets_processor.calibration.calibration_converter import CalibrationConverter
from obsarray.templater.dataset_util import DatasetUtil as du
from hypernets_processor.data_utils.quality_checks import QualityChecks
from hypernets_processor.data_utils.site_specific_quality_checks import SiteSpecificQualityChecks

import warnings
import os
from datetime import datetime, timezone

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "21/10/2020"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"


class SequenceProcessor:
    """
    Class for processing sequence data

    :type context: processor context
    :param context: hypernets_processor.context.Context
    """

    def __init__(self, context=None):
        """
        Constructor method
        """
        self.context = context

    def process_sequence(self, sequence_path):
        """
        Processes sequence file
        """

        # update context
        self.context.set_config_value(
            "time", parse_sequence_path(sequence_path)["datetime"]
        )
        self.context.set_config_value("sequence_path", sequence_path)
        self.context.set_config_value("sequence_name", os.path.basename(sequence_path))

        reader = HypernetsReader(self.context)
        calcon = CalibrationConverter(self.context)
        cal = Calibrate(self.context)
        surf = SurfaceReflectance(self.context)
        qc = QualityChecks(self.context)
        ssqc = SiteSpecificQualityChecks(self.context)
        avg = Average(
            self.context,
        )
        rhymer = RhymerHypstar(self.context)
        writer = HypernetsWriter(self.context)

        # initialise all data products to None
        L0a_irr = None
        L0a_rad = None
        L0a_bla = None
        L0a_swir_irr = None
        L0a_swir_rad = None
        L0a_swir_bla = None

        L1a_rad, L0a_rad_masked, L0a_rad_bla_masked = None, None, None
        L1a_irr, L0a_irr_masked, L0a_irr_bla_masked = None, None, None

        L1a_swir_rad, L0a_swir_rad_masked, L0a_swir_rad_bla_masked = (
            None,
            None,
            None,
        )

        L1a_swir_irr, L0a_swir_irr_masked, L0a_swir_irr_bla_masked = (
            None,
            None,
            None,
        )

        L1b_rad = None
        L1b_irr = None

        L1c = None
        L2a = None

        # when reprocessing from specific level, read in and set that data
        if self.context.get_config_value("reprocess_from"):
            directory=writer.return_directory()
            if self.context.get_config_value("reprocess_from").upper() == "L2A":
                L2a = self.find_preexisting_file(directory, "L2A")
                L1b_rad = self.find_preexisting_file(directory, "L1B_RAD")
                L1b_irr = self.find_preexisting_file(directory, "L1B_IRR")
            elif self.context.get_config_value("reprocess_from").upper()=="L1B":
                L1b_rad = self.find_preexisting_file(directory,"L1B_RAD")
                L1b_irr = self.find_preexisting_file(directory,"L1B_IRR")
            else:
                raise ValueError("It is only possible to reprocess from L2A or L1B files. Please change the `reprocess_from' config value")


        with warnings.catch_warnings():
            if not self.context.get_config_value("verbose"):
                warnings.simplefilter("ignore")

            tstart = datetime.now(timezone.utc)
            self.context.set_config_value("start_time_processing_sequence", tstart)
            if self.context.get_config_value("network") == "w":
                calibration_data_rad, calibration_data_irr = calcon.read_calib_files(
                    sequence_path
                )
                # Read L0
                if not self.context.get_config_value("reprocess_from"):
                    self.context.logger.info("Reading raw data...")
                    L0a_irr, L0a_rad, L0a_bla = reader.read_sequence(
                        sequence_path, calibration_data_rad, calibration_data_irr
                    )
                    self.context.logger.info("Done")

                # Calibrate to L1a
                if self.context.get_config_value("max_level").upper() in [
                    "L1A",
                    "L1B",
                    "L1C",
                    "L2A",
                    "L2B",
                ]:
                    if L0a_rad:
                        self.context.logger.info("Processing to L1a radiance...")
                        L1a_rad, L0a_rad_masked, L0a_rad_bla_masked = cal.calibrate_l1a(
                            "radiance", L0a_rad, L0a_bla, calibration_data_rad
                        )
                        self.context.logger.info("Done")

                    if L0a_irr:
                        self.context.logger.info("Processing to L1a irradiance...")
                        L1a_irr, L0a_irr_masked, L0a_irr_bla_masked = cal.calibrate_l1a(
                            "irradiance", L0a_irr, L0a_bla, calibration_data_irr
                        )

                        self.context.logger.info("Done")

                if L0a_rad_masked and L0a_irr_masked:
                    if self.context.get_config_value("max_level").upper() in [
                        "L1B",
                        "L1C",
                        "L2A",
                        "L2B",
                    ]:
                        self.context.logger.info("Processing to L1b radiance...")
                        L1b_rad = cal.calibrate_l1b(
                            "radiance",
                            L0a_rad_masked,
                            L0a_rad_bla_masked,
                            calibration_data_rad,
                        )
                        # print(L1b_rad)

                        self.context.logger.info("Done")

                        self.context.logger.info("Processing to L1b irradiance...")
                        L1b_irr = cal.calibrate_l1b(
                            "irradiance",
                            L0a_irr_masked,
                            L0a_irr_bla_masked,
                            calibration_data_irr,
                        )


                azis = rhymer.checkazimuths(L1a_rad)

                if L1b_rad and L1b_irr and len(azis)>0:
                    if self.context.get_config_value("max_level").upper() in ["L1C", "L2A", "L2B"]:
                        self.context.logger.info("Processing to L1c...")
                        # check if different azimuth angles within single sequence
                        for a in azis:
                            print("Processing for azimuth:{}".format(a))
                            rad_, irr_, ra = rhymer.selectazimuths(L1a_rad, L1a_irr, a)
                            print("Processing for relative azimuth: {}".format(ra))

                            # if self.context.get_config_value("protocol") == "water_std_use_all_irr":

                            #     L1a_uprad, L1a_downrad, L1a_irr, dataset_l1b = rhymer.cycleparse(rad_, irr,
                            #                                                                          dataset_l1b)
                            # if self.context.get_config_value("protocol") == "water_std":
                            #     L1a_uprad, L1a_downrad, L1a_irr, dataset_l1b = rhymer.cycleparse(rad_, irr_,
                            #                                                                          dataset_l1b)

                            L1c_int = rhymer.process_l1c_int(rad_, L1b_irr)

                            # add relative azimuth angle for the filename
                            L1c = surf.reflectance_w(L1c_int, L1b_irr, razangle=ra)
                            self.context.logger.info("Done")

                            if self.context.get_config_value("max_level").upper() in ["L2A","L2B"]:
                                self.context.logger.info("Processing to L2a...")
                                # add relative azimuth angle for the filename
                                L2a = surf.process_l2(L1c, razangle=ra)
                                self.context.logger.info(
                                    "Done for azimuth {}".format(ra)
                                )
                        self.context.logger.info("Done")

                else:
                    self.context.logger.info("Not a standard sequence")
                    self.context.anomaly_handler.add_anomaly("ms")

            elif self.context.get_config_value("network") == "l":
                comb = CombineSWIR(self.context)
                intp = Interpolate(self.context)

                # Read L0
                if not self.context.get_config_value("reprocess_from"):
                    self.context.logger.info("Reading raw data...")
                    (
                        calibration_data_rad,
                        calibration_data_irr,
                        calibration_data_swir_rad,
                        calibration_data_swir_irr,
                    ) = calcon.read_calib_files(sequence_path)

                    (
                        L0a_irr,
                        L0a_rad,
                        L0a_bla,
                        L0a_swir_irr,
                        L0a_swir_rad,
                        L0a_swir_bla,
                    ) = reader.read_sequence(
                        sequence_path,
                        calibration_data_rad,
                        calibration_data_irr,
                        calibration_data_swir_rad,
                        calibration_data_swir_irr,
                    )
                    self.context.logger.info("Done")

                if self.context.get_config_value("max_level").upper() in [
                    "L1A",
                    "L1B",
                    "L1C",
                    "L2A",
                    "L2B",
                ]:
                    if L0a_rad and L0a_bla:
                        self.context.logger.info("Processing to L1a radiance...")
                        L1a_rad, L0a_rad_masked, L0a_rad_bla_masked = cal.calibrate_l1a(
                            "radiance", L0a_rad, L0a_bla, calibration_data_rad
                        )
                        self.context.logger.info("Done")

                    if L0a_irr and L0a_bla:
                        self.context.logger.info("Processing to L1a irradiance...")
                        L1a_irr, L0a_irr_masked, L0a_irr_bla_masked = cal.calibrate_l1a(
                            "irradiance", L0a_irr, L0a_bla, calibration_data_irr
                        )
                        self.context.logger.info("Done")

                    if L0a_swir_rad and L0a_swir_bla:
                        self.context.logger.info("Processing to L1a SWIR radiance...")
                        (
                            L1a_swir_rad,
                            L0a_swir_rad_masked,
                            L0a_swir_rad_bla_masked,
                        ) = cal.calibrate_l1a(
                            "radiance",
                            L0a_swir_rad,
                            L0a_swir_bla,
                            calibration_data_swir_rad,
                            swir=True,
                        )
                        self.context.logger.info("Done")


                    if L0a_swir_irr and L0a_swir_bla:
                        self.context.logger.info("Processing to L1a SWIR irradiance...")
                        (
                            L1a_swir_irr,
                            L0a_swir_irr_masked,
                            L0a_swir_irr_bla_masked,
                        ) = cal.calibrate_l1a(
                            "irradiance",
                            L0a_swir_irr,
                            L0a_swir_bla,
                            calibration_data_swir_irr,
                            swir=True,
                        )

                        self.context.logger.info("Done")

                if self.context.get_config_value("max_level").upper() in ["L1B", "L1C", "L2A", "L2B"]:
                    if L0a_rad_masked and L0a_swir_rad_masked:
                        self.context.logger.info("Processing to L1b radiance...")
                        L1b_rad = comb.combine(
                            "radiance",
                            L0a_rad_masked,
                            L0a_rad_bla_masked,
                            L0a_swir_rad_masked,
                            L0a_swir_rad_bla_masked,
                            calibration_data_rad,
                            calibration_data_swir_rad,
                        )
                        self.context.logger.info("Done")

                    if L0a_irr_masked and L0a_swir_irr_masked:
                        self.context.logger.info("Processing to L1b irradiance...")
                        L1b_irr = comb.combine(
                            "irradiance",
                            L0a_irr_masked,
                            L0a_irr_bla_masked,
                            L0a_swir_irr_masked,
                            L0a_swir_irr_bla_masked,
                            calibration_data_irr,
                            calibration_data_swir_irr,
                        )
                        self.context.logger.info("Done")

                if L1b_rad and L1b_irr and (not self.context.get_config_value("reprocess_from") or not self.context.get_config_value("reprocess_from").upper() == "L2A"):
                    if self.context.get_config_value("max_level") in ["L1C", "L2A", "L2B"]:
                        self.context.logger.info("Processing to L1c...")
                        L1c = intp.interpolate_l1c(L1b_rad, L1b_irr)
                        self.context.logger.info("Done")
                    if self.context.get_config_value("max_level") in ["L2A", "L2B"]:
                        self.context.logger.info("Processing to L2a...")
                        L2a = surf.process_l2(L1c)
                        self.context.logger.info("Done")
                elif not self.context.get_config_value("reprocess_from"):
                    self.context.logger.info("Not a standard sequence")
                    self.context.anomaly_handler.add_anomaly("ms")

                if L2a:
                    if self.context.get_config_value("max_level").upper() in ["L2B",]:
                        self.context.logger.info("Processing to L2B...")
                        L2b = ssqc.apply_site_specific_QC(L2a, L1b_rad, L1b_irr)
                        self.context.logger.info("Done")
            else:
                raise NameError(
                    "Invalid network: " + self.context.get_config_value("network")
                )
        tend = datetime.now(timezone.utc)
        print(
            "time for computation of one seq (min, sec):{}".format(
                divmod((tend - tstart).total_seconds(), 60)
            )
        )
        return None

    def find_preexisting_file(self, directory, level):
        """
        function to find preexisting product from previous run

        :param directory: product directory
        :param level: level of product (including both level and type e.g. L1B_IRR)
        :return: product xarray object
        """

        files = glob.glob(os.path.join(directory, "*%s*.nc"%level))
        if len(files) > 1:
            self.context.logger.info("multiple %s files found, using the most recent one"%level)

        elif len(files) == 0:
            self.context.logger.info("no %s file found for this sequence"%level)
            self.context.anomaly_handler.add_anomaly("npr")
            return None

        file = files[-1]
        self.context.logger.info("starting from file: %s" % (file))
        return xr.open_dataset(file)

if __name__ == "__main__":
    pass
