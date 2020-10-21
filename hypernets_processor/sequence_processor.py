"""
Contains main class for processing sequence data
"""

from hypernets_processor.version import __version__
from hypernets_processor.calibration.calibrate import Calibrate
from hypernets_processor.surface_reflectance.surface_reflectance import SurfaceReflectance
from hypernets_processor.interpolation.interpolate import InterpolateL1c
from hypernets_processor.rhymer.rhymer.hypstar.rhymer_hypstar import RhymerHypstar
from hypernets_processor.data_io.hypernets_reader import HypernetsReader
from hypernets_processor.utils.paths import parse_sequence_path
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

        self.context.logger.info("Processing sequence: " + sequence_path)

        # update context
        self.context.set_config_value("time", parse_sequence_path(sequence_path)["datetime"])

        # Read L0
        self.context.logger.debug("Reading raw data...")
        reader = HypernetsReader(self.context)
        l0_irr, l0_rad, l0_bla = reader.read_sequence(sequence_path)
        self.context.logger.debug("Done")

        # Calibrate to L1a
        self.context.logger.debug("Calibrating L1a...")
        calibrate = Calibrate(self.context, MCsteps=100)
        L1a_rad = calibrate.calibrate_l1a("radiance", l0_rad, l0_bla)
        L1a_irr = calibrate.calibrate_l1a("irradiance", l0_irr, l0_bla)
        self.context.logger.debug("Done")

        if self.context.get_config_value("network") == "w":
            pass

        elif self.context.get_config_value("network") == "l":
            pass

        else:
            raise NameError("Invalid network: " + self.context.get_config_value("network"))

        return None


if __name__ == "__main__":
    pass
