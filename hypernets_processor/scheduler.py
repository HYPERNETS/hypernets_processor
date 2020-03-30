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
    """

    def __init__(self):
        """
        Initialises class
        """
        self.scheduler = Sched()

    def schedule(self, job, *args, **kwargs):
        """
        Schedule job

        :type job: func
        :param job: job function

        :type job_config: dict
        :param job_config: configuration parameters for job, entries may be:

        * seconds (*int*) - seconds between job repeats
        * minutes (*int*) - minutes between job repeats
        * parallel (*bool*) - switch for running jobs on different threads (False if omitted)
        * logger (*logging.Logger*) - logger (optional)
        * name (*str*) - job name for logging (optional)

        :param args: args for job

        :param kwargs: kwargs for job
        """

        job_config = kwargs.pop("job_config")

        seconds = job_config["seconds"] if "seconds" in job_config.keys() else None
        minutes = job_config["minutes"] if "minutes" in job_config.keys() else None
        parallel = job_config["parallel"] if "parallel" in job_config.keys() else None
        logger = job_config["logger"] if "logger" in job_config.keys() else None
        name = job_config["name"] if "name" in job_config.keys() else None

        if seconds is not None:
            self.scheduler.every(seconds).seconds.do(self.job_wrapper, job, parallel, logger, name, *args, **kwargs)
        elif minutes is not None:
            self.scheduler.every(minutes).minutes.do(self.job_wrapper, job, parallel, logger, name, *args, **kwargs)

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
                        result = func(*args, **kwargs)
                        logger.info("Completed: " + name)
                        return result
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

    def run(self):
        """
        Run scheduled jobs
        """

        while True:
            self.scheduler.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    pass
