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
        self._coud_index_dict = {}
    
    def event(self, event):
        if event.type == Event.MousePressEvent and MouseEvent.LeftButton in event.buttons:
            self._pressed = True
            self._coud_index_dict = {}
        if event.type == Event.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            self._pressed = False
            
        
        if event.type == Event.MouseMoveEvent:
            self._coud_index_dict = {}
            camera = self.getController().getScene().getActiveCamera()
            self._handle.setParent(camera)
            field_of_view = camera.getViewportWidth() / camera.getViewportHeight()
            fov_tan = math.tan(math.radians(field_of_view) / 2.)
            self._handle.setPosition(Vector(fov_tan * event.x * (0.5 * camera.getViewportWidth()) , fov_tan * -event.y * (0.5 * camera.getViewportHeight()),-10))
            
            if self._pressed:
                pixel_colors = self._renderer.getSelectionColorAtCoorindateRadius(event.x,event.y,15)
                if pixel_colors:
                    for pixel_color in pixel_colors:
                        if pixel_color.a:
                            cloud_index  = int(255 - pixel_color.a * 255)
                            #targeted_node = Application.getInstance().getCloudNodeByIndex(index)
                            #Pixel colors are encoded in (r,g,b) with r being least significant and b being most.
                            pixel_index = int(pixel_color.r * 255) + (int(pixel_color.g * 255) << 8) + (int(pixel_color.b * 255) << 16)
                            if cloud_index not in self._coud_index_dict:
                                self._coud_index_dict[cloud_index] = [pixel_index]
                            else:
                                self._coud_index_dict[cloud_index].extend([pixel_index])
                
            self._scene.acquireLock()
            for entry in self._coud_index_dict:
                Application.getInstance().getCloudNodeByIndex(entry).getMeshData().removeVertex(self._coud_index_dict[entry])
            self._scene.releaseLock()
            self._renderer.resetSelectionImage() #Deletes the selection image, so a new set will only be selected if the image is rerendered.
                    #print()
                #print(pixel_dict)
        
                
