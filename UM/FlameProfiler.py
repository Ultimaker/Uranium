# Uranium is released under the terms of the LGPLv3 or higher.
import time
import math
import os
import threading
from contextlib import contextmanager
import functools
from typing import List, Callable, Any

from PyQt5.QtCore import pyqtSlot as pyqt5PyqtSlot
from UM.Logger import Logger
# A simple profiler which produces data suitable for viewing as a flame graph
# when using the Big Flame Graph plugin.
#
# An example of code which uses this profiling data is this Cura plugin:
# https://github.com/sedwards2009/cura-big-flame-graph
#
# Set the environment variable URANIUM_FLAME_PROFILER to something before
# starting the application to make the profiling code available.


def enabled() -> bool:
    return "URANIUM_FLAME_PROFILER" in os.environ


record_profile = False  # Flag to keep track of whether we are recording data.


# Profiling data is build up of a tree of these kinds of nodes. Each node
# has a name, start time, end time, and a list of children nodes which are
# other functions/methods which were called by this function.
class _ProfileCallNode:
    def __init__(self, name, line_number, start_time, end_time, children):
        self.__name = name
        self.__line_number = line_number
        self.__start_time = start_time
        self.__end_time = end_time
        self.__children = children if children is not None else [] # type: List[_ProfileCallNode]

    def getStartTime(self):
        return self.__start_time

    def getEndTime(self):
        return self.__end_time

    def getDuration(self):
        return self.__end_time - self.__start_time

    def toJSON(self, root=False):
        if root:
            return """
{
  "c": {
    "callStats": """ + self._plainToJSON() + """,
    "sampleIterval": 1,
    "objectName": "Cura",
    "runTime": """ + str(self.getDuration()) + """,
    "totalSamples": """ + str(self.getDuration()) + """
  },
  "version": "0.34"
}
"""
        else:
            return self._plainToJSON()

    def _plainToJSON(self):
        return '''{
"stack": [
  "''' + self.__name + '''",
  "Code: ''' + self.__name + '''",
  ''' + str(self.__line_number) + ''',
  ''' + str(self.getDuration()) + '''
],
"sampleCount": '''+ str(self.getDuration()) + ''',
"children": [
    ''' + ",\n".join( [kid.toJSON() for kid in self.__children]) + '''
]
}
'''
child_accu_stack = [ [] ]   # type: List[List[_ProfileCallNode]]
clear_profile_requested = False
record_profile_requested = False
stop_record_profile_requested = False


def getProfileData():
    """Fetch the accumulated profile data.

    :return: :type{ProfileCallNode} or None if there is no data.
    """

    raw_profile_calls = child_accu_stack[0]
    if len(raw_profile_calls) == 0:
        return None

    start_time = raw_profile_calls[0].getStartTime()
    end_time = raw_profile_calls[-1].getEndTime()
    fill_children = _fillInProfileSpaces(start_time, end_time, raw_profile_calls)
    return _ProfileCallNode("", 0, start_time, end_time, fill_children)


def clearProfileData():
    """Erase any profile data."""

    global clear_profile_requested
    clear_profile_requested = True


def startRecordingProfileData():
    """Start recording profile data."""

    global record_profile_requested
    global stop_record_profile_requested
    stop_record_profile_requested = False
    record_profile_requested = True


def stopRecordingProfileData():
    """Stop recording profile data."""

    global stop_record_profile_requested
    stop_record_profile_requested = True


def _fillInProfileSpaces(start_time, end_time, profile_call_list):
    result = []
    time_counter = start_time
    for profile_call in profile_call_list:
        if secondsToMS(profile_call.getStartTime()) != secondsToMS(time_counter):
            result.append(_ProfileCallNode("", 0, time_counter, profile_call.getStartTime(), []))
        result.append(profile_call)
        time_counter = profile_call.getEndTime()

    if secondsToMS(time_counter) != secondsToMS(end_time):
        result.append(_ProfileCallNode("", 0, time_counter, end_time, []))

    return result


def secondsToMS(value):
    return math.floor(value *1000)


@contextmanager
def profileCall(name):
    """Profile a block of code.

    Use this context manager to wrap and profile a block of code.
    :param name: :type{str} The name to use to identify this code in the profile report.
    """

    if enabled():
        start_time = time.perf_counter()
        child_accu_stack.append([])
        yield
        end_time = time.perf_counter()

        child_values = child_accu_stack.pop()
        if (end_time - start_time) > 0.001: # Filter out small durations (< 1ms)
            call_stat = _ProfileCallNode(name, 0, start_time, end_time, _fillInProfileSpaces(start_time, end_time,
                                                                                         child_values))
            child_accu_stack[-1].append(call_stat)
    else:
        yield


def isRecordingProfile() -> bool:
    """Return whether we are recording profiling information.

    :return: :type{bool} True if we are recording.
    """

    global record_profile
    return record_profile and threading.main_thread() is threading.current_thread()


def updateProfileConfig():
    global child_accu_stack
    global record_profile

    # We can only update the active profiling config when we are not deeply nested inside profiled calls.
    if len(child_accu_stack) <= 1:
        global clear_profile_requested
        if clear_profile_requested:
            clear_profile_requested = False
            child_accu_stack = [[]]

        global record_profile_requested
        if record_profile_requested:
            record_profile_requested = False
            record_profile = True
            Logger.log('d', 'Starting record record_profile_requested')

        global stop_record_profile_requested
        if stop_record_profile_requested:
            stop_record_profile_requested = False
            record_profile = False
            Logger.log('d', 'Stopping record stop_record_profile_requested')


def profile(function):
    """Decorator which can be manually applied to methods to record profiling information."""

    if enabled():
        @functools.wraps(function)
        def runIt(*args, ** kwargs):
            if isRecordingProfile():
                with profileCall(function.__qualname__):
                    return function(*args, ** kwargs)
            else:
                return function(*args, **kwargs)
        return runIt
    else:
        return function


def pyqtSlot(*args, **kwargs) -> Callable[..., Any]:
    """Drop in replacement for PyQt5's pyqtSlot decorator which records profiling information.

    See the PyQt5 documentation for information about pyqtSlot.
    """

    if enabled():
        def wrapIt(function):
            @functools.wraps(function)
            def wrapped(*args2, **kwargs2):
                if isRecordingProfile():
                    with profileCall("[SLOT] "+ function.__qualname__):
                        return function(*args2, **kwargs2)
                else:
                    return function(*args2, **kwargs2)

            return pyqt5PyqtSlot(*args, **kwargs)(wrapped)
        return wrapIt
    else:
        def dontWrapIt(function):
            return pyqt5PyqtSlot(*args, **kwargs)(function)
        return dontWrapIt
