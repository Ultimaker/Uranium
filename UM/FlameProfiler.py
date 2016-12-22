# Uranium is released under the terms of the AGPLv3 or higher.

import time
import math
from contextlib import contextmanager

from UM.Logger import Logger

###########################################################################
SIGNAL_PROFILE = True
record_profile = False

class ProfileCallNode:
    def __init__(self, name, line_number, start_time, end_time, children):
        self.__name = name
        self.__line_number = line_number
        self.__start_time = start_time
        self.__end_time = end_time
        self.__children = children if children is not None else [] # type: List[ProfileCallNode]

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
child_accu_stack = [ [] ]
clear_profile_requested = False
record_profile_requested = False
stop_record_profile_requested = False

def getProfileData():
    raw_profile_calls = child_accu_stack[0]
    if len(raw_profile_calls) == 0:
        return None

    start_time = raw_profile_calls[0].getStartTime()
    end_time = raw_profile_calls[-1].getEndTime()
    fill_children = fillInProfileSpaces(start_time, end_time, raw_profile_calls)
    return ProfileCallNode("", 0, start_time, end_time, fill_children)

def clearProfileData():
    global clear_profile_requested
    clear_profile_requested = True

def startRecordingProfileData():
    global record_profile_requested
    record_profile_requested = True

def stopRecordingProfileData():
    global stop_record_profile_requested
    stop_record_profile_requested = True

def fillInProfileSpaces(start_time, end_time, profile_call_list):
    result = []
    time_counter = start_time
    for profile_call in profile_call_list:
        if secondsToMS(profile_call.getStartTime()) != secondsToMS(time_counter):
            result.append(ProfileCallNode("", 0, time_counter, profile_call.getStartTime(), []))
        result.append(profile_call)
        time_counter = profile_call.getEndTime()

    if secondsToMS(time_counter) != secondsToMS(end_time):
        result.append(ProfileCallNode("", 0, time_counter, end_time, []))

    return result

def secondsToMS(value):
    return math.floor(value *1000)

@contextmanager
def profileCall(name):
    start_time = time.time()
    child_accu_stack.append([])
    yield
    end_time = time.time()
    call_stat = ProfileCallNode(name, 0, start_time, end_time,
                                fillInProfileSpaces(start_time, end_time, child_accu_stack.pop()))
    child_accu_stack[-1].append(call_stat)

def isRecordingProfile():
    global record_profile
    return record_profile


def markProfileRoot():
    global child_accu_stack
    global record_profile

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
    def runIt(*args, ** kwargs):
        if isRecordingProfile():
            with profileCall(function.__qualname__):
                return function(*args, ** kwargs)
        else:
            return function(*args, **kwargs)
    return runIt
