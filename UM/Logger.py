# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys
import traceback
import inspect
from typing import List

from UM.PluginObject import PluginObject


##  Static class used for logging purposes. This class is only meant to be used as a static class.
class Logger:
    __loggers = []  # type: List[Logger]

    def __init__(self):
        raise Exception("This class is static only")

    ##  Add a logger to the list.
    #   \param logger \type{Logger}
    @classmethod
    def addLogger(cls, logger: "Logger"):
        cls.__loggers.append(logger)

    ##  Get all loggers
    #   \returns \type{list} List of Loggers
    @classmethod
    def getLoggers(cls) -> List["Logger"]:
        return cls.__loggers

    ##  Send a message of certain type to all loggers to be handled.
    #
    #   This method supports placeholders in either str.format() style or % style. For more details see
    #   the respective Python documentation pages.
    #
    #   Note that only str.format() supports keyword argument placeholders. Additionally, if str.format()
    #   makes any changes, % formatting will not be applied.
    #
    #   \param log_type \type{string} Values must be; 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning).
    #   \param message \type{string} containing message to be logged
    #
    #   \param *args \type{list} List of placeholder replacements that will be passed to str.format() or %.
    #   \param **kwargs \type{dict} List of placeholder replacements that will be passed to str.format().
    @classmethod
    def log(cls, log_type: str, message: str, *args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        frame_info = inspect.getframeinfo(caller_frame)
        try:
            if args or kwargs: # Only format the message if there are args
                new_message = message.format(*args, **kwargs)

                if new_message == message:
                    new_message = message % args # Replace all the %s with the variables. Python formatting is magic.

                message = new_message

            message = "{class_name}.{function} [{line}]: {message}".format(class_name = caller_frame.f_globals["__name__"], function = frame_info.function, line = frame_info.lineno, message = message)

            for logger in cls.__loggers:
                logger.log(log_type, message)
        except Exception as e:
            print("FAILED TO LOG: ", log_type, message, e)

        if not cls.__loggers:
            print(message)

    ##  Logs that an exception occurs.
    #
    #   It'll include the traceback of the exception in the log message. The
    #   traceback is obtained from the current execution state.
    #
    #   \param log_type The importance level of the log (warning, info, etc.).
    #   \param message The message to go along with the exception.
    @classmethod
    def logException(cls, log_type: str, message: str, *args):
        cls.log(log_type, "Exception: " + message, *args)
        # The function traceback.format_exception gives a list of strings, but those are not properly split on newlines.
        # traceback.format_exc only gives back a single string, but we can properly split that. It does add an extra newline at the end, so strip that.
        for line in traceback.format_exc().rstrip().split("\n"):
            cls.log(log_type, line)


##  Abstract base class for log output classes.
class LogOutput(PluginObject):
    ##  Create the log output.
    #
    #   This is called during the plug-in loading stage.
    def __init__(self):
        super().__init__()  # Call super to make multiple inheritance work.
        self._name = type(self).__name__  # Set name of the logger to it's class name

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
    def log(self, log_type: str, message: str):
        raise NotImplementedError("Logger was not correctly implemented")
