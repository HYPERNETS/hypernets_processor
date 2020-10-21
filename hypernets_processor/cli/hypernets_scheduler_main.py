"""
Main function for hypernets_scheduler_cli to run
"""

from hypernets_processor.version import __version__
from hypernets_processor.utils.config import read_config_file, read_jobs_list
from hypernets_processor.utils.logging import configure_logging
from hypernets_processor.utils.config import get_config_value
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
    * jobs_list (str) - Path of jobs list file, to run on schedule

    """

    scheduler_config_dict = dict()

    sections = [sch for sch in scheduler_config.sections()]
    sections.remove("Log")

    for sch in sections:

        scheduler_config_dict[sch] = {}

        # Schedule Configuration
        scheduler_config_dict[sch]["seconds"] = get_config_value(scheduler_config, sch, "seconds", dtype=int)
        scheduler_config_dict[sch]["minutes"] = get_config_value(scheduler_config, sch, "minutes", dtype=int)
        scheduler_config_dict[sch]["hours"] = get_config_value(scheduler_config, sch, "hours", dtype=int)
        scheduler_config_dict[sch]["start_time"] = get_config_value(scheduler_config, sch, "start_time", dtype=str)
        scheduler_config_dict[sch]["parallel"] = get_config_value(scheduler_config, sch, "seconds", dtype=bool)
        scheduler_config_dict[sch]["jobs_list"] = get_config_value(scheduler_config, sch, "jobs_list", dtype=str)

        # todo - sort out start time format

        # Checks
        # Check only have hours, minutes or seconds
        intervals = [scheduler_config_dict[sch]["seconds"], scheduler_config_dict[sch]["minutes"],
                     scheduler_config_dict[sch]["hours"]]
        if intervals.count(None) != 2:
            raise ValueError("job repeat interval must be defined as 1 of seconds, minutes or hours for " + sch)

    return scheduler_config_dict


def main(scheduler_config_path):
    """
    Main function to schedule automated hypernets_processor jobs

    :type scheduler_config_path: str
    :param scheduler_config_path: path of scheduler config file
    """

    scheduler_config = read_config_file(scheduler_config_path)

    logger = configure_logging(config=scheduler_config)

    scheduler_config = unpack_scheduler_config(scheduler_config)

    jobs_list = read_jobs_list(scheduler_config["Processor Schedule"]["jobs_list"])

    # schedule jobs
    processor_sch = Scheduler(logger=logger)

    for job_config_path in jobs_list:

        # define scheduler job config
        scheduler_job_config = dict()

        # read job config file to set job name
        job_config = read_config_file(job_config_path)
        if ("Job" in job_config.keys()) and ("name" in job_config["name"].keys()):
            scheduler_job_config["name"] = job_config["Job"]["name"]
        else:
            scheduler_job_config["name"] = job_config_path

        del job_config

        scheduler_job_config["seconds"] = scheduler_config["Processor Schedule"]["seconds"]
        scheduler_job_config["minutes"] = scheduler_config["Processor Schedule"]["minutes"]
        scheduler_job_config["hours"] = scheduler_config["Processor Schedule"]["hours"]
        scheduler_job_config["parallel"] = scheduler_config["Processor Schedule"]["parallel"]

        # schedule job
        processor_sch.schedule(processor_main,
                               scheduler_job_config=scheduler_job_config,
                               job_config_path=job_config_path)

    # run scheduled jobs
    processor_sch.run(start_time=scheduler_config["Processor Schedule"]["start_time"])

    return None


if __name__ == "__main__":
    pass
