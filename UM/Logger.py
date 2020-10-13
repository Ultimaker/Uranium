# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import threading
import traceback
import inspect
from typing import List

from UM.PluginObject import PluginObject


class Logger:
    """Static class used for logging purposes. This class is only meant to be used as a static class."""

    __loggers = []  # type: List[Logger]

    def __init__(self):
        raise Exception("This class is static only")

    @classmethod
    def addLogger(cls, logger: "Logger"):
        """Add a logger to the list."""

        cls.__loggers.append(logger)

    @classmethod
    def getLoggers(cls) -> List["Logger"]:
        """Get all loggers

        :returns: List of Loggers
        """

        return cls.__loggers

    @classmethod
    def log(cls, log_type: str, message: str, *args, **kwargs):
        """Send a message of certain type to all loggers to be handled.

        This method supports placeholders in either str.format() style or % style. For more details see
        the respective Python documentation pages.

        Note that only str.format() supports keyword argument placeholders. Additionally, if str.format()
        makes any changes, % formatting will not be applied.

        :param log_type: Values must be; 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning).
        :param message: containing message to be logged

        :param args: List of placeholder replacements that will be passed to str.format() or %.
        :param kwargs: List of placeholder replacements that will be passed to str.format().
        """

        caller_frame = inspect.currentframe()
        frame_info = None

        while caller_frame is not None:  # Avoid crash if the inspect module returns None
            caller_frame = caller_frame.f_back
            if caller_frame is None:
                return
            frame_info = inspect.getframeinfo(caller_frame)

            if frame_info.filename != __file__:  # Backtrack the stack until we found the entry point into this file
                break

        try:
            assert caller_frame is not None
            assert frame_info is not None
        except AssertionError:
            print("FAILED TO LOG (Frame not found): ", log_type, message)
            return

        try:
            if args or kwargs: # Only format the message if there are args
                new_message = message.format(*args, **kwargs)

                if new_message == message:
                    new_message = message % args # Replace all the %s with the variables. Python formatting is magic.

                message = new_message

            current_thread = threading.current_thread()
            message = "[{thread}] {class_name}.{function} [{line}]: {message}".format(thread = current_thread.name,
                                                                                      class_name = caller_frame.f_globals["__name__"],
                                                                                      function = frame_info.function,
                                                                                      line = frame_info.lineno,
                                                                                      message = message)

            for logger in cls.__loggers:
                logger.log(log_type, message)
        except Exception as e:
            print("FAILED TO LOG: ", log_type, message, e)

        if not cls.__loggers:
            print(message)

    @classmethod
    def logException(cls, log_type: str, message: str, *args):
        """Logs that an exception occurs.

        It'll include the traceback of the exception in the log message. The
        traceback is obtained from the current execution state.

        :param log_type: The importance level of the log (warning, info, etc.).
        :param message: The message to go along with the exception.
        """

        cls.log(log_type, "Exception: " + message, *args)
        # The function traceback.format_exception gives a list of strings, but those are not properly split on newlines.
        # traceback.format_exc only gives back a single string, but we can properly split that. It does add an extra newline at the end, so strip that.
        for line in traceback.format_exc().rstrip().split("\n"):
            cls.log(log_type, line)

    @classmethod
    def debug(cls, message: str, *args, **kwargs):
        """Logs a debug message (just a convenience method for log())"""

        cls.log("d", message, *args, **kwargs)

    @classmethod
    def info(cls, message: str, *args, **kwargs):
        """Logs an info message (just a convenience method for log())"""

        cls.log("i", message, *args, **kwargs)

    @classmethod
    def warning(cls, message: str, *args, **kwargs):
        """Logs a warning message (just a convenience method for log())"""

        cls.log("w", message, *args, **kwargs)

    @classmethod
    def error(cls, message: str, *args, **kwargs):
        """Logs an error message (just a convenience method for log())"""

        cls.log("e", message, *args, **kwargs)

    @classmethod
    def critical(cls, message: str, *args, **kwargs):
        """Logs a critical message (just a convenience method for log())"""

        cls.log("c", message, *args, **kwargs)


class LogOutput(PluginObject):
    """Abstract base class for log output classes."""

    def __init__(self) -> None:
        """Create the log output.

        This is called during the plug-in loading stage.
        """

        super().__init__()  # Call super to make multiple inheritance work.
        self._name = type(self).__name__  # Set name of the logger to it's class name

    def log(self, log_type: str, message: str) -> None:
        """Log a message.

        The possible message types are:
        - "d", debug
        - "i", info
        - "w", warning
        - "e", error
        - "c", critical

        :param log_type: A value describing the type of message.
        :param message: The message to log.
        :exception NotImplementedError:
        """

        raise NotImplementedError("Logger was not correctly implemented")
