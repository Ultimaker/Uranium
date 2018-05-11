# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from UM.Application import Application

class PreferencesProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._preferences = Application.getInstance().getPreferences()
        self._preferences.preferenceChanged.connect(self._onPreferenceChanged)

    preferenceChanged = pyqtSignal(str, arguments = ["preference"])

    @pyqtSlot(str, result = "QVariant")
    def getValue(self, key):
        return self._preferences.getValue(key)

    @pyqtSlot(str, "QVariant")
    def setValue(self, key, value):
        self._preferences.setValue(key, value)

    @pyqtSlot(str)
    def resetPreference(self, key):
        self._preferences.resetPreference(key)

    def _onPreferenceChanged(self, preference):
        self.preferenceChanged.emit(preference)

def createPreferencesProxy(engine, script_engine):
    return PreferencesProxy()
