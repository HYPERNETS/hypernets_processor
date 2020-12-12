"""
Contains main class for processing sequence data
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import Interpolate
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.data_io.hypernets_writer import HypernetsWriter
from hypernets_processor.utils.paths import parse_sequence_path

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

        self.context.logger.info("Processing sequence: " + sequence_path)

        # update context
        self.context.set_config_value("time", parse_sequence_path(sequence_path)["datetime"])
        self.context.set_config_value("site_abbr", "TEST")
        self.context.set_config_value("sequence_path", sequence_path)
        self.context.set_config_value("sequence_name", os.path.basename(sequence_path))
        writer = HypernetsWriter(self.context)

        # Read L0
        self.context.logger.debug("Reading raw data...")
        reader = HypernetsReader(self.context)
        l0_irr, l0_rad, l0_bla = reader.read_sequence(sequence_path)
        self.context.logger.debug("Done")

        # Calibrate to L1a
        self.context.logger.debug("Processing to L1a...")
        cal = Calibrate(self.context, MCsteps=100)
        L1a_rad = cal.calibrate_l1a("radiance", l0_rad, l0_bla)
        L1a_irr = cal.calibrate_l1a("irradiance", l0_irr, l0_bla)
        self.context.logger.debug("Done")

        intp = Interpolate(self.context, MCsteps=1000)
        surf = SurfaceReflectance(self.context, MCsteps=1000)

        if self.context.get_config_value("network") == "w":
            rhymer = RhymerHypstar(self.context)

            self.context.logger.debug("Processing to L1b...")
            L1b = rhymer.process_l1b(L1a_rad, L1a_irr)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L1c...")
            L1c = rhymer.process_l1c(L1b)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L1d...")
            L1d = surf.process_l1d(L1c)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L2a...")
            L2a = surf.process(L1d)
            self.context.logger.debug("Done")

        elif self.context.get_config_value("network") == "l":

            self.context.logger.debug("Processing to L1b radiance...")
            L1b_rad = cal.average_l1b("radiance", L1a_rad)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L1b irradiance...")
            L1b_irr = cal.average_l1b("irradiance", L1a_irr)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L1c...")
            L1c = intp.interpolate_l1c(L1b_rad, L1b_irr)
            self.context.logger.debug("Done")

            self.context.logger.debug("Processing to L2a...")
            L2a = surf.process(L1c)
            self.context.logger.debug("Done")

        else:
            raise NameError("Invalid network: " + self.context.get_config_value("network"))

        self.context.logger.info("All Done")

        return None


if __name__ == "__main__":
    pass
