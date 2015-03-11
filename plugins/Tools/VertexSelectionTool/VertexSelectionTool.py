from UM.Event import MouseEvent
from UM.Tool import Tool
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer
from UM.Scene.Selection import Selection
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

from PyQt5.QtGui import qAlpha, qRed, qGreen, qBlue

class VertexSelectionTool(Tool):
    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()


    def event(self, event):
        if event.type == MouseEvent.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            pixel_color = self._renderer.getSelectionColorAtCoordinate(event.x,event.y)
            if pixel_color:
                if pixel_color.a:
                    print("cloud index" ,  255 - pixel_color.a*255)
                    index  = int(255 - pixel_color.a*255)
                    targeted_node = Application.getInstance().getCloudNodeByIndex(index)
                    #Pixel colors are encoded in (r,g,b) with r being least significant and b being most.
                    pixel_index = int(pixel_color.r *255) + (int(pixel_color.g * 255) << 8) + (int(pixel_color.b * 255) << 16)
                    print("pixel index", pixel_index)
                    Selection.add(targeted_node)
                
