from UM.Job import Job
from UM.Application import Application

##  A Job subclass that performs mesh loading.
#
#   The result of this Job is a MeshData object.
class LoadMeshJob(Job):
    def __init__(self, node, filename):
        super().__init__("Loading mesh {0}".format(filename))
        self._filename = filename
        self._handler = Application.getInstance().getMeshFileHandler()
        self._device = Application.getInstance().getStorageDevice('local')
        self._node = node

    def run(self):
        self.setResult(self._handler.read(self._filename, self._device))

    def getNode(self):
        return self._node
