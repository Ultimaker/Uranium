from . import SceneNode
from UM.View.Renderer import Renderer
from UM.Application import Application
from UM.Resources import Resources
from UM.Math.Color import Color
from UM.ColorGenerator import ColorGenerator
import numpy
class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = "Pointcloud"
        self._selectable = True
        Application.getInstance().addCloudNode(self)
        self._material = None
   
   ##   \brief Create new material. 
   #    This uses the 'global' index of the cloud to create a color. The color is selected from a list of 64 colors.
    def createMaterial(self,renderer):
        self._material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, 'default.vert'), Resources.getPath(Resources.ShadersLocation, 'default.frag'))
        self._material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
        cloud_color = ColorGenerator().createColor(Application.getInstance().getCloudNodeIndex(self))
        self._material.setUniformValue("u_diffuseColor", Color(cloud_color[0], cloud_color[1], cloud_color[2], 1.0))
        self._material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
        self._material.setUniformValue("u_shininess", 50.0)
    
    def render(self, renderer):
        if not self._material:
            self.createMaterial(renderer)
        if self.getMeshData() and self.isVisible():
            renderer.queueNode(self, mode = Renderer.RenderPoints, material = self._material)
            return True
    
    ##  \brief Set the mesh of this node/object
    #   \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
        id = Application.getInstance().getCloudNodeIndex(self)
        
        # Create a unique color for each vert. First 3 uint 8  represent index in this cloud, final uint8 gives cloud ID.
        vertice_indices = numpy.arange(mesh_data.getVertexCount(), dtype = numpy.int32)
        cloud_indices = numpy.empty(mesh_data.getVertexCount(),dtype = numpy.int32)
        cloud_indices.fill(255 - id)
        cloud_indices  = numpy.left_shift(cloud_indices,24) # shift 24 bits.
        combined_clouds = numpy.add(cloud_indices,vertice_indices)
        data = numpy.fromstring(combined_clouds.tostring(),numpy.uint8)
    
        
        colors  = numpy.resize(data,(mesh_data.getVertexCount() , 4))
        colors = colors.astype(numpy.float32)
        colors /= 255
        self._mesh_data.setColors(colors)
        self._resetAABB()
        self.meshDataChanged.emit(self)