# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshWriter import MeshWriter
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector


##  Central class for reading and writing meshes.
# preRead
#   This class is created by Application and handles reading and writing mesh files.
class MeshFileHandler(object):
    def __init__(self):
        super().__init__()
        self._mesh_readers = {}
        self._mesh_writers = {}

        PluginRegistry.addType("mesh_writer", self.addWriter)
        PluginRegistry.addType("mesh_reader", self.addReader)

    ##  Find a MeshReader that accepts the given file name.
    #   \param file_name The name of file to load.
    #   \returns MeshReader that accepts the given file name. If no acceptable MeshReader is found None is returned.
    def getReaderForFile(self, file_name):
        for id, reader in self._mesh_readers.items():
            try:
                if reader.acceptsFile(file_name):
                    return reader
            except Exception as e:
                Logger.log("e", str(e))

        return None

    # Try to read the mesh_data from a file using a specified MeshReader.
    # \param reader the MeshReader to read the file with.
    # \param file_name The name of the mesh to load.
    # \param kwargs Keyword arguments.
    #               Possible values are:
    #               - Center: True if the model should be centered around (0,0,0), False if it should be loaded as-is. Defaults to True.
    # \returns MeshData if it was able to read the file, None otherwise.
    def readerRead(self, reader, file_name, **kwargs):
        try:
            results = reader.read(file_name)
            if results is not None:
                if type(results) is not list:
                    results = [results]

                for result in results:
                    if kwargs.get("center", True):
                        # If the result has a mesh and no children it needs to be centered
                        if result.getMeshData() and len(result.getChildren()) == 0:
                            extents = result.getMeshData().getExtents()
                            move_vector = Vector(extents.center.x, extents.center.y, extents.center.z)
                            result.setCenterPosition(move_vector)

                            if result.getMeshData().getExtents(result.getWorldTransformation()).bottom != 0:
                                result.translate(Vector(0, -result.getMeshData().getExtents(result.getWorldTransformation()).bottom, 0))

                        # Move all the meshes of children so that toolhandles are shown in the correct place.
                        for node in result.getChildren():
                            if node.getMeshData():
                                extents = node.getMeshData().getExtents()
                                m = Matrix()
                                m.translate(-extents.center)
                                node.setMeshData(node.getMeshData().getTransformed(m))
                                node.translate(extents.center)
                return results

        except OSError as e:
            Logger.log("e", str(e))

        Logger.log("w", "Unable to read file %s", file_name)
        return None #unable to read

    ##  Get an instance of a mesh writer by ID
    def getWriter(self, writer_id):
        if writer_id not in self._mesh_writers:
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
                    ext = input_type.get("extension", None)
                    if ext:
                        description = input_type.get("description", ext)
                        supported_types[ext] = description

        return supported_types

    def addWriter(self, writer):
        self._mesh_writers[writer.getPluginId()] = writer

    def addReader(self, reader):
        self._mesh_readers[reader.getPluginId()] = reader
