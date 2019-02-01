# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Union, Dict

from PyQt5.QtCore import QUrl, QObject, pyqtProperty

from UM.View.Renderer import Renderer
from UM.PluginObject import PluginObject

import UM.Application

MYPY = False
if MYPY:
    from UM.Controller import Controller


## Abstract base class for view objects.
class View(QObject, PluginObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._renderer = None  # type: Optional[Renderer]
        self._controller = UM.Application.Application.getInstance().getController()  # type: Controller
        self._components = {}  # type: Dict[str, QUrl]

    @pyqtProperty(str, constant = True)
    def name(self) -> str:
        return self.getPluginId()

    ##  Add a QML component that is provided by this View.
    def addDisplayComponent(self, name: str, source: Union[str, QUrl]) -> None:
        if type(source) == str:
            source = QUrl.fromLocalFile(source)
        self._components[name] = source

    ##  Get a QUrl by name.
    def getDisplayComponent(self, name: str) -> QUrl:
        if name in self._components:
            return self._components[name]
        return QUrl()

    ##  Get the controller object associated with this View.
    #   \sa Controller
    def getController(self):
        return self._controller

    ##  Get the Renderer instance for this View.
    def getRenderer(self):
        return self._renderer

    ##  Set the renderer object to use with this View.
    #   \param renderer \type{Renderer} The renderer to use.
    def setRenderer(self, renderer: Renderer) -> None:
        self._renderer = renderer

    ##  Begin the rendering process.
    #
    #   This should queue all the meshes that should be rendered.
    def beginRendering(self) -> None:
        raise NotImplementedError()

    ##  Perform any steps needed when ending the rendering process.
    #
    #   If there is any cleanup or other tasks that need to be performed
    #   after rendering this method should be used.
    def endRendering(self) -> None:
        raise NotImplementedError()
    
    ##  Handle an event.
    #   \param event \type{Event} The event to handle.
    #   \sa Event
    def event(self, event):
        pass
