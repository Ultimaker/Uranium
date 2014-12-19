from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Mesh.MeshData import MeshData
import struct
import time
from UM.Application import Application
from UM.Scene.PointCloudNode import PointCloudNode


class ScannerEngineBackend(Backend):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        time.sleep(2)
        self._socket_thread.sendCommand(1) # Debug stuff
        
        
        self.interpretData(self.recieveData())


    ## Convert byte array using pcl::pointNormal type
    def convertBytesToVerticeWithNormalsListPCL(self,data):
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
        
    ##  Interpret a byte stream as a command. 
    #   Based on the command_id (the fist 4 bits of the message) a different action will be taken.
    def interpretData(self, data):
        app = Application.getInstance()
        data_id = struct.unpack('i', data[0:4])[0] #The data ID tells us how to handle the data.
        if data_id == 2:#Recieved pointcloud without normals
            recieved_mesh = MeshData()
            for vert in self.convertBytesToVerticeList(data[4:len(data)]):
                recieved_mesh.addVertex(vert[0],vert[1],vert[2])
            node = PointCloudNode(app.getController().getScene().getRoot())
            node.setMeshData(recieved_mesh)
            operation = AddSceneNodeOperation(node,app.getController().getScene().getRoot())
            app.getOperationStack().push(operation)
            #print(self.convertBytesToVerticeList(data[4:len(data)]))
        if data_id == 3:#recieved pointcloud with normals
            recieved_mesh = MeshData()
            print("recieved %s points" %(len(data)))
            for vert in self.convertBytesToVerticeWithNormalsListPCL(data[4:len(data)]):
                recieved_mesh.addVertexWithNormal(vert[0],vert[1],vert[2],vert[3],vert[4],vert[5])
            node = PointCloudNode(app.getController().getScene().getRoot())
            node.setMeshData(recieved_mesh)
            operation = AddSceneNodeOperation(node,app.getController().getScene().getRoot())
            app.getOperationStack().push(operation)
        