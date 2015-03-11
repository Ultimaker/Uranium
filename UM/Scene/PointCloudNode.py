from . import SceneNode
from UM.View.Renderer import Renderer
from UM.Application import Application
import numpy
class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = "Pointcloud"
        self._selectable = True
        Application.getInstance().addCloudNode(self)
        

    def render(self, renderer):
        if self.getMeshData() and self.isVisible():
            renderer.queueNode(self, mode = Renderer.RenderPoints)
            return True
    
    ##  \brief Set the mesh of this node/object
    #   \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
        id = Application.getInstance().getCloudNodeIndex(self)
        
        # Create a unique color for each vert. First 3 uint 8  represent index in this cloud, final uint8 gives cloud ID.
        vertice_indices = numpy.arange(mesh_data.getVertexCount(), dtype = numpy.int32)
        cloud_indices = numpy.empty(mesh_data.getVertexCount(),dtype = numpy.int32)
        cloud_indices.fill(id)
        cloud_indices  = numpy.left_shift(cloud_indices,24) # shift 24 bits.
        combined_clouds = numpy.add(cloud_indices,vertice_indices)
        data = numpy.fromstring(combined_clouds.tostring(),numpy.uint8)
        colors  = numpy.resize(data,(mesh_data.getVertexCount() , 4))
        self._mesh_data.setColors(colors)
        self._resetAABB()
        self.meshDataChanged.emit(self)