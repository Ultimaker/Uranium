# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job


##  A Job subclass that performs mesh writing.
#
#   The result of this Job is a MeshData object.
class WriteMeshJob(Job):
    def __init__(self, writer, stream, node, mode):
        super().__init__()
        self._stream = stream
        self._writer = writer
        self._node = node
        self._file_name = ""
        self._mode = mode

    def setFileName(self, name):
        self._file_name = name

    def getFileName(self):
        return self._file_name

    def getStream(self):
        return self._stream

    def run(self):
        Job.yieldThread()
        self.setResult(self._writer.write(self._stream, self._node, self._mode))

