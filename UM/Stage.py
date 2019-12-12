# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Union, Dict

from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, QUrl

from UM.PluginObject import PluginObject


##  Stages handle combined views in an Uranium application.
#   The active stage decides which QML component to show where.
#   Uranium has no notion of specific view locations as that's application specific.
class Stage(QObject, PluginObject):

    iconSourceChanged = pyqtSignal()

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._components = {}  # type: Dict[str, QUrl]
        self._icon_source = QUrl()

    ##  Something to do when this Stage is selected
    def onStageSelected(self) -> None:
        pass

    ##  Something to do when this Stage is deselected
    def onStageDeselected(self) -> None:
        pass

    ##  Add a QML component to the stage
    def addDisplayComponent(self, name: str, source: Union[str, QUrl]) -> None:
        if type(source) == str:
            source = QUrl.fromLocalFile(source)
        self._components[name] = source

    ##  Get a QUrl by name.
    def getDisplayComponent(self, name: str) -> QUrl:
        if name in self._components:
            return self._components[name]
        return QUrl()

    @pyqtProperty(QUrl, notify = iconSourceChanged)
    def iconSource(self) -> QUrl:
        return self._icon_source

    def setIconSource(self, source: Union[str, QUrl]) -> None:
        if type(source) == str:
            source = QUrl.fromLocalFile(source)

        if self._icon_source != source:
            self._icon_source = source
            self.iconSourceChanged.emit()
