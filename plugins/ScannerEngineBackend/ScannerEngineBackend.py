from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Mesh.MeshData import MeshData
import struct
import time
from UM.Application import Application
from UM.Scene.PointCloudNode import PointCloudNode

from . import ultiscantastic_pb2

## Class that is responsible for listening to the backend.
class ScannerEngineBackend(Backend):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        
        self._socket.registerMessageType(1, ultiscantastic_pb2.PointCloudWithNormals)
        self._socket.registerMessageType(2, ultiscantastic_pb2.StartScan)
        self._socket.registerMessageType(3, ultiscantastic_pb2.ProgressUpdate)

        self._message_handlers[ultiscantastic_pb2.PointCloudWithNormals] = self._onPointCloudWithNormalsMessage
        self._message_handlers[ultiscantastic_pb2.ProgressUpdate] = self._onProgressUpdateMessage
        
        print(" HDHAHHA" ,ultiscantastic_pb2.StartScan.PHASE)
        
        message = ultiscantastic_pb2.StartScan()
        message.type = ultiscantastic_pb2.StartScan.GREY
        self.startEngine()
        time.sleep(1)
        self._socket.sendMessage(message)
        time.sleep(1)
        self._socket.sendMessage(message)
        
    def getEngineCommand(self):
        return [Preferences.getPreference("BackendLocation"), '-p', "49674"]
    
    def _onPointCloudWithNormalsMessage(self, message):
        print("Recieved pointcloud")
    
    def _onProgressUpdateMessage(self,message):
        print("Progress update message " )

    def _addPointCloudWithNormals(self, data):
        app = Application.getInstance()
        recieved_mesh = MeshData()
        for vert in self._convertBytesToVerticeWithNormalsListPCL(data):
            recieved_mesh.addVertexWithNormal(vert[0],vert[1],vert[2],vert[3],vert[4],vert[5])
        node = PointCloudNode(app.getController().getScene().getRoot())
        node.setMeshData(recieved_mesh)
        operation = AddSceneNodeOperation(node,app.getController().getScene().getRoot())
        app.getOperationStack().push(operation)
    
    ## Convert byte array using pcl::pointNormal type
    def _convertBytesToVerticeWithNormalsListPCL(self,data):
        result = []
        derp = struct.unpack('ffffffffffff',data[0:48])
        if not (len(data) % 48):
            if data is not None:
                for index in range(0,int(len(data) / 48)): #For each 24 bits (12 floats)
                    #PCL sends; x,y,z,1.0,n_x,n_y,n_z,0.0,curvatureX,curvatureY,curvatureZ,0)
                    decoded_data = struct.unpack('ffffffffffff',data[index*48:index*48+48])
                    result.append((decoded_data[0],decoded_data[1],decoded_data[2],decoded_data[4],decoded_data[5],decoded_data[6]))
                return result
        else:
            Logger.log('e', "Data length was incorrect for requested type")
            return None