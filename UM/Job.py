# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time
from typing import Any, Optional

from UM.Decorators import deprecated
from UM.JobQueue import JobQueue
from UM.Signal import Signal, signalemitter


@signalemitter
class Job:
    """Base class for things that should be performed in a thread.

    The Job class provides a basic interface for a 'job', that is a
    self-contained task that should be performed in a thread. It makes
    use of the JobQueue for the actual threading.
    :sa JobQueue
    """

    def __init__(self) -> None:
        super().__init__()
        self._running = False   # type: bool
        self._finished = False  # type: bool
        self._result = None     # type: Any
        self._message = None    # type: Any
        self._error = None      # type: Optional[Exception]

    def run(self) -> None:
        """Perform the actual task of this job. Should be reimplemented by subclasses.

        :exception NotImplementedError
        """

        raise NotImplementedError()

    # Get optional message
    @deprecated("Get message for job is no longer used", "4.5")
    def getMessage(self):
        return self._message

    # Set optional message
    @deprecated("Set message for job is no longer used", "4.5")
    def setMessage(self, message) -> None:
        self._message = message

    def getResult(self) -> Any:
        """Get the result of the job.

        The actual result object returned by this method is dependant on the implementation.
        """

        return self._result

    def setResult(self, result: Any) -> None:
        """Set the result of this job.

        This should be called by run() to set the actual result of the Job.
        """

        self._result = result

    def setError(self, error: Exception) -> None:
        """Set an exception that was thrown while the job was being executed.

        Setting error to something else than None implies the Job failed
        to execute properly.

        :param error: The exception to set.
        """

        self._error = error

    def start(self) -> None:
        """Start the job.

        This will put the Job into the JobQueue to be processed whenever a thread is available.

        :sa JobQueue::add()
        """

        JobQueue.getInstance().add(self)

    def cancel(self) -> None:
        """Cancel the job.

        This will remove the Job from the JobQueue. If the run() function has already been called,
        this will do nothing.
        """

        JobQueue.getInstance().remove(self)

    def isRunning(self) -> bool:
        """Check whether the job is currently running.

        :return:
        """

        return self._running

    def isFinished(self) -> bool:
        """Check whether the job has finished processing."""

        return self._finished

    def hasError(self) -> bool:
        """Check whether the Job has encountered an error during execution.

        :return: True if an error was set, False if not.
        """

        return self._error is not None

    def getError(self) -> Optional[Exception]:
        """Get the error that was encountered during execution.

        :return: The error encountered during execution or None if there was no error.
        """

        return self._error

    finished = Signal()
    """Emitted when the job has finished processing.

    :param job: :type{Job} The finished job.
    """

    progress = Signal()
    """Emitted when the job processing has progressed.

    :param job: :type{Job} The job reporting progress.
    :param amount: :type{int} The amount of progress made, from 0 to 100.
    """

    @staticmethod
    def yieldThread() -> None:
        """Utility function that allows us to yield thread processing.

        This is mostly a workaround for broken python threads. This function
        forces a GIL release and allows a different thread to start processing
        if it is waiting.
        """

        time.sleep(0)  # Sleeping for 0 introduces no delay but does allow context switching.
