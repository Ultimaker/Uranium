# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional

from PyQt5.QtCore import QObject, pyqtProperty, Q_ENUMS, pyqtSignal
from UM.FlameProfiler import pyqtSlot

from datetime import timedelta
import math

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")


class DurationFormat(QObject):
    class Format:
        Seconds = 0
        Short = 1
        Long = 2
        ISO8601 = 3
    Q_ENUMS(Format)


class Duration(QObject):
    """A class representing a time duration.

    This is primarily used as a value type to QML so we can report things
    like "How long will this print take" without needing a bunch of logic
    in the QML.
    """

    def __init__(self, duration: Optional[int] = None, parent = None) -> None:
        """Create a duration object.

        :param duration: The duration in seconds. If this is None (the default), an invalid Duration object will be created.
        :param parent: The QObject parent.
        """

        super().__init__(parent)

        self._days = -1
        self._hours = -1
        self._minutes = -1
        self._seconds = -1

        if duration is not None:
            self.setDuration(duration)

    durationChanged = pyqtSignal()

    @pyqtProperty(int, notify = durationChanged)
    def days(self):
        return self._days

    @pyqtProperty(int, notify = durationChanged)
    def hours(self):
        return self._hours

    @pyqtProperty(int, notify = durationChanged)
    def minutes(self):
        return self._minutes

    @pyqtProperty(int, notify = durationChanged)
    def seconds(self):
        return self._seconds

    @pyqtProperty(bool, notify = durationChanged)
    def valid(self):
        return self._days != -1 and self._hours != -1 and self._minutes != -1 and self._seconds != -1

    @pyqtProperty(bool, notify = durationChanged)
    def isTotalDurationZero(self):
        return self._days == 0 and self._hours == 0 and self._minutes == 0 and self._seconds == 0

    def setDuration(self, duration: int) -> None:
        """Set the duration in seconds.

        This will convert the given amount of seconds into an amount of days, hours, minutes and seconds.
        Note that this is mostly a workaround for issues with PyQt, as a value type this class should not
        really have a setter.
        """

        if duration < 0:
            self._days = -1
            self._hours = -1
            self._minutes = -1
            self._seconds = -1
        else:
            duration = round(duration)
            # If a Python int goes above the upper bound of C++ int, which is 2^16 - 1, you will get a error when Qt
            # tries to convert the Python int to C++ int:
            #    TypeError: unable to convert a Python 'int' object to a C++ 'int' instance
            # So we make sure here that the number won't exceed the limit due to CuraEngine bug or whatever, and
            # Cura won't crash.
            if int(duration) >= (2**31):
                duration = 0

            self._days = math.floor(duration / (3600 * 24))
            duration -= self._days * 3600 * 24
            self._hours = math.floor(duration / 3600)
            duration -= self._hours * 3600
            self._minutes = math.floor(duration / 60)
            duration -= self._minutes * 60
            self._seconds = duration

        self.durationChanged.emit()

    @pyqtSlot(int, result = str)
    def getDisplayString(self, display_format = DurationFormat.Format.Short):
        """Get a string representation of this object that can be used to display
        in interfaces.

        This is not called toString() primarily because that conflicts with
        JavaScript's toString().
        :return: A human-readable string representation of this duration.
        """

        if display_format == DurationFormat.Format.Seconds:
            return str(((self._days * 24 + self._hours)* 60 + self._minutes) * 60 + self._seconds )
        elif display_format == DurationFormat.Format.Short:
            if self._days > 0:
                return i18n_catalog.i18nc("@label Short days-hours-minutes format. {0} is days, {1} is hours, {2} is minutes", "{0:0>2}d {1:0>2}h {2:0>2}min", self._days, self._hours, self._minutes)
            else:
                return i18n_catalog.i18nc("@label Short hours-minutes format. {0} is hours, {1} is minutes", "{0:0>2}h {1:0>2}min", self._hours, self._minutes)
        elif display_format == DurationFormat.Format.Long:
            if self._days > 0:
                return i18n_catalog.i18ncp("@label Long duration format. {0} is days", "{0} day", "{0} days", self._days) + " " + i18n_catalog.i18ncp("@label Long duration format. {0} is hours", "{0} hour", "{0} hours", self._hours) + " " + i18n_catalog.i18ncp("@label Long duration format. {0} is minutes", "{0} minute", "{0} minutes", self._minutes)
            elif self._hours > 0:
                return i18n_catalog.i18ncp("@label Long duration format. {0} is hours", "{0} hour", "{0} hours", self._hours) + " " + i18n_catalog.i18ncp("@label Long duration format. {0} is minutes", "{0} minute", "{0} minutes", self._minutes)
            else:
                return i18n_catalog.i18ncp("@label Long duration format. {0} is minutes", "{0} minute", "{0} minutes", self._minutes)
        elif display_format == DurationFormat.Format.ISO8601:
            return "%02d:%02d:%02d" % (self._days * 24 + self._hours, self._minutes, self._seconds)

        return ""

    def __int__(self):
        """Get an integer representation of this duration.

        The integer contains the number of seconds in the duration. Convert it
        back to a Duration instance by providing the number of seconds to the
        constructor.
        """

        return self._days * 3600 * 24 + self._hours * 3600 + self._minutes * 60 + self._seconds