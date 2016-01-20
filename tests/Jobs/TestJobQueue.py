# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

from UM.Application import Application
from UM.Job import Job
from UM.JobQueue import JobQueue

import time
import threading

class ShortTestJob(Job):
    def run(self):
        self.setResult("TestJob")

class LongTestJob(Job):
    def run(self):
        time.sleep(1.5)
        self.setResult("LongTestJob")

@pytest.fixture
def job_queue():
    JobQueue._instance = None
    return JobQueue()

class TestJobQueue():
    def test_create(self):
        JobQueue._instance = None
        jq = JobQueue()

        assert len(jq._threads) > 0
        assert jq == JobQueue.getInstance()

        JobQueue._instance = None

        jq = JobQueue(4)
        assert len(jq._threads) == 4

    def test_addShort(self, job_queue):
        job = ShortTestJob()
        job.start()

        assert job in job_queue._jobs

        time.sleep(0.1)

        assert job.isFinished()
        assert job.getResult() == "TestJob"

    def test_addLong(self, job_queue):
        job = LongTestJob()
        job.start()

        assert job in job_queue._jobs

        time.sleep(1)

        assert not job.isFinished()
        assert job.getResult() == None

        time.sleep(1)

        assert job.isFinished()
        assert job.getResult() == "LongTestJob"


    test_addMultiple_data = [2, 5, 10]
    @pytest.mark.parametrize("count", test_addMultiple_data)
    def test_addMultiple(self, job_queue, count):
        jobs = []
        for i in range(count):
            job = ShortTestJob()
            job.start()

            jobs.append(job)

            assert job in job_queue._jobs

        time.sleep(0.01 * count)

        for job in jobs:
            assert job.isFinished()
            assert job.getResult() == "TestJob"

    def test_remove(self):
        pass

if __name__ == "__main__":
    unittest.main()
