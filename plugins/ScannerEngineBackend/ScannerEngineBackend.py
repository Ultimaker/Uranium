from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
from UM.Operations.AddMeshOperation import AddMeshOperation
from UM.Mesh.MeshData import MeshData
import struct
import time
from UM.Application import Application


class ScannerEngineBackend(Backend):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        time.sleep(2)
        self._socket_thread.sendCommand(1) # Debug stuff
        
        
        self.interpretData(self.recieveData())
        

    def interpretData(self, data):
        app = Application.getInstance()
        #op = AddMeshOperation(app.getMeshFileHandler().read(file_name.toLocalFile(), app.getStorageDevice('local')), self._controller.getScene().getRoot())
        #app.getOperationStack().push(op)
        data_id = struct.unpack('i', data[0:4])[0] #The data ID tells us how to handle the data.
        if data_id == 2:#Recieved pointcloud without normals
            recieved_mesh = MeshData()
            for vert in self.convertBytesToVerticeList(data[4:len(data)]):
                recieved_mesh.addVertex(vert[0],vert[1],vert[2])
            operation = AddMeshOperation(recieved_mesh,app.getController().getScene().getRoot())
            app.getOperationStack().push(operation)
            #print(self.convertBytesToVerticeList(data[4:len(data)]))
        if data_id == 3:#recieved pointcloud with normals
            print(self.convertBytesToVerticeWithNormalsList(data[4:len(data)]))
        