# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSlot, Q_ENUMS, pyqtSignal

from datetime import timedelta
import math

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

class DurationFormat(QObject):
    class Format:
        Short = 1
        Long = 2
    Q_ENUMS(Format)

##  A class representing a time duration.
#
#   This is primarily used as a value type to QML so we can report things
#   like "How long will this print take" without needing a bunch of logic
#   in the QML.
class Duration(QObject):
    ##  Create a duration object.
    #
    #   \param duration The duration in seconds. If this is None (the default), an invalid Duration object will be created.
    #   \param parent The QObject parent.
    def __init__(self, duration = None, parent = None):
        super().__init__(parent)

        self._days = -1
        self._hours = -1
        self._minutes = -1
        self._seconds = -1

        if duration != None:
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

    ##  Set the duration in seconds.
    #
    #   This will convert the given amount of seconds into an amount of days, hours, minutes and seconds.
    #   Note that this is mostly a workaround for issues with PyQt, as a value type this class should not
    #   really have a setter.
    def setDuration(self, duration):
        if duration < 0:
            self._days = -1
            self._hours = -1
            self._minutes = -1
            self._seconds = -1
        else:
            duration = round(duration)
            self._days = math.floor(duration / (3600 * 24))
            duration -= self._days * 3600 * 24
            self._hours = math.floor(duration / 3600)
            duration -= self._hours * 3600
            self._minutes = math.floor(duration / 60)
            duration -= self._minutes * 60
            self._seconds = duration

        self.durationChanged.emit()

    ##  Get a string representation of this object that can be used to display in interfaces.
    #
    #   This is not called toString() primarily because that conflicts with JavaScript"s toString()
    @pyqtSlot(int, result = str)
    def getDisplayString(self, format = DurationFormat.Format.Short):
        if format == DurationFormat.Format.Short:
            if self._days > 0:
                return i18n_catalog.i18nc("Short days-hours-minutes format. {0} is days, {1} is hours, {2} is minutes", "{0:0>2}d {1:0>2}:{2:0>2}".format(self._days, self._hours, self._minutes))
            else:
                return i18n_catalog.i18nc("Short hours-minutes format. {0} is hours, {1} is minutes", "{0:0>2}:{1:0>2}".format(self._hours, self._minutes))
        elif format == DurationFormat.Format.Long:
            if self._days > 0:
                return i18n_catalog.i18nc("Days-hours-minutes duration format. {0} is days, {1} is hours, {2} is minutes", "{0} days {1} hours {2} minutes".format(self._days, self._hours, self._minutes))
            elif self._hours > 0:
                return i18n_catalog.i18nc("Hours-minutes duration fromat. {0} is hours, {1} is minutes", "{0} hours {1} minutes".format(self._hours, self._minutes))
            else:
                return i18n_catalog.i18nc("Minutes only duration format, {0} is minutes", "{0} minutes".format(self._minutes))

        return ""

