from queue import Queue
import logging
import traceback

from twisted.internet import reactor, defer
from twisted.python import failure
from twisted.python.threadable import isInIOThread


logger = logging.getLogger(__name__)


MEMORY_DUMP_INTERVAL = float(60 * 60)


#
# Various decorators
#

def call_on_reactor_thread(func):
    def helper(*args, **kargs):
        if isInIOThread():
            # TODO(emilon): Do we really want it to block if its on the reactor thread?
            return func(*args, **kargs)
        else:
            return reactor.callFromThread(func, *args, **kargs)
    helper.__name__ = func.__name__
    return helper


def blocking_call_on_reactor_thread(func):
    def helper(*args, **kargs):
        return blockingCallFromThread(reactor, func, *args, **kargs)
    helper.__name__ = func.__name__
    return helper


#
# Other utils
#


def unhandled_error_observer(event):
    """
    Stop the reactor if we get an unhandled error.
    """
    if event['isError']:
        logger.warning("Strict, mode enabled, stopping the reactor")
        # TODO(emilon): Should we try to stop dispersy too?
        reactor.exitCode = 1
        if reactor.running:
            reactor.stop()


def blockingCallFromThread(reactor, f, *args, **kwargs):
    """
    Improved version of twisted's blockingCallFromThread that shows the complete
    stacktrace when an exception is raised on the reactor's thread.
    If being called from the reactor thread already, just return the result of execution of the callable.
    """
    if isInIOThread():
            return f(*args, **kwargs)
    else:
        queue = Queue.Queue()

        def _callFromThread():
            result = defer.maybeDeferred(f, *args, **kwargs)
            result.addBoth(queue.put)
        reactor.callFromThread(_callFromThread)
        result = queue.get()
        if isinstance(result, failure.Failure):
            other_thread_tb = traceback.extract_tb(result.getTracebackObject())
            this_thread_tb = traceback.extract_stack()
            logger.error("Exception raised on the reactor's thread %s: \"%s\".\n Traceback from this thread:\n%s\n"
                         " Traceback from the reactor's thread:\n %s", result.type.__name__, result.getErrorMessage(),
                         ''.join(traceback.format_list(this_thread_tb)), ''.join(traceback.format_list(other_thread_tb)))
            result.raiseException()
        return result
