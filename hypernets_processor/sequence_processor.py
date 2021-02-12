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

import os

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

        # update context
        self.context.set_config_value("time", parse_sequence_path(sequence_path)["datetime"])
        self.context.set_config_value("sequence_path", sequence_path)
        self.context.set_config_value("sequence_name", os.path.basename(sequence_path))

        reader = HypernetsReader(self.context)
        calcon = CalibrationConverter(self.context)
        cal = Calibrate(self.context, MCsteps=100)
        surf = SurfaceReflectance(self.context, MCsteps=1000)
        avg = Average(self.context,)
        rhymer=RhymerHypstar(self.context)
        writer=HypernetsWriter(self.context)


        if self.context.get_config_value("network") == "w":

            calibration_data_rad,calibration_data_irr = calcon.read_calib_files()
            # Read L0
            self.context.logger.info("Reading raw data...")
            l0_irr,l0_rad,l0_bla = reader.read_sequence(sequence_path,calibration_data_rad,calibration_data_irr)
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
            comb = CombineSWIR(self.context,MCsteps=100)
            intp = Interpolate(self.context,MCsteps=1000)

            # Read L0
            self.context.logger.info("Reading raw data...")
            (calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,
             calibration_data_swir_irr) = calcon.read_calib_files()
            l0_irr,l0_rad,l0_bla,l0_swir_irr,l0_swir_rad,l0_swir_bla = reader.read_sequence(sequence_path,calibration_data_rad,calibration_data_irr,calibration_data_swir_rad,calibration_data_swir_irr)
            self.context.logger.info("Done")

            # Calibrate to L1a
            self.context.logger.info("Processing to L1a...")
            L1a_rad = cal.calibrate_l1a("radiance",l0_rad,l0_bla,calibration_data_rad)
            L1a_irr = cal.calibrate_l1a("irradiance",l0_irr,l0_bla,calibration_data_irr)

            L1a_swir_rad = cal.calibrate_l1a("radiance",l0_swir_rad,l0_swir_bla,
                                             calibration_data_swir_rad,swir=True)
            L1a_swir_irr = cal.calibrate_l1a("irradiance",l0_swir_irr,l0_swir_bla,
                                             calibration_data_swir_irr,swir=True)
            self.context.logger.info("Done")

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
            raise NameError("Invalid network: " + self.context.get_config_value("network"))

        return None


if __name__ == "__main__":
    pass
