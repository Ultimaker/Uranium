from PyQt5.QtCore import QObject, pyqtSlot

from Cura.Resources import Resources

class ResourcesProxy(QObject):
    ResourcesLocation = Resources.ResourcesLocation
    SettingsLocation = Resources.SettingsLocation
    PreferencesLocation = Resources.PreferencesLocation

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(int, result=str)
    def getPath(self, type):
        return Resources.getPath(type)

    @pyqtSlot(str, result=str)
    def getIcon(self, name):
        return Resources.getIcon(name)
