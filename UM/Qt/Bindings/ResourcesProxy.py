# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, QUrl, Q_ENUMS
from UM.FlameProfiler import pyqtSlot

import UM.Resources
from UM.Logger import Logger

class ResourcesProxy(QObject):
    class Type:
        Resources = UM.Resources.Resources.Resources
        Preferences = UM.Resources.Resources.Preferences
        Themes = UM.Resources.Resources.Themes
        Images = UM.Resources.Resources.Images
        Meshes = UM.Resources.Resources.Meshes
        i18n = UM.Resources.Resources.i18n
        Shaders = UM.Resources.Resources.Shaders
        UserType = UM.Resources.Resources.UserType
    Q_ENUMS(Type)

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(int, str, result = str)
    def getPath(self, type, name):
        try:
            return UM.Resources.Resources.getPath(type, name)
        except:
            Logger.log("w", "Could not find the requested resource: %s", name)
            return ""
