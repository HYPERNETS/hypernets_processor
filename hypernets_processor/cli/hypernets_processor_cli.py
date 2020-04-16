"""
hypernets_processor cli
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.common import configure_std_parser, read_processor_config_file, read_job_config_file
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
    # Configuration files
    parser.add_argument("-s", "--processor-config", action="store",
                        help="Path of processor configuration file")

    parser.add_argument("-j", "--job-config", action="store",
                        help="Path of job configuration file")

    return parser


parser = configure_parser()
parsed_args = parser.parse_args()


def cli():
    """
    Command line interface function for hypernets_processor
    """

    # unpack parsed_args
    processor_config = read_processor_config_file(parsed_args.p)
    job_config = read_job_config_file(parsed_args.j)

    # run main
    main(processor_config=processor_config,
         job_config=job_config)

    return None


if __name__ == "__main__":
    pass
