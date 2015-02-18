from UM.Job import Job
from UM.Scene.SceneNode import SceneNode
from UM.Application import Application
from UM.Mesh.MeshData import MeshData
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
import numpy
import struct

class ProcessPointcloudJob(Job):
    def __init__(self, message):
        super().__init__(description = 'Processing recieved cloud')
        self._message = message

    def run(self):
        pass