import unittest

from UM.Application import Application
from UM.Job import Job
from UM.JobQueue import JobQueue

import time
import threading

class TestJob(Job):
    def __init__(self):
        super().__init__()

    def run(self):
        self.setResult("TestJob")

class LongTestJob(Job):
    def __init__(self):
        super().__init__()

    def run(self):
        time.sleep(1.5)
        self.setResult("LongTestJob")

class JobQueueApplication(Application):
    def __init__(self):
        super().__init__("test", "1.0")

    def functionEvent(self, event):
        pass

class TestJobQueue(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self._app = JobQueueApplication.getInstance()

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_Create(self):
        JobQueue._instance = None
        jq = JobQueue()

        self.assertGreater(len(jq._threads), 0)
        self.assertEqual(jq, JobQueue.getInstance())

        JobQueue._instance = None

        jq = JobQueue(4)
        self.assertEqual(len(jq._threads), 4)

    def test_Add(self):
        jq = JobQueue.getInstance()

        job = TestJob()
        job.start()

        self.assertIn(job, jq._jobs)

        time.sleep(0.1)

        self.assertEqual(job.isFinished(), True)
        self.assertEqual(job.getResult(), "TestJob")

        job1 = TestJob()
        job2 = TestJob()

        job1.start()
        job2.start()

        time.sleep(0.1)

        self.assertEqual(job1.isFinished(), True)
        self.assertEqual(job1.getResult(), "TestJob")
        self.assertEqual(job2.isFinished(), True)
        self.assertEqual(job2.getResult(), "TestJob")

        job = LongTestJob()
        job.start()

        time.sleep(1)

        self.assertEqual(job.isFinished(), False)
        self.assertEqual(job.getResult(), None)

        time.sleep(1)

        self.assertEqual(job.isFinished(), True)
        self.assertEqual(job.getResult(), "LongTestJob")

        jobs = []
        for i in range(10):
            job = TestJob()
            job.start()
            jobs.append(job)

        time.sleep(0.5)
        for job in jobs:
            self.assertEqual(job.isFinished(), True)
            self.assertEqual(job.getResult(), "TestJob")

    def test_Remove(self):
        pass

if __name__ == "__main__":
    unittest.main()
