# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Q_ENUMS

from UM.Resources import Resources
from UM.Logger import Logger

class ResourcesProxy(QObject):
    class Type:
        Resources = Resources.Resources
        Preferences = Resources.Preferences
        Themes = Resources.Themes
        Images = Resources.Images
        Meshes = Resources.Meshes
        i18n = Resources.i18n
        Shaders = Resources.Shaders
        UserType = Resources.UserType
    Q_ENUMS(Type)

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(int, str, result = str)
    def getPath(self, type, name):
        try:
            return UM.Resources.getPath(type, name)
        except:
            Logger.log("w", "Could not find the requested resource: %s", name)
            return ""
