from threading import Lock

from twisted.internet import reactor
from twisted.internet.base import DelayedCall
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.task import LoopingCall
from twisted.python.threadable import isInIOThread

from .util import blocking_call_on_reactor_thread


CLEANUP_FREQUENCY = 100


class TaskManager:

    """
    Provides a set of tools to mantain a list of twisted "tasks" (Deferred, LoopingCall, DelayedCall) that are to be
    executed during the lifetime of an arbitrary object, usually getting killed with it.
    """
    _reactor = reactor

    def __init__(self):
        self._pending_tasks = {}
        self._cleanup_counter = CLEANUP_FREQUENCY
        self._task_lock = Lock()

    def replace_task(self, name: str, task):
        """
        Replace named task with the new one, cancelling the old one in the process.
        """
        self.cancel_pending_task(name)
        return self.register_task(name, task)

    def register_task(self, name: str, task, delay=None, value=None, interval=None):
        """
        Register a task so it can be canceled at shutdown time or by name.
        """
        #assert isInIOThread()
        assert not self.is_pending_task_active(name), name
        assert isinstance(task, (Deferred, DelayedCall, LoopingCall)), (task, type(task) == type(Deferred))

        if delay is not None:
            if isinstance(task, Deferred):
                if value is None:
                    raise ValueError("Expecting value to fire the Deferred with")
                dc = self._reactor.callLater(delay, task.callback, value)
            elif isinstance(task, LoopingCall):
                if interval is None:
                    raise ValueError("Expecting interval for delayed LoopingCall")
                dc = self._reactor.callLater(delay, task.start, interval)
            else:
                raise ValueError("Expecting Deferred or LoopingCall if task is delayed")

            task = (dc, task)

        self._maybe_clean_task_list()
        with self._task_lock:
            self._pending_tasks[name] = task
        return task

    @blocking_call_on_reactor_thread
    def cancel_pending_task(self, name: str) -> None:
        """
        Cancels the named task
        """
        self._maybe_clean_task_list()
        is_active, stopfn = self._get_isactive_stopper(name)
        if is_active and stopfn:
            stopfn()
            self._pending_tasks.pop(name)

    def cancel_all_pending_tasks(self) -> None:
        """
        Cancels all the registered tasks.
        This usually should be called when stopping or destroying the object so no tasks are left floating around.
        """
        assert all([isinstance(task, (Deferred, DelayedCall, LoopingCall, tuple))
                    for task in self._pending_tasks.itervalues()]), self._pending_tasks

        for name in self._pending_tasks.keys():
            self.cancel_pending_task(name)

    def is_pending_task_active(self, name: str) -> None:
        """
        Return a boolean determining if a task is active.
        """
        return self._get_isactive_stopper(name)[0]

    def wait_for_deferred_tasks(self) -> "DeferredList":
        """
        Returns a deferred that will fire when all registered Deferreds are done.
        """
        assert isInIOThread()
        self._maybe_clean_task_list()
        return DeferredList(self._iter_deferreds())

    def _iter_deferreds(self) -> None:
        for task in self._pending_tasks.values():
            if isinstance(task, Deferred):
                yield task

    def _get_isactive_stopper(self, name: str):
        """
        Return a boolean determining if a task is active and its cancel/stop method if the task is registered.
        """
        task = self._pending_tasks.get(name, None)

        def do_get(task):
            if isinstance(task, Deferred):
                # Have in mind that any deferred in the pending tasks list should have been constructed with a
                # canceller function.
                return not task.called, getattr(task, 'cancel', None)
            elif isinstance(task, DelayedCall):
                return task.active(), task.cancel
            elif isinstance(task, LoopingCall):
                return task.running, task.stop
            elif isinstance(task, tuple):
                if task[0].active():
                    return task[0].active(), task[0].cancel
                else:
                    return do_get(task[1])
            else:
                return False, None

        return do_get(task)

    def _maybe_clean_task_list(self) -> None:
        """
        Removes finished tasks from the task list.
        """
        if self._cleanup_counter:
            self._cleanup_counter -= 1
        else:
            self._cleaup_counter = CLEANUP_FREQUENCY
            for name in self._pending_tasks.keys():
                if not self.is_pending_task_active(name):
                    self._pending_tasks.pop(name)
