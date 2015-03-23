from UM.Event import MouseEvent
from UM.Tool import Tool
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Math.Ray import Ray
from UM.Math.Plane import Plane
from UM.Event import Event
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer
from UM.Scene.Selection import Selection
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from . import VertexEraseToolHandle
import math
import numpy

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
            
            ## Ray castin from camera. Not using camera function as we need it in local space, not global.
            field_of_view = camera.getViewportWidth() / camera.getViewportHeight()
            fov_tan = math.tan(math.radians(field_of_view) / 2.)
            
            invp = numpy.linalg.inv(camera.getProjectionMatrix().getData().copy())
            invv = Matrix().getData()

            near = numpy.array([event.x, -event.y, -1.0, 1.0], dtype=numpy.float32)
            near = numpy.dot(invp, near)
            near = numpy.dot(invv, near)
            near = near[0:3] / near[3]

            far = numpy.array([event.x, -event.y, 1.0, 1.0], dtype = numpy.float32)
            far = numpy.dot(invp, far)
            far = numpy.dot(invv, far)
            far = far[0:3] / far[3]

            dir = far - near
            dir /= numpy.linalg.norm(dir)   
            #Plane on which the circle lies.
            plane = Plane(Vector(0, 0, 1),100)
            ray = Ray(Vector(0,0,0), Vector(dir[0],dir[1],dir[2]))
            intersection_distance = plane.intersectsRay(ray) #Intersect
            self._handle.setPosition(ray.getPointAlongRay(intersection_distance).flip()) #Use (flipped) intersection.
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
        
                
