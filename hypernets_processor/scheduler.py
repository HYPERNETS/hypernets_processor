"""
Contains class for scheduling and automating hypernets data processing jobs
"""

from hypernets_processor.version import __version__
import time
from multiprocessing.pool import ThreadPool
import functools
from schedule import Scheduler as Sched

'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "29/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class Scheduler:
    """
    Class to schedule recurring jobs (i.e. like cron)

    :param logger: logger (optional)
    :type logger: logging.logger
    """

    def __init__(self, logger=None):
        """
        Initialises class
        """
        self.scheduler = Sched()
        self.logger = logger

    def schedule(self, job, *args, **kwargs):
        """
        Schedule job

        :type job: func
        :param job: job function

        :type scheduler_job_config: dict
        :param scheduler_job_config: configuration parameters for job, entries may be:

        * seconds (*int*) - seconds between job repeats
        * minutes (*int*) - minutes between job repeats
        * parallel (*bool*) - switch for running jobs on different threads (False if omitted)
        * name (*str*) - job name for logging (optional)

        :param args: args for job

        :param kwargs: kwargs for job
        """

        scheduler_job_config = kwargs.pop("scheduler_job_config")

        seconds = scheduler_job_config["seconds"] if "seconds" in scheduler_job_config.keys() else None
        minutes = scheduler_job_config["minutes"] if "minutes" in scheduler_job_config.keys() else None
        hours = scheduler_job_config["hours"] if "hours" in scheduler_job_config.keys() else None
        parallel = scheduler_job_config["parallel"] if "parallel" in scheduler_job_config.keys() else None
        name = scheduler_job_config["name"] if "name" in scheduler_job_config.keys() else None

        if seconds is not None:
            self.scheduler.every(seconds).seconds.do(self.job_wrapper, job, parallel,
                                                     self.logger, name, *args, **kwargs)
        elif minutes is not None:
            self.scheduler.every(minutes).minutes.do(self.job_wrapper, job, parallel,
                                                     self.logger, name, *args, **kwargs)

        elif hours is not None:
            self.scheduler.every(hours).hours.do(self.job_wrapper, job, parallel,
                                                 self.logger, name, *args, **kwargs)

    def get_scheduled_jobs(self):
        """
        Return scheduled jobs

        :return: scheduled jobs
        :rtype: list
        """

        return self.scheduler.jobs

    @staticmethod
    def job_wrapper(job, parallel=False, logger=None, name=None, *args, **kwargs):
        """
        Wraps job function to provide logging, error handling and parallel processing when scheduled

        :type job: func
        :param job: function
        """

        if logger is not None:
            def with_logging(func, logger, name):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    logger.info("Started: " + name)

                    try:
                        print("here7")
                        msg = func(*args, **kwargs)

                        log_msg = "Completed: " + name
                        if type(msg) == str:
                            log_msg += " (" + msg + ")"

                        logger.info(log_msg)

                        return msg

                    except Exception as exception:

                        exception_type = type(exception).__name__
                        exception_value = exception.__str__()

                        logger.info("Failed: " + name + " - " + exception_type + ": " + exception_value)

                return wrapper

            job = with_logging(job, logger, name)

        if parallel:
            pool = ThreadPool(processes=1)
            async_result = pool.apply_async(job, args, kwargs)
            return async_result.get()
        else:
            return job(*args, **kwargs)

    def run(self, start_time=None):
        """
        Run scheduled jobs

        :type start_time: datetime.datetime
        :param start_time: time to delay starting running pending jobs too
        """

        # todo - implement start_time feature

        while True:
            print("here5")

            self.scheduler.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    pass
