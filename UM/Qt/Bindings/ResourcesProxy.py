# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Q_ENUMS

from UM.Resources import Resources

class ResourcesProxy(QObject):
    class Location:
        ResourcesLocation = Resources.ResourcesLocation
        SettingsLocation = Resources.SettingsLocation
        PreferencesLocation = Resources.PreferencesLocation
        ThemesLocation = Resources.ThemesLocation
        ImagesLocation = Resources.ImagesLocation
        WizardPagesLocation = Resources.WizardPagesLocation
    Q_ENUMS(Location)

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(int, str, result=QUrl)
    def getPath(self, type, name):
        return QUrl.fromLocalFile(Resources.getPath(type, name))
