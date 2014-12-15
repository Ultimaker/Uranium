from PyQt5.QtCore import QObject, pyqtSlot, QUrl

from UM.Resources import Resources

class ResourcesProxy(QObject):
    ResourcesLocation = Resources.ResourcesLocation
    SettingsLocation = Resources.SettingsLocation
    PreferencesLocation = Resources.PreferencesLocation

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(int, result=QUrl)
    def getPath(self, type):
        return QUrl.fromLocalFile(Resources.getPath(type))

    @pyqtSlot(str, result=QUrl)
    def getIcon(self, name):
        return QUrl.fromLocalFile(Resources.getIcon(name))
