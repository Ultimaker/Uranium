# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import multiprocessing
import threading

from UM.Logger import Logger
from UM.Signal import Signal, signalemitter

from typing import cast, List, Optional, TYPE_CHECKING, Union
if TYPE_CHECKING:
    from UM.Job import Job

##  A thread pool and queue manager for Jobs.
#
#   The JobQueue class manages a queue of Job objects and a set of threads that
#   can take things from this queue to process them.
#   \sa Job
@signalemitter
class JobQueue:
    ##  Initialize.
    #
    #   \param thread_count The amount of threads to use. Can be a positive integer or 'auto'.
    #                       When 'auto', the number of threads is based on the number of processors and cores on the machine.
    def __init__(self, thread_count: Union[str, int] = "auto") -> None: #pylint: disable=bad-whitespace
        if JobQueue.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        JobQueue.__instance = self

        super().__init__()

        if thread_count == "auto":
            try:
                thread_count = multiprocessing.cpu_count()
            except NotImplementedError:
                thread_count = 0
        thread_count = cast(int, thread_count) #Now it's always an integer.

        if thread_count <= 0:
            thread_count = 2  # Assume we can run at least two threads in parallel.

        self._threads = [_Worker(self) for t in range(thread_count)]

        self._semaphore = threading.Semaphore(0)
        self._jobs = []  # type: List[Job]
        self._jobs_lock = threading.Lock()

        for thread in self._threads:
            thread.daemon = True
            thread.start()

    ##  Add a Job to the queue.
    #
    #   \param job The Job to add.
    def add(self, job: "Job") -> None:
        with self._jobs_lock:
            self._jobs.append(job)
            self._semaphore.release()

    ##  Remove a waiting Job from the queue.
    #
    #   \param job The Job to remove.
    #
    #   \note If a job has already begun processing it is already removed from the queue
    #   and thus can no longer be cancelled.
    def remove(self, job: "Job") -> None:
        with self._jobs_lock:
            if job in self._jobs:
                self._jobs.remove(job)

    ##  Emitted whenever a job starts processing.
    #
    #   \param job \type{Job} The job that has started processing.
    jobStarted = Signal()

    ##  Emitted whenever a job has finished processing.
    #
    #   \param job \type{Job} The job that has finished processing.
    jobFinished = Signal()

    ## protected:

    #   Get the next job off the queue.
    #   Note that this will block until a job is available.
    def _nextJob(self) -> Optional["Job"]:
        self._semaphore.acquire()
        with self._jobs_lock:
            # Semaphore release() can apparently cause all waiting threads to continue.
            # So to prevent issues, double check whether we actually have waiting jobs.
            if not self._jobs:
                return None
            return self._jobs.pop(0)

    __instance = None

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "JobQueue":
        return cls.__instance


##  Internal
#
#   A worker thread that can process jobs from the JobQueue.
class _Worker(threading.Thread):
    def __init__(self, queue: JobQueue) -> None:
        super().__init__()
        self._queue = queue

    def run(self) -> None:
        while True:
            # Get the next job from the queue. Note that this blocks until a new job is available.
            job = self._queue._nextJob()
            if not job:
                continue

            # Process the job.
            self._queue.jobStarted.emit(job)
            job._running = True

            try:
                job.run()
            except Exception as e:
                Logger.logException("e", "Job %s caused an exception", str(job))
                job.setError(e)

            job._running = False
            job._finished = True
            job.finished.emit(job)
            self._queue.jobFinished.emit(job)
