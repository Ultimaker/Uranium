# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.


from UM.Signal import Signal, SignalEmitter

from UM.JobQueue import JobQueue

##  Base class for things that should be performed in a thread.
#
#   The Job class provides a basic interface for a 'job', that is a
#   self-contained task that should be performed in a thread. It makes
#   use of the JobQueue for the actual threading.
class Job(SignalEmitter):
    ##  Initialize.
    #
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - description \type{string} A short description of the job that can be displayed in the UI. Defaults to an empty string.
    #                 - visible \type{bool} True if this job should be shown in the UI, False if not. Defaults to False
    def __init__(self, **kwargs):
        super().__init__()
        self._running = False
        self._finished = False
        self._result = None
        self._description = kwargs.get("description", "")
        self._visible = kwargs.get("visible", False)
        self._error = None

    ##  Get the description for this job.
    def getDescription(self):
        return self._description

    ##  Should this job be shown in the UI
    #   \return \type{bool}
    def isVisible(self):
        return self._visible

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
    def setResult(self, result):
        self._result = result

    def setError(self, error):
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
    def isRunning(self):
        return self._running

    ##  Check whether the job has finished processing.
    #
    #   \return \type{bool}
    def isFinished(self):
        return self._finished

    def hasError(self):
        return self._error is not None

    def getError(self):
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
