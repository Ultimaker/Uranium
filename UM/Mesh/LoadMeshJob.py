from UM.Job import Job
from UM.Application import Application

import os.path

##  A Job subclass that performs mesh loading.
#
#   The result of this Job is a MeshData object.
class LoadMeshJob(Job):
    def __init__(self, filename):
        super().__init__(description = "Loading mesh {0}".format(os.path.basename(filename)), visible = True)
        self._filename = filename
        self._handler = Application.getInstance().getMeshFileHandler()
        self._device = Application.getInstance().getStorageDevice('local')

    def run(self):
        self.setResult(self._handler.read(self._filename, self._device))
