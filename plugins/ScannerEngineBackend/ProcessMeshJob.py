from UM.Job import Job
from UM.Scene.SceneNode import SceneNode
from UM.Application import Application
from UM.Mesh.MeshData import MeshData
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
import numpy
import struct

class ProcessMeshJob(Job):
    def __init__(self, message):
        super().__init__(description = 'Processing recieved mesh')
        self._message = message

    def run(self):
        recieved_mesh = MeshData()
        verts , indices = self._convertBytesToMesh(self._message.vertices,self._message.indices)
        recieved_mesh.addVertices(verts)
        recieved_mesh.addIndices(indices)
        recieved_mesh.calculateNormals() #We didn't get normals, calculate them for sake of visualisation.
        node = SceneNode()
        node.setMeshData(recieved_mesh)
        operation = AddSceneNodeOperation(node,Application.getInstance().getController().getScene().getRoot())
        Application.getInstance().getOperationStack().push(operation)
    
    def _convertBytesToMesh(self, verts_data, indices_data):
        verts = None
        indices = None
        verts = numpy.fromstring(verts_data,dtype=numpy.float32)
        verts = verts.reshape(-1,4) # Reshape list to pairs of 4 (as they are sent as homogenous data)
        verts =  verts[:,0:3] # Cut off the homogenous coord.
        indices = numpy.fromstring(indices_data,dtype=numpy.uint32)
        indices = indices.reshape(-1,3)
        return (verts,indices)   
