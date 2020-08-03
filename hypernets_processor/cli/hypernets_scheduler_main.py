"""
Main function for hypernets_scheduler_cli to run
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.common import configure_logging, read_config_file
from hypernets_processor import Scheduler
from hypernets_processor.cli.hypernets_processor_main import main as processor_main


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def unpack_scheduler_config(scheduler_config):
    """
    Returns information from scheduler configuration file

    :type fname: str
    :param fname: path of configuration file

    :rtype: dict
    :return: scheduler configuration information, with entries (defaults occur if entry omitted from config file):

    * seconds (int) - Scheduled job repeat interval in seconds, default None (if not None minutes and hours are None)
    * minutes (int) - Scheduled job repeat interval in minutes, default None (if not None seconds and hours are None)
    * hours (int) - Scheduled job repeat interval in hour, default None (if not None seconds and minutes are None)
    * start_time (datetime.datetime) - Scheduled time to start running tasks, default None (means start now)
    * parallel (bool) - Switch to run scheduled jobs on different threads, default False

    """

    scheduler_config_dict = dict()

    # Schedule Configuration
    scheduler_config_dict["seconds"] = scheduler_config["Schedule"]["seconds"] if "seconds" in \
                                           scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["minutes"] = scheduler_config["Schedule"]["minutes"] if "minutes" in \
                                           scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["hours"] = scheduler_config["Schedule"]["hours"] if "hours" in \
                                         scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["start_time"] = scheduler_config["Schedule"]["start_time"] if "start_time" in \
                                             scheduler_config["Schedule"].keys() else None
    scheduler_config_dict["parallel"] = scheduler_config["Schedule"]["parallel"] if "parallel" in \
                                            scheduler_config["Schedule"].keys() else False

    # Sort out types
    if scheduler_config_dict["seconds"] is not None:
        scheduler_config_dict["seconds"] = int(scheduler_config_dict["seconds"])
    if scheduler_config_dict["minutes"] is not None:
        scheduler_config_dict["minutes"] = int(scheduler_config_dict["minutes"])
    if scheduler_config_dict["hours"] is not None:
        scheduler_config_dict["hours"] = int(scheduler_config_dict["hours"])

    if scheduler_config_dict["parallel"] == "False":
        scheduler_config_dict["parallel"] = False

    if scheduler_config_dict["parallel"] == "True":
        scheduler_config_dict["parallel"] = True

    # todo - sort out start time format

    # Checks
    # Check only have hours, minutes or seconds
    intervals = [scheduler_config_dict["seconds"], scheduler_config_dict["minutes"], scheduler_config_dict["hours"]]
    if intervals.count(None) != 2:
        raise ValueError("Scheduled job repeat interval must be defined as 1 of seconds, minutes or hours")

    return scheduler_config_dict


def main(jobs_list, processor_config, scheduler_config):
    """
    Main function to schedule automated hypernets_processor jobs

    :type jobs_list: list
    :param jobs_list: job config fnames

    :type processor_config: configparser.RawConfigParser
    :param processor_config: processor configuration information

    :type scheduler_config: configparser.RawConfigParser
    :param scheduler_config: scheduler configuration information

    """

    # Configure logging
    logger = configure_logging(config=scheduler_config)
    scheduler_config = unpack_scheduler_config(scheduler_config)

    # schedule jobs
    s = Scheduler(logger=logger)

    for job_config_fname in jobs_list:

        # read job config file
        job_config = read_config_file(job_config_fname)

        # define scheduler job config
        scheduler_job_config = dict()

        if ("Job" in job_config.keys()) and ("name" in job_config["name"].keys()):
            scheduler_job_config["name"] = job_config["Job"]["name"]
        else:
            scheduler_job_config["name"] = job_config_fname

        scheduler_job_config["seconds"] = scheduler_config["seconds"]
        scheduler_job_config["minutes"] = scheduler_config["minutes"]
        scheduler_job_config["hours"] = scheduler_config["hours"]
        scheduler_job_config["parallel"] = scheduler_config["parallel"]

        # schedule job
        s.schedule(processor_main,
                   scheduler_job_config=scheduler_job_config,
                   job_config=job_config,
                   processor_config=processor_config)

    # run scheduled jobs
    s.run(start_time=scheduler_config["start_time"])

    return None


if __name__ == "__main__":
    pass
