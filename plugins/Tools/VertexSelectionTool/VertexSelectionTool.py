from UM.Event import MouseEvent
from UM.Tool import Tool
from UM.Math.Vector import Vector
from UM.Event import Event
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer
from UM.Scene.Selection import Selection
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from . import VertexSelectionToolHandle

from PyQt5.QtGui import qAlpha, qRed, qGreen, qBlue

class VertexSelectionTool(Tool):
    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = VertexSelectionToolHandle.VertexSelectionToolHandle()
        self._selected_point_coordinates = None


    def event(self, event):
        if event.type == MouseEvent.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            pixel_color = self._renderer.getSelectionColorAtCoordinate(event.x,event.y)
            if pixel_color:
                if pixel_color.a:
                    index  = int(255 - pixel_color.a*255)
                    targeted_node = Application.getInstance().getCloudNodeByIndex(index)
                    #Pixel colors are encoded in (r,g,b) with r being least significant and b being most.
                    pixel_index = int(pixel_color.r *255) + (int(pixel_color.g * 255) << 8) + (int(pixel_color.b * 255) << 16)
                    temp = targeted_node.getMeshData().getVertex(pixel_index)
                    self._selected_point_coordinates = Vector(temp[0],temp[1],temp[2])
                    self._handle.setParent(self.getController().getScene().getRoot())
                    self._handle.setPosition(self._selected_point_coordinates)
                
