# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshWriter import MeshWriter
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector

##  Central class for reading and writing meshes.
#
#   This class is created by Application and handles reading and writing mesh files.
class MeshFileHandler(object):
    def __init__(self):
        super().__init__()
        self._mesh_readers = {}
        self._mesh_writers = {}

        PluginRegistry.addType("mesh_writer", self.addWriter)
        PluginRegistry.addType("mesh_reader", self.addReader)

    # Try to read the mesh_data from a file. Based on the extension in the file a correct meshreader is selected.
    # \param file_name The name of the mesh to load.
    # \param kwargs Keyword arguments.
    #               Possible values are:
    #               - Center: True if the model should be centered around (0,0,0), False if it should be loaded as-is. Defaults to True.
    # \returns MeshData if it was able to read the file, None otherwise.
    def read(self, file_name, **kwargs):
        try:
            for id, reader in self._mesh_readers.items():
                result = reader.read(file_name)
                if result is not None:
                    if kwargs.get("center", True):
                        # If the result has a mesh and no children it needs to be centered
                        if result.getMeshData() and len(result.getChildren()) == 0:
                            extents = result.getMeshData().getExtents()
                            move_vector = Vector()
                            move_vector.setX(extents.center.x)
                            move_vector.setY(extents.center.y) # Ensure that bottom is on 0 (above plate)
                            move_vector.setZ(extents.center.z)
                            result.setCenterPosition(move_vector)

                            if result.getMeshData().getExtents().bottom != 0:
                               result.translate(Vector(0,-result.getMeshData().getExtents().bottom ,0))

                        # Move all the meshes of children so that toolhandles are shown in the correct place.
                        for node in result.getChildren():
                            if node.getMeshData():
                                extents = node.getMeshData().getExtents()
                                m = Matrix()
                                m.translate(-extents.center)
                                node.setMeshData(node.getMeshData().getTransformed(m))
                                node.translate(extents.center)
                    return result

        except OSError as e:
            Logger.log("e", str(e))

        Logger.log("w", "Unable to read file %s", file_name)
        return None #unable to read

    ##  Get an instance of a mesh writer by ID
    def getWriter(self, writer_id):
        if not writer_id in self._mesh_writers:
            return None

        return self._mesh_writers[writer_id]

    ##  Get a mesh writer object that supports writing the specified mime type
    #
    #   \param mime The mime type that should be supported.
    #   \return A MeshWriter instance or None if no mesh writer supports the specified mime type. If there are multiple
    #           writers that support the specified mime type, the first entry is returned.
    def getWriterByMimeType(self, mime):
        writer_data = PluginRegistry.getInstance().getAllMetaData(filter = {"mesh_writer": {}}, active_only = True)
        for entry in writer_data:
            for output in entry["mesh_writer"].get("output", []):
                if mime == output["mime_type"]:
                    return self._mesh_writers[entry["id"]]

        return None

    ##  Get list of all supported filetypes for writing.
    #   \return List of dicts containing id, extension, description and mime_type for all supported file types.
    def getSupportedFileTypesWrite(self):
        supported_types = []
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"mesh_writer": {}}, active_only = True)
        for entry in meta_data:
            for output in entry["mesh_writer"].get("output", []):
                ext = output.get("extension", "")
                description = output.get("description", ext)
                mime_type = output.get("mime_type", "text/plain")
                mode = output.get("mode", MeshWriter.OutputMode.TextMode)
                supported_types.append({
                    "id": entry["id"],
                    "extension": ext,
                    "description": description,
                    "mime_type": mime_type,
                    "mode": mode
                })
        return supported_types

    # Get list of all supported filetypes for reading.
    # \returns List of strings with all supported filetypes.
    def getSupportedFileTypesRead(self):
        supported_types = {}
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"mesh_reader": {}}, active_only = True)
        for entry in meta_data:
            if "mesh_reader" in entry:
                for input_type in entry["mesh_reader"]:
                    print("INPUT_TYPE: ", str(input_type))
                    ext = input_type.get("extension", None)
                    if ext:
                        description = input_type.get("description", ext)
                        supported_types[ext] = description

        return supported_types

    def addWriter(self, writer):
        self._mesh_writers[writer.getPluginId()] = writer

    def addReader(self, reader):
        self._mesh_readers[reader.getPluginId()] = reader
