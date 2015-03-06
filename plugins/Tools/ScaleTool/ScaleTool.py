from UM.Tool import Tool
from UM.Event import Event
from UM.Application import Application
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection

from . import ScaleToolHandle

class ScaleTool(Tool):
    def __init__(self):
        super().__init__()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = ScaleToolHandle.ScaleToolHandle()

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            self._handle.setParent(self.getController().getScene().getRoot())
            self._handle.setPosition(Selection.getSelectedObject(0).getGlobalPosition())

        if event.type == Event.MouseMoveEvent:
            axis = self._renderer.getIdAtCoordinate(event.x, event.y)
            if axis and ToolHandle.isAxis(axis):
                self._handle.setActiveAxis(axis)
            else:
                self._handle.setActiveAxis(None)

        if event.type == Event.ToolDeactivateEvent:
            self._handle.setParent(None)
