# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Union

from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, QUrl

from UM.PluginObject import PluginObject

##  Stages handle combined views in an Uranium application.
#   The active stage decides which QML component to show where.
#   Uranium has no notion of specific view locations as that's application specific.
class Stage(QObject, PluginObject):

    iconSourceChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self._components = {}
        self._icon_source = QUrl()

    ##  Add a QML component to the stage
    def addDisplayComponent(self, name: str, component: QObject):
        self._components[name] = component

    ##  Get a QML component by name.
    def getDisplayComponent(self, name: str):
        if name in self._components:
            return self._components[name]
        return None

    @pyqtProperty(QUrl, notify = iconSourceChanged)
    def iconSource(self):
        return self._icon_source

    def setIconSource(self, source: Union[str, QUrl]):
        if type(source) == str:
            source = QUrl(source)

        if self._icon_source != source:
            self._icon_source = source
            self.iconSourceChanged.emit()
