"""
hypernets_processor cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.common import configure_logging, configure_std_parser, read_config
from hypernets_processor.cli.hypernets_processor_main import main


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def configure_parser():
    """
    Configure parser

    :return: parser
    :rtype: argparse.ArgumentParser
    """

    description = "Tool for processing Hypernets Land and Water Network hyperspectral field data"

    # Create standard parser
    parser = configure_std_parser(description=description)

    # Add specific arguments
    parser.add_argument("-c", "--config", action="store",
                        help="Path of configuration file")

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface function for hypernets_processor
    """

    logger = configure_logging()
    main(logger=logger)

    return None


if __name__ == "__main__":
    pass
