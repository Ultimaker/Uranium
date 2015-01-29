from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Mesh.MeshData import MeshData
import struct
import time
from UM.Application import Application
from UM.Scene.PointCloudNode import PointCloudNode
from PyQt5.QtGui import QImage
from UM.Signal import Signal, SignalEmitter

import numpy

from . import ultiscantastic_pb2

## Class that is responsible for listening to the backend.
class ScannerEngineBackend(Backend, SignalEmitter):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        
        self._message_handlers[ultiscantastic_pb2.PointCloudPointNormal] = self._onPointCloudMessage
        self._message_handlers[ultiscantastic_pb2.ProgressUpdate] = self._onProgressUpdateMessage
        self._message_handlers[ultiscantastic_pb2.Image] = self._onImageMessage
        self._message_handlers[ultiscantastic_pb2.CalibrationProblem] = self._onCalibrationProblemMessage
        
        
        self._latest_camera_image = QImage(1, 1, QImage.Format_RGB888)
        '''data = b'' 
        data += bytes( [255] )
        data += bytes( [0] )
        data += bytes( [255] )
        w = 1
        h = 1
        image = QImage(data, w, h, QImage.Format_RGB32)
        image.save("herpaderp.png")'''
    
    def _onCalibrationProblemMessage(self, message):
        if message.type == ultiscantastic_pb2.CalibrationProblem.OBJECT_NOT_FOUND:
            self.calibrationProblemMessage.emit("Object")
    
    calibrationProblemMessage = Signal()
    
    def getLatestCameraImage(self):
        return self._latest_camera_image
    
    def _createSocket(self):
        super()._createSocket()
        self._socket.registerMessageType(1, ultiscantastic_pb2.PointCloudPointNormal)
        self._socket.registerMessageType(2, ultiscantastic_pb2.StartScan)
        self._socket.registerMessageType(3, ultiscantastic_pb2.ProgressUpdate)
        self._socket.registerMessageType(4, ultiscantastic_pb2.StartCalibration)
        self._socket.registerMessageType(5, ultiscantastic_pb2.Image)
        self._socket.registerMessageType(6, ultiscantastic_pb2.setCalibrationStep)
        self._socket.registerMessageType(7, ultiscantastic_pb2.CalibrationProblem)
        self._socket.registerMessageType(8, ultiscantastic_pb2.PointCloudWithNormals)
        
    def startScan(self, type = 0):
        message = ultiscantastic_pb2.StartScan()
        if type == 0:
            message.type = ultiscantastic_pb2.StartScan.GREY
        elif type == 1:
            message.type = ultiscantastic_pb2.StartScan.PHASE
        self._socket.sendMessage(message)
    
    
    def sendPointcloud(self, mesh_data):
        message = ultiscantastic_pb2.PointCloudWithNormals()
        message.vertices = mesh_data.getVerticesAsByteArray()
        message.normals = mesh_data.getNormalsAsByteArray()
        message.id = 0
        self._socket.sendMessage(message)
        
    def startCalibration(self, type = 0):
        message = ultiscantastic_pb2.StartCalibration()
        if type == 0:
            message.type = ultiscantastic_pb2.StartCalibration.CORNER
        elif type == 1:
            message.type = ultiscantastic_pb2.StartCalibration.BOARD
        print("Sending calibration message")
        self._socket.sendMessage(message)
        
    def getEngineCommand(self):
        return [Preferences.getPreference("BackendLocation"), '-p', str(self._port)]
    
    def _onPointCloudMessage(self, message):
        app = Application.getInstance()
        recieved_mesh = MeshData()
        for vert in self._convertBytesToVerticeWithNormalsListPCL(message.data):
            recieved_mesh.addVertexWithNormal(vert[0],vert[1],vert[2],vert[3],vert[4],vert[5])
        node = PointCloudNode(app.getController().getScene().getRoot())
        node.setMeshData(recieved_mesh)
        operation = AddSceneNodeOperation(node,app.getController().getScene().getRoot())
        app.getOperationStack().push(operation)
        self.sendPointcloud(recieved_mesh) #DEBUG STUFFS
        print("Recieved pointcloud")
    
    # Handle image sent by engine    
    def _onImageMessage(self, message):
        if message.type == ultiscantastic_pb2.Image.RGB:
            image = QImage(message.data, message.width, message.height, QImage.Format_RGB888)
            
        elif message.type == ultiscantastic_pb2.Image.MONO:
            data = numpy.fromstring(message.data,numpy.uint8)
            resized_data = numpy.resize(data,(message.width,message.height))
            multi_channel = numpy.dstack((resized_data,resized_data,resized_data))
            image = QImage(multi_channel.tostring(),message.width,message.height,QImage.Format_RGB888)
        
        self.newCameraImage.emit()
        self._latest_camera_image = image   
    
    newCameraImage = Signal()
    
    def _onProgressUpdateMessage(self, message):
        self.processingProgress.emit(message.amount)

    def _addPointCloudWithNormals(self, data):
        app = Application.getInstance()
        recieved_mesh = MeshData()
        for vert in self._convertBytesToVerticeWithNormalsListPCL(data):
            recieved_mesh.addVertexWithNormal(vert[0],vert[1],vert[2],vert[3],vert[4],vert[5])
        node = PointCloudNode(app.getController().getScene().getRoot())
        node.setMeshData(recieved_mesh)
        operation = AddSceneNodeOperation(node,app.getController().getScene().getRoot())
        app.getOperationStack().push(operation)
    
    def setCalibrationStep(self, key):
        message = ultiscantastic_pb2.setCalibrationStep()
        if key == "board":
            message.step = ultiscantastic_pb2.setCalibrationStep.BOARD
        elif key == "projector_focus":
            message.step = ultiscantastic_pb2.setCalibrationStep.PROJECTOR_FOCUS
        elif key == "camera_focus":
            message.step = ultiscantastic_pb2.setCalibrationStep.CAMERA_FOCUS
        elif key == "camera_exposure":
            message.step = ultiscantastic_pb2.setCalibrationStep.CAMERA_EXPOSURE
        elif key == "calibrate":
            message.step = ultiscantastic_pb2.setCalibrationStep.COMPUTE
        self._socket.sendMessage(message)
    
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