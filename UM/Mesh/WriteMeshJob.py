from UM.Job import Job
from UM.Application import Application
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

import os.path

##  A Job subclass that performs mesh loading.
#
#   The result of this Job is a MeshData object.
class WriteMeshJob(Job):
    def __init__(self, filename, mesh):
        super().__init__(description = "Saving to file {0}".format(os.path.basename(filename)), visible = True)
        self._filename = filename
        self._handler = Application.getInstance().getMeshFileHandler()
        self._device = Application.getInstance().getStorageDevice('LocalFileStorage')
        self._mesh = mesh

    def getFileName(self):
        return self._filename

    def run(self):
        self.setResult(self._handler.write(self._filename, self._device, self._mesh))
