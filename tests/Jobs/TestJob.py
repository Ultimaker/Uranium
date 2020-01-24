import pytest
from unittest.mock import patch, MagicMock

from UM.Job import Job




def test_getSetError():
    job = Job()
    exception = Exception("Some Error :(")
    job.setError(exception)

    assert job.getError() == exception
    assert job.hasError()


def test_getSetResult():
    job = Job()
    job.setResult("blarg")
    assert job.getResult() == "blarg"


def test_run():
    job = Job()
    with pytest.raises(NotImplementedError):
        job.run()


def test_start():
    job = Job()
    job_queue = MagicMock()
    with patch("UM.JobQueue.JobQueue.getInstance", MagicMock(return_value = job_queue)):
        job.start()
    job_queue.add.called_once_with(job)


def test_cancel():
    job = Job()
    job_queue = MagicMock()
    with patch("UM.JobQueue.JobQueue.getInstance", MagicMock(return_value=job_queue)):
        job.cancel()
    job_queue.remove.called_once_with(job)


def test_isRunning():
    job = Job()
    assert not job.isRunning()