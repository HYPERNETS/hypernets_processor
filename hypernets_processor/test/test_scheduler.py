"""
Tests for Scheduler class
"""

from hypernets_processor.version import __version__
import unittest
import sys
import os
import logging
from contextlib import contextmanager
from io import StringIO
import multiprocessing
import time
from hypernets_processor.scheduler import Scheduler


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "29/3/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def test_job(a, b):
    return a + b


def bad_job():
    return 1/0


def return_test_logger(fname=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if fname is None:
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    else:
        file_formatter = logging.Formatter('%(message)s')
        file_handler = logging.FileHandler(fname)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class TestScheduler(unittest.TestCase):
    def test_job_wrapper_no_parallel_no_logger(self):

        s = Scheduler()

        a = 2
        b = 4
        c = s.job_wrapper(test_job, parallel=False, logger=None, a=a, b=b)
        self.assertEqual(c, a+b)

    def test_job_wrapper_parallel_no_logger(self):

        s = Scheduler()

        a = 2
        b = 4
        c = s.job_wrapper(test_job, parallel=True, logger=None, a=a, b=b)
        self.assertEqual(a+b, c)

    def test_job_wrapper_parallel_logger(self):

        s = Scheduler()

        a = 2
        b = 4

        with captured_output() as (out, err):
            c = s.job_wrapper(test_job, parallel=True, logger=return_test_logger(), name="Test Job", a=a, b=b)

        # This can go inside or outside the `with` block
        output = out.getvalue().strip()
        self.assertEqual(output, 'Started: Test Job\nCompleted: Test Job')

        self.assertEqual(a+b, c)

    def test_job_wrapper_parallel_logger_bad_job(self):

        s = Scheduler()

        with captured_output() as (out, err):
            c = s.job_wrapper(bad_job, parallel=True, logger=return_test_logger(), name="Test Job")

        # This can go inside or outside the `with` block
        output = out.getvalue().strip()
        self.assertEqual(output, 'Started: Test Job\nFailed: Test Job - ZeroDivisionError: division by zero')

    def test_schedule_seconds(self):

        s = Scheduler(logger=return_test_logger())

        scheduler_job_config = {"seconds": 2,
                                "parallel": False,
                                "name": "test name"}

        s.schedule(test_job, 2, 4, scheduler_job_config=scheduler_job_config)
        jobs = s.get_scheduled_jobs()

        self.assertEqual(1, len(jobs))

        job = jobs[0]
        self.assertEqual(job.interval, 2)
        self.assertEqual(job.unit, "seconds")
        self.assertEqual(job.job_func.__name__, "job_wrapper")
        self.assertEqual(job.job_func.args[0].__name__, "test_job")
        self.assertEqual(job.job_func.args[1], False)
        self.assertEqual(type(job.job_func.args[2]), logging.Logger)
        self.assertEqual(job.job_func.args[3], "test name")
        self.assertEqual(job.job_func.args[4], 2)
        self.assertEqual(job.job_func.args[5], 4)

    def test_schedule_minutes(self):

        s = Scheduler(logger=return_test_logger())

        scheduler_job_config = {"minutes": 2,
                                "parallel": False,
                                "name": "test name"}

        s.schedule(test_job, 2, 4, scheduler_job_config=scheduler_job_config)
        jobs = s.get_scheduled_jobs()

        self.assertEqual(1, len(jobs))

        job = jobs[0]
        self.assertEqual(job.interval, 2)
        self.assertEqual(job.unit, "minutes")
        self.assertEqual(job.job_func.__name__, "job_wrapper")
        self.assertEqual(job.job_func.args[0].__name__, "test_job")
        self.assertEqual(job.job_func.args[1], False)
        self.assertEqual(type(job.job_func.args[2]), logging.Logger)
        self.assertEqual(job.job_func.args[3], "test name")
        self.assertEqual(job.job_func.args[4], 2)
        self.assertEqual(job.job_func.args[5], 4)

    def test_schedule_hours(self):

        s = Scheduler(logger=return_test_logger())

        scheduler_job_config = {"hours": 2,
                                "parallel": False,
                                "name": "test name"}

        s.schedule(test_job, 2, 4, scheduler_job_config=scheduler_job_config)
        jobs = s.get_scheduled_jobs()

        self.assertEqual(1, len(jobs))

        job = jobs[0]
        self.assertEqual(job.interval, 2)
        self.assertEqual(job.unit, "hours")
        self.assertEqual(job.job_func.__name__, "job_wrapper")
        self.assertEqual(job.job_func.args[0].__name__, "test_job")
        self.assertEqual(job.job_func.args[1], False)
        self.assertEqual(type(job.job_func.args[2]), logging.Logger)
        self.assertEqual(job.job_func.args[3], "test name")
        self.assertEqual(job.job_func.args[4], 2)
        self.assertEqual(job.job_func.args[5], 4)

    def test_run(self):

        log_fname = "test.txt"

        logger = return_test_logger(log_fname)

        s = Scheduler(logger=logger)

        scheduler_job_config = {"seconds": 2,
                                "parallel": False,
                                "name": "test name"}

        s.schedule(test_job, 2, 4, scheduler_job_config=scheduler_job_config)

        p = multiprocessing.Process(target=s.run)

        p.start()
        time.sleep(5)
        p.terminate()

        # Cleanup
        p.join()

        with open(log_fname) as f:
            log = f.read()

        self.assertEqual(log, 'Started: test name\nCompleted: test name\nStarted: test name\nCompleted: test name\n')

        os.remove(log_fname)


if __name__ == '__main__':
    unittest.main()
