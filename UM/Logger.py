# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import sys
import inspect
from functools import wraps
import time
import threading
import traceback

from UM.PluginObject import PluginObject


##  Static class used for logging purposes. This class is only meant to be used as a static class.
class Logger:
    def __init__(self):
        raise Exception("This class is static only")

    ##  Add a logger to the list.
    #   \param logger \type{Logger}
    @classmethod
    def addLogger(cls, logger):
        cls.__loggers.append(logger)

    ##  Get all loggers
    #   \returns \type{list} List of Loggers
    @classmethod
    def getLoggers(cls):
        return cls.__loggers

    ##  Send a message of certain type to all loggers to be handled.
    #   \param log_type \type{string} Values must be; 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning).
    #   \param message \type{string} containing message to be logged
    #   \param *args \type{list} List of variables to be added to the message.
    @classmethod
    def log(cls, log_type, message, *args):
        function = inspect.currentframe().f_back.f_code
        filename = function.co_filename
        for path in sys.path:
            if filename.startswith(path):
                filename = filename.replace(path, "...")
                continue
        address = "%s (%s [%s]): " %(filename, function.co_name, function.co_firstlineno)
        
        if args: # Only format the message if there are args
            message = message % args # Replace all the %s with the variables. Python formatting is magic.
        
        for logger in cls.__loggers:
            filled_message = address + message
            logger.log(log_type, filled_message)

        if not cls.__loggers:
            print(message)

    ##
    @classmethod
    def logException(cls, log_type, message, *args):
        cls.log(log_type, "Exception: " + message, *args)
        # The function traceback.format_exception gives a list of strings, but those are not properly split on newlines.
        # traceback.format_exc only gives back a single string, but we can properly split that. It does add an extra newline at the end, so strip that.
        for line in traceback.format_exc().rstrip().split("\n"):
            cls.log(log_type, line)

    __loggers = []

##  Decorator to time how long a function takes to execute.
def timeIt(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        Logger.log("d", "@timeIt: {0} took {1:.3f}s".format(fn.__name__, t2-t1))
        return result
    return measure_time

##  Decorator which logs the name of the current thread.
def logThread(fn):
    @wraps(fn)
    def logIt(*args, **kwargs):
        Logger.log("d", "@logThread: {0} running on thread {1}".format(fn.__name__, threading.current_thread().name))
        return fn(*args, **kwargs)
    return logIt

##  Decorator which logs the parameters and start and end of a function/method.
def spy(fn):
    @wraps(fn)
    def spyIt(*args, **kwargs):
        arg_str = "{0}({1})".format(fn.__name__, ",".join( (repr(a) for a in args) ))
        Logger.log("d", "@spy: -> " + arg_str)
        result = fn(*args, **kwargs)
        Logger.log("d", "@spy: <- " + arg_str + " returning " + repr(result))
        return result
    return spyIt

##  Decorator which logs the current execution stack when the function/method is called.
def logStack(fn):
    @wraps(fn)
    def logIt(*args, **kwargs):
        Logger.log("d", "@logStack: {0} stack {1}".format(fn.__name__, traceback.format_stack()))
        return fn(*args, **kwargs)
    return logIt

##  Abstract base class for log output classes.
class LogOutput(PluginObject):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritance work.
        self._name = type(self).__name__ # Set name of the logger to it's class name

    ##  Log a message.
    #
    #   The possible message types are:
    #   - "d", debug
    #   - "i", info
    #   - "w", warning
    #   - "e", error
    #   - "c", critical
    #
    #   \param log_type \type{string} A value describing the type of message.
    #   \param message \type{string} The message to log.
    #   \exception NotImplementedError
    def log(self, log_type, message):
        raise NotImplementedError("Logger was not correctly implemented")
