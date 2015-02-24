from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Mesh.MeshData import MeshData
import struct
import time
from UM.Application import Application
from UM.Scene.PointCloudNode import PointCloudNode
from UM.Scene.SceneNode import SceneNode
from PyQt5.QtGui import QImage
from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger

import numpy

from . import ultiscantastic_pb2
from . import ProcessMeshJob

## Class that is responsible for listening to the backend.
class ScannerEngineBackend(Backend, SignalEmitter):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        
        self._message_handlers[ultiscantastic_pb2.PointCloudPointNormal] = self._onPointCloudMessage
        self._message_handlers[ultiscantastic_pb2.ProgressUpdate] = self._onProgressUpdateMessage
        self._message_handlers[ultiscantastic_pb2.Image] = self._onImageMessage
        self._message_handlers[ultiscantastic_pb2.StatusMessage] = self._onStatusMessage
        self._message_handlers[ultiscantastic_pb2.Mesh] = self._onMeshMessage
        self._latest_camera_image = QImage(1, 1, QImage.Format_RGB888)
        self._settings = None
        Application.getInstance().activeMachineChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()
    
    def _onActiveMachineChanged(self):
        self._settings = Application.getInstance().getActiveMachine()
        if self._settings:
            self._settings.settingChanged.connect(self._onSettingChanged)
    
    def _onSettingChanged(self, setting):
        print("setting changed ", setting.getKey())
        self.sendSetting(setting)
    
    def _onStatusMessage(self, message):
        if message.status == ultiscantastic_pb2.StatusMessage.OBJECT_NOT_FOUND:
            self.StatusMessage.emit("Object")
    
    StatusMessage = Signal()
    
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
        self._socket.registerMessageType(7, ultiscantastic_pb2.StatusMessage)
        self._socket.registerMessageType(8, ultiscantastic_pb2.PointCloudWithNormals)
        self._socket.registerMessageType(9, ultiscantastic_pb2.RecalculateNormal)
        self._socket.registerMessageType(10, ultiscantastic_pb2.PoissonModelCreation)
        self._socket.registerMessageType(11, ultiscantastic_pb2.StatisticalOutlierRemoval)
        self._socket.registerMessageType(12, ultiscantastic_pb2.Setting)
        self._socket.registerMessageType(13, ultiscantastic_pb2.Mesh)
        
    def startScan(self, type = 0):
        print("starting scan")
        message = ultiscantastic_pb2.StartScan()
        group_node = SceneNode()
        name = "Scan" 
        if type == 0:
            message.type = ultiscantastic_pb2.StartScan.GREY
            name += " grey"
        elif type == 1:
            message.type = ultiscantastic_pb2.StartScan.PHASE
            name += " phase"
        print("added group:" , id(group_node))
        message.id = id(group_node)
        group_node.setName(name)
        operation = AddSceneNodeOperation(group_node,Application.getInstance().getController().getScene().getRoot())
        Application.getInstance().getOperationStack().push(operation)
        self._socket.sendMessage(message)
    
    def removeOutliers(self, node):
        message = ultiscantastic_pb2.StatisticalOutlierRemoval()
        message.cloud.id = id(node)
        message.cloud.vertices = node.getMeshData().getVerticesAsByteArray()
        message.cloud.normals = node.getMeshData().getNormalsAsByteArray()
        message.number_of_neighbours = 10
        message.cutoff_deviation = 0.5
        self._socket.sendMessage(message)
        
    def sendSetting(self, setting):
        message = ultiscantastic_pb2.Setting()
        message.key = setting.getKey()
        message.value = str(setting.getValue())
        type = setting.getType()
        if type == 'int':
            message.type = ultiscantastic_pb2.Setting.INT
        elif type == 'enum':
            message.type = ultiscantastic_pb2.Setting.STRING
        elif type == 'string':
            message.type = ultiscantastic_pb2.Setting.STRING
        elif type == 'float':
            message.type = ultiscantastic_pb2.Setting.FLOAT
        self._socket.sendMessage(message)
    
    def sendPointcloud(self, node):
        message = ultiscantastic_pb2.PointCloudWithNormals()
        message.vertices = node.getMeshData().getVerticesAsByteArray()
        message.normals = node.getMeshData().getNormalsAsByteArray()
        message.id = id(node)
        self._socket.sendMessage(message)
    
    def recalculateNormals(self, node):
        print("Sending recalculate normals message")
        message = ultiscantastic_pb2.RecalculateNormal()
        message.cloud.vertices = node.getMeshData().getVerticesAsByteArray()
        message.cloud.normals = node.getMeshData().getNormalsAsByteArray()
        message.cloud.id = id(node)
        message.view_point.x = 0
        message.view_point.y = 0
        message.view_point.z = 0
        message.radius = 2.5
        message.id = id(node)
        self._socket.sendMessage(message)
    
    def poissonModelCreation(self, clouds):
        message = ultiscantastic_pb2.PoissonModelCreation()
        message.depth = 8
        message.num_samples_per_node = 1
        message.iso_divide = 8;
        
        for cloud in clouds:
            cloud_message = ultiscantastic_pb2.PointCloudWithNormals()
            cloud_message.vertices = cloud.getVerticesAsByteArray()
            cloud_message.normals = cloud.getNormalsAsByteArray()
            cloud_message.id = 0
            message.clouds.extend([cloud_message])
        
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
        #TODO: For debug purposes this is easier, but it should be moved to a job.
        Logger.log('d', "Recieved point cloud")
        app = Application.getInstance()
        recieved_mesh = MeshData()
        for vert in self._convertBytesToVerticeWithNormalsListPCL(message.data):
            recieved_mesh.addVertexWithNormal(vert[0],vert[1],vert[2],vert[3],vert[4],vert[5])
        if not message.inplace:    
            pointcloud_node = PointCloudNode()
            pointcloud_node.setMeshData(recieved_mesh)    
            for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                if int(message.id) == int(id(node)): #found the node where this scan needs to be added to.
                    pointcloud_node.setName(node.getName() + " "+ str(len(node.getChildren())))
                    pointcloud_node.setParent(node) 
                    return
            pointcloud_node.setParent(Application.getInstance().getController().getScene().getRoot()) #Group is deleted?
            print("Unable to find group node with id", message.id)
        else:
            for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                if int(message.id) == int(id(node)): #found the node where this scan needs to be added to.
                    print("found node, adding")
                    node.setMeshData(recieved_mesh) #Overide the mesh data
        #node = PointCloudNode(group_node)
        #node.setMeshData(recieved_mesh)
        #node.setName(group_node.getName() + " - scan")
        #operation = AddSceneNodeOperation(group_node,app.getController().getScene().getRoot())
        #app.getOperationStack().push(operation)
        
        #if not self._do_once:
        #    self._do_once = True
        #    self.poissonModelCreation([recieved_mesh])
    
       
    
    def _onMeshMessage(self,message):
        Logger.log('d', "Recieved Mesh")
        job = ProcessMeshJob.ProcessMeshJob(message)
        job.start()
            
    
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

    '''def _addPointCloudWithNormals(self, data):
        app = Application.getInstance()
        recieved_mesh = MeshData()
        for vert in self._convertBytesToVerticeWithNormalsListPCL(data):
            recieved_mesh.addVertexWithNormal(vert[0],vert[1],vert[2],vert[3],vert[4],vert[5])
        node = PointCloudNode(app.getController().getScene().getRoot())
        node.setMeshData(recieved_mesh)
        operation = AddSceneNodeOperation(node,app.getController().getScene().getRoot())
        app.getOperationStack().push(operation)'''
    
    # Set the step of the process (scanning, calibration, etc)
    def setProcessStep(self, step): 
        if step >=3 and step <= 7:
            message = ultiscantastic_pb2.setCalibrationStep()
            if step == 3:
                message.step = ultiscantastic_pb2.setCalibrationStep.BOARD
            elif step == 4:
                message.step = ultiscantastic_pb2.setCalibrationStep.PROJECTOR_FOCUS
            elif step == 5:
                message.step = ultiscantastic_pb2.setCalibrationStep.CAMERA_FOCUS
            elif step == 6:
                message.step = ultiscantastic_pb2.setCalibrationStep.CAMERA_EXPOSURE
            elif step == 7:
                message.step = ultiscantastic_pb2.setCalibrationStep.COMPUTE
        else:
            if step == 10:
                self.startScan()
                return
            else:
                return

        self._socket.sendMessage(message)
    
    ## Convert byte array using pcl::pointNormal type
    def _convertBytesToVerticeWithNormalsListPCL(self,data):
        result = []
        derp = struct.unpack('ffffffffffff',data[0:48])
        if not (len(data) % 48):
            if data is not None:
                for index in range(0,int(len(data) / 48)): #For each 48 bits (12 floats)
                    #PCL sends; x,y,z,1.0,n_x,n_y,n_z,0.0,curvatureX,curvatureY,curvatureZ,0)
                    decoded_data = struct.unpack('ffffffffffff',data[index*48:index*48+48])
                    result.append((decoded_data[0],decoded_data[1],decoded_data[2],decoded_data[4],decoded_data[5],decoded_data[6]))
                return result
        else:
            Logger.log('e', "Data length was incorrect for requested type")
            return None