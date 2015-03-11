from PyQt5.QtCore import QObject, pyqtSlot

from UM.Preferences import Preferences

class PreferencesProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._preferences = Preferences.getInstance()

    @pyqtSlot(str, result = 'QVariant')
    def getValue(self, key):
        return self._preferences.getValue(key)

    @pyqtSlot(str, 'QVariant')
    def setValue(self, key, value):
        self._preferences.setValue(key, value)

    @pyqtSlot(str)
    def resetValue(self, key):
        self._preferences.resetValue(key)

def createPreferencesProxy(engine, script_engine):
    return PreferencesProxy()
