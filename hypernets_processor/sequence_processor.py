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
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.utils.paths import parse_sequence_path
from hypernets_processor.calibration.calibration_converter import CalibrationConverter
from hypernets_processor.data_io.dataset_util import DatasetUtil as du

import os
import pandas as pd
import numpy as np
'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "21/10/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
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
        import sys
        print(sys.executable)

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

            calibration_data_rad,calibration_data_irr = calcon.read_calib_files(sequence_path)
            # Read L0
            self.context.logger.info("Reading raw data...")
            l0_irr,l0_rad,l0_bla = reader.read_sequence(sequence_path,calibration_data_rad,calibration_data_irr)
            self.context.logger.info("Done")

            # Calibrate to L1a
            if self.context.get_config_value("max_level") in ["L1A","L1B","L1C","L2A"]:
                self.context.logger.info("Processing to L1a...")
                if l0_rad:
                    print(calibration_data_rad)
                    L1a_rad = cal.calibrate_l1a("radiance",l0_rad,l0_bla,calibration_data_rad)
                if l0_irr:
                    L1a_irr = cal.calibrate_l1a("irradiance",l0_irr,l0_bla,calibration_data_irr)
                self.context.logger.info("Done")

            if l0_rad and l0_irr:
                if self.context.get_config_value("max_level") in ["L1B","L1C","L2A"]:
                    self.context.logger.info("Processing to L1b radiance...")
                    L1b_rad = avg.average_l1b("radiance", L1a_rad)
                    if self.context.get_config_value("write_l1b"):
                        writer.write(L1b_rad, overwrite=True, remove_vars_strings=self.context.get_config_value("remove_vars_strings"))
                    self.context.logger.info("Done")

                    self.context.logger.info("Processing to L1b irradiance...")
                    L1b_irr = avg.average_l1b("irradiance", L1a_irr)
                    if self.context.get_config_value("write_l1b"):
                        writer.write(L1b_irr, overwrite=True, remove_vars_strings=self.context.get_config_value("remove_vars_strings"))
                    self.context.logger.info("Done")
                    print(rhymer.qc_illumination(L1a_irr))
                    if rhymer.qc_illumination(L1a_irr)> 0.1:
                        self.context.logger.info("Non constant illumination for sequence {}".format(L1a_irr.attrs['sequence_id']))
                        self.context.anomaly_handler.add_anomaly("nu")

            # pd.set_option('display.max_columns', None)  # or 1000
            # pd.set_option('display.max_rows', None)  # or 1000
            # pd.set_option('display.max_colwidth', -1)  # or 199
            #print(pd.DataFrame(du.unpack_flags(L1a_irr['quality_flag']).to_dataframe()))

            if L1b_rad and L1b_irr:
                if self.context.get_config_value("max_level") in ["L1C","L2A"]:
                    self.context.logger.info("Processing to L1c...")
                    L1c_int = rhymer.process_l1c_int(L1a_rad, L1a_irr)
#                    if rhymer.qc_bird(L1c_int) < 0.1:
#                        L1c_int["quality_flag"] = \
#                            du.set_flag(L1c_int["quality_flag"],"ld_ed_clearsky_failing")
                    L1c = surf.process_l1c(L1c_int, L1b_irr)
                    print(pd.DataFrame(du.unpack_flags(L1c['quality_flag']).to_dataframe()))
                    self.context.logger.info("Done")

                if self.context.get_config_value("max_level")=="L2A":
                    self.context.logger.info("Processing to L2a...")
                    L2a = surf.process_l2(L1c)
                    self.context.logger.info("Done")
            else:
                self.context.logger.info("Not a standard sequence")
                self.context.anomaly_handler.add_anomaly("s")

        elif self.context.get_config_value("network") == "l":
            comb = CombineSWIR(self.context)
            intp = Interpolate(self.context)

            # Read L0
            self.context.logger.info("Reading raw data...")
            (calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,
             calibration_data_swir_irr) = calcon.read_calib_files(sequence_path)
            l0_irr,l0_rad,l0_bla,l0_swir_irr,l0_swir_rad,l0_swir_bla = reader.read_sequence(sequence_path,calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,calibration_data_swir_irr)
            self.context.logger.info("Done")

            if self.context.get_config_value("max_level") in ["L1A","L1B","L1C","L2A"]:
                self.context.logger.info("Processing to L1a...")
                if l0_rad:
                    L1a_rad = cal.calibrate_l1a("radiance",l0_rad,l0_bla,
                                                calibration_data_rad)
                if l0_irr:
                    L1a_irr = cal.calibrate_l1a("irradiance",l0_irr,l0_bla,
                                                calibration_data_irr)
                if l0_swir_rad:
                    L1a_swir_rad = cal.calibrate_l1a("radiance",l0_swir_rad,l0_swir_bla,
                                                     calibration_data_swir_rad,swir=True)
                if l0_swir_irr:
                    L1a_swir_irr = cal.calibrate_l1a("irradiance",l0_swir_irr,
                                                     l0_swir_bla,
                                                     calibration_data_swir_irr,swir=True)
                self.context.logger.info("Done")

            if self.context.get_config_value("max_level") in ["L1B","L1C","L2A"]:
                if l0_rad and l0_swir_rad:
                    self.context.logger.info("Processing to L1b radiance...")
                    L1b_rad = comb.combine("radiance",L1a_rad,L1a_swir_rad)
                    self.context.logger.info("Done")

                if l0_irr and l0_swir_irr:
                    self.context.logger.info("Processing to L1b irradiance...")
                    L1b_irr = comb.combine("irradiance",L1a_irr,L1a_swir_irr)
                    self.context.logger.info("Done")

            if l0_rad and l0_irr:
                if self.context.get_config_value("max_level") in ["L1C","L2A"]:
                    self.context.logger.info("Processing to L1c...")
                    L1c = intp.interpolate_l1c(L1b_rad,L1b_irr)
                    self.context.logger.info("Done")
                if self.context.get_config_value("max_level") == "L2A":
                    self.context.logger.info("Processing to L2a...")
                    L2a = surf.process_l2(L1c)
                    self.context.logger.info("Done")
            else:
                self.context.logger.info("Not a standard sequence")
                self.context.anomaly_handler.add_anomaly("s")

        else:
            raise NameError("Invalid network: " + self.context.get_config_value("network"))

        return None


if __name__ == "__main__":
    pass
