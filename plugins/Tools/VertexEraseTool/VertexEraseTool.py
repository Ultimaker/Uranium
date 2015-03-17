from UM.Event import MouseEvent
from UM.Tool import Tool
from UM.Math.Vector import Vector
from UM.Event import Event
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer
from UM.Scene.Selection import Selection
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from . import VertexEraseToolHandle
import math

from PyQt5.QtGui import qAlpha, qRed, qGreen, qBlue

class VertexEraseTool(Tool):
    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = VertexEraseToolHandle.VertexEraseToolHandle()
        self._pressed = False

    def event(self, event):
        if event.type == Event.MousePressEvent and MouseEvent.LeftButton in event.buttons:
            self._pressed = True
        if event.type == Event.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            self._pressed = False
        
        if event.type == Event.MouseMoveEvent:
            camera = self.getController().getScene().getActiveCamera()
            self._handle.setParent(camera)
            field_of_view = camera.getViewportWidth() / camera.getViewportHeight()
            fov_tan = math.tan(math.radians(field_of_view) / 2.)
            self._handle.setPosition(Vector(fov_tan * event.x * (0.5 * camera.getViewportWidth()) , fov_tan * -event.y * (0.5 * camera.getViewportHeight()),-10))
            if self._pressed:
                pixel_color = self._renderer.getSelectionColorAtCoordinate(event.x,event.y)
                
        
                
