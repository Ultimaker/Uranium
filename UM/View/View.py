# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Union, Dict, TYPE_CHECKING

from PyQt5.QtCore import QUrl, QObject, pyqtProperty

from UM.View.Renderer import Renderer
from UM.PluginObject import PluginObject

import UM.Application

if TYPE_CHECKING:
    from UM.Event import Event
    from UM.Controller import Controller
    from UM.Event import Event


class View(QObject, PluginObject):
    """Abstract base class for view objects."""
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._renderer = None  # type: Optional[Renderer]
        self._controller = UM.Application.Application.getInstance().getController()  # type: Controller
        self._components = {}  # type: Dict[str, QUrl]

    @pyqtProperty(str, constant = True)
    def name(self) -> str:
        return self.getPluginId()

    def addDisplayComponent(self, name: str, source: Union[str, QUrl]) -> None:
        """Add a QML component that is provided by this View."""
        if type(source) == str:
            source = QUrl.fromLocalFile(source)
        self._components[name] = source

    def getDisplayComponent(self, name: str) -> QUrl:
        """Get a QUrl by name."""
        if name in self._components:
            return self._components[name]
        return QUrl()

    def getController(self) -> "Controller":
        """Get the controller object associated with this View.
        :sa Controller
        """
        return self._controller

    def getRenderer(self) -> Optional["Renderer"]:
        """Get the Renderer instance for this View."""
        return self._renderer

    def setRenderer(self, renderer: Renderer) -> None:
        """Set the renderer object to use with this View.

        :param renderer: :type{Renderer} The renderer to use.
        """
        self._renderer = renderer

    def beginRendering(self) -> None:
        """Begin the rendering process.

        This should queue all the meshes that should be rendered.
        """
        pass

    def endRendering(self) -> None:
        """Perform any steps needed when ending the rendering process.

        If there is any cleanup or other tasks that need to be performed
        after rendering this method should be used.
        """
        pass

    def event(self, event: "Event") -> bool:
        return False
