from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector
from UM.ColorGenerator import ColorGenerator
from UM.Math.Color import Color

class PointCloudAlignToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._mesh_builder = MeshBuilder()
        self._line_builder = MeshBuilder()
        self._auto_scale = False
        self._color_generator = ColorGenerator()
        self._color_index = 0
        self._used_colors = [] # We need to keep local references in order to trick the garabage collector
        self._latest_point = None
        #self._mesh_builder.addCube(width= 25, height = 25, depth = 25, center = Vector(50,50,50), color =ToolHandle.XAxisColor)
        #self.setSolidMesh(self._mesh_builder.getData())
    
    #def _populateColorList(self):
        
    
    def addSelectedPoint1(self, point):
        self._latest_point = point
        col = self._color_generator.getColor(self._color_index) 
        self._used_colors.append(Color(col[0],col[1],col[2],1.0))
        self._mesh_builder.addCube(width= 25, height = 25, depth = 25, center = Vector(point[0],point[1],point[2]), color = self._used_colors[self._color_index])
        self._mesh_builder.getData().dataChanged.emit()
        self.setSolidMesh(self._mesh_builder.getData())

    def addSelectedPoint2(self, point):
        self._mesh_builder.addCube(width= 25, height = 25, depth = 25, center = Vector(point[0],point[1],point[2]), color = self._used_colors[self._color_index])
        self._mesh_builder.getData().dataChanged.emit()
        
        self._line_builder.addLine(Vector(self._latest_point[0],self._latest_point[1],self._latest_point[2]),Vector(point[0],point[1],point[2]), color = self._used_colors[self._color_index])
        self._line_builder.getData().dataChanged.emit()
        self.setLineMesh(self._line_builder.getData())
        self.setSolidMesh(self._mesh_builder.getData())
        
        self._color_index += 1