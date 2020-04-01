"""
Main function for hypernets_scheduler_cli to run
"""

from hypernets_processor.version import __version__
from hypernets_processor.cli.common import configure_logging, read_job_config_file
from hypernets_processor import Scheduler
from hypernets_processor.cli.hypernets_processor_cli import main as processor_main


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "26/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


def main(jobs_list, processor_config, scheduler_config):
    """
    Main function to schedule automated hypernets_processor jobs

    :type jobs_list: list
    :param jobs_list: job config fnames

    :type processor_config: dict
    :param processor_config: processor configuration information, with entries:

    * ...

    :type scheduler_config: dict
    :param scheduler_config: scheduler configuration information, with entries:

    * seconds (int) - Scheduled job repeat interval in seconds, default None (if not None minutes and hours are None)
    * minutes (int) - Scheduled job repeat interval in minutes, default None (if not None seconds and hours are None)
    * hours (int) - Scheduled job repeat interval in hour, default None (if not None seconds and minutes are None)
    * start_time (datetime.datetime) - Scheduled time to start running tasks, default None (means start now)
    * parallel (bool) - Switch to run scheduled jobs on different threads, default False
    * log_path (str) - Path to write log to, default None (means log goes to stdout)
    * verbose (bool) - Switch for verbose output, default False
    * quiet (bool) - Switch for quiet output, default False

    """

    # Configure logging
    logger = configure_logging(fname=scheduler_config["log_path"],
                               verbose=scheduler_config["verbose"],
                               quiet=scheduler_config["quiet"])

    # schedule jobs
    s = Scheduler()

    for job_config_fname in jobs_list:

        # read job config file
        job_config = read_job_config_file(job_config_fname)

        # define scheduler job config
        scheduler_job_config = dict()
        scheduler_job_config["name"] = job_config["name"]
        scheduler_job_config["seconds"] = scheduler_config["seconds"]
        scheduler_job_config["minutes"] = scheduler_config["minutes"]
        scheduler_job_config["hours"] = scheduler_config["hours"]
        scheduler_job_config["parallel"] = scheduler_config["parallel"]
        scheduler_job_config["logger"] = logger

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
