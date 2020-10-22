"""
Main function for job init
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import read_config_file, JOB_CONFIG_TEMPLATE_PATH, JOBS_FILE_PATH
import os


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "20/10/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(settings):
    """
    Main function for job init

    :type settings: dict
    :param settings: user defined configuration values
    """

    # Create config from template
    job_config = read_config_file(JOB_CONFIG_TEMPLATE_PATH)

    job_config["Job"]["job_name"] = settings["job_name"]

    # Create directories (resets with existing if unchanged)
    os.makedirs(settings["job_working_directory"], exist_ok=True)
    job_config["Job"]["job_working_directory"] = settings["job_working_directory"]
    os.makedirs(settings["raw_data_directory"], exist_ok=True)
    job_config["Input"]["raw_data_directory"] = settings["raw_data_directory"]

    # Write config
    job_config_path = os.path.join(settings["job_working_directory"], settings["job_name"]+".config")
    with open(job_config_path, 'w') as f:
        job_config.write(f)

    # Set job log file
    log_path = os.path.join(settings["job_working_directory"], settings["job_name"] + ".log")
    if not os.path.exists(log_path):
        open(log_path, 'a').close()
    job_config["Log"]["log_path"] = log_path

    # Add to scheduler
    if settings["add_to_scheduler"]:
        with open(JOBS_FILE_PATH, "a") as f:
            if os.path.getsize(JOBS_FILE_PATH) > 0:
                f.write("\n" + job_config_path)
            else:
                f.write(job_config_path)


if __name__ == "__main__":
    pass
