# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Decorators import deprecated


##  A Job subclass that performs mesh writing.
#
#   The result of this Job is a MeshData object.
@deprecated("Use the more generic WriteJob", "2.4")
class WriteMeshJob(Job):
    ##  Creates a new job for writing meshes.
    #
    #   \param writer The file writer to use, with the correct MIME type.
    #   \param stream The output stream to write to.
    #   \param nodes A collection of nodes to write to the stream.
    #   \param mode Additional information to send to the writer, such as whether to
    #   write in binary format or in ASCII format.
    def __init__(self, writer, stream, nodes, mode):
        super().__init__()
        self._stream = stream
        self._writer = writer
        self._nodes = nodes
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
        self.setResult(self._writer.write(self._stream, self._nodes, self._mode))

