# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Decorators import deprecated


##  A Job subclass that performs mesh writing.
#
#   The result of this Job is a MeshData object.
@deprecated("Use the more generic WriteJob", "2.4")
class WriteMeshJob(WriteFileJob):
    ##  Creates a new job for writing meshes.
    #
    #   \param writer The file writer to use, with the correct MIME type.
    #   \param stream The output stream to write to.
    #   \param nodes A collection of nodes to write to the stream.
    #   \param mode Additional information to send to the writer, such as whether to
    #   write in binary format or in ASCII format.
    def __init__(self, writer, stream, nodes, mode):
        super().__init__(writer, stream, nodes, mode)
