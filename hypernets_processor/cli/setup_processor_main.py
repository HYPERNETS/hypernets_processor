"""
Main function to setup processor on install
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.hypernets_db_builder import HypernetsDBBuilder
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "24/9/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(working_directory=None, mdb_path=None, set_mdb=False, adb_path=None, set_adb=False, archive_directory=None):
    """
    Main function to run routine to setup hypernets_processor

    :type processor_config_path: str
    :param processor_config_path: processor configuration file path
    """

    # Create directories
    os.makedirs(working_directory, exist_ok=True)
    os.makedirs(archive_directory, exist_ok=True)

    # Create databases
    hdb = HypernetsDBBuilder()

    if mdb_path is None:
        mdb_path = os.path.join(working_directory, "metadata.db")

    if set_mdb:
        metadata_db_url = "sqlite:///" + mdb_path

        if not os.path.exists(mdb_path):
            metadata_db = hdb.create_db_template(metadata_db_url, "metadata_db")

    if adb_path is None:
        adb_path = os.path.join(working_directory, "anomoly.db")

    if set_adb:
        anomoly_db_url = "sqlite:///" + adb_path

        if not os.path.exists(mdb_path):
            anomoly_db = hdb.create_db_template(anomoly_db_url, "anomoly_db")

    return None


if __name__ == "__main__":
    pass
