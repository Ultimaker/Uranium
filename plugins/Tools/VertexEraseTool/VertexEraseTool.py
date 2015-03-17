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
            coud_index_dict = {}
            if self._pressed:
                pixel_colors = self._renderer.getSelectionColorAtCoorindateRadius(event.x,event.y,5)
                if pixel_colors:
                    for pixel_color in pixel_colors:
                        if pixel_color.a:
                            index  = int(255 - pixel_color.a*255)
                            #targeted_node = Application.getInstance().getCloudNodeByIndex(index)
                            #Pixel colors are encoded in (r,g,b) with r being least significant and b being most.
                            pixel_index = int(pixel_color.r *255) + (int(pixel_color.g * 255) << 8) + (int(pixel_color.b * 255) << 16)
                            if index not in coud_index_dict:
                                coud_index_dict[index] = [pixel_index]
                            else:
                                if pixel_index not in coud_index_dict[index]:
                                    coud_index_dict[index].extend([pixel_index])
                            #targeted_node.getMeshData().removeVertex(pixel_index)
                
                self._scene.acquireLock()
                for entry in coud_index_dict:
                    #print("index" , entry)
                    #print("node" , Application.getInstance().getCloudNodeByIndex(entry))
                    
                    Application.getInstance().getCloudNodeByIndex(entry).getMeshData().removeVertex(coud_index_dict[entry])
                self._scene.releaseLock()    
                    #print()
                #print(pixel_dict)
        
                
