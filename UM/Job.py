# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time

from UM.Signal import Signal, signalemitter

from UM.JobQueue import JobQueue


##  Base class for things that should be performed in a thread.
#
#   The Job class provides a basic interface for a 'job', that is a
#   self-contained task that should be performed in a thread. It makes
#   use of the JobQueue for the actual threading.
#   \sa JobQueue
@signalemitter
class Job:
    def __init__(self):
        super().__init__()
        self._running = False   # type: bool
        self._finished = False  # type: bool
        self._result = None     # type: any
        self._error = None

    ##  Perform the actual task of this job. Should be reimplemented by subclasses.
    #   \exception NotImplementedError
    def run(self):
        raise NotImplementedError()

    ##  Get the result of the job.
    #
    #   The actual result object returned by this method is dependant on the implementation.
    def getResult(self):
        return self._result

    ##  Set the result of this job.
    #
    #   This should be called by run() to set the actual result of the Job.
    def setResult(self, result: any):
        self._result = result

    ##  Set an exception that was thrown while the job was being executed.
    #
    #   Setting error to something else than None implies the Job failed
    #   to execute properly.
    #
    #   \param error \type{Exception} The exception to set.
    def setError(self, error: Exception):
        self._error = error

    ##  Start the job.
    #
    #   This will put the Job into the JobQueue to be processed whenever a thread is available.
    #
    #   \sa JobQueue::add()
    def start(self):
        JobQueue.getInstance().add(self)

    ##  Cancel the job.
    #
    #   This will remove the Job from the JobQueue. If the run() function has already been called,
    #   this will do nothing.
    def cancel(self):
        JobQueue.getInstance().remove(self)

    ##  Check whether the job is currently running.
    #
    #   \return \type{bool}
    def isRunning(self) -> bool:
        return self._running

    ##  Check whether the job has finished processing.
    #
    #   \return \type{bool}
    def isFinished(self) -> bool:
        return self._finished

    ##  Check whether the Job has encountered an error during execution.
    #
    #   \return \type{bool} True if an error was set, False if not.
    def hasError(self) -> bool:
        return self._error is not None

    ##  Get the error that was encountered during execution.
    #
    #   \return \type{Exception} The error encountered during execution or None if there was no error.
    def getError(self) -> Exception:
        return self._error

    ##  Emitted when the job has finished processing.
    #
    #   \param job \type{Job} The finished job.
    finished = Signal()

    ##  Emitted when the job processing has progressed.
    #
    #   \param job \type{Job} The job reporting progress.
    #   \param amount \type{int} The amount of progress made, from 0 to 100.
    progress = Signal()

    ##  Utility function that allows us to yield thread processing.
    #
    #   This is mostly a workaround for broken python threads. This function
    #   forces a GIL release and allows a different thread to start processing
    #   if it is waiting.
    @staticmethod
    def yieldThread():
        time.sleep(0)  # Sleeping for 0 introduces no delay but does allow context switching.
