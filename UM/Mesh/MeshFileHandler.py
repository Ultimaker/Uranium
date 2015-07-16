# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

from UM.Math.Matrix import Matrix

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
    # \param storage_device The StorageDevice where the mesh can be found.
    # \param kwargs Keyword arguments.
    #               Possible values are:
    #               - Center: True if the model should be centered around (0,0,0), False if it should be loaded as-is. Defaults to True.
    # \returns MeshData if it was able to read the file, None otherwise.
    def read(self, file_name, storage_device, **kwargs):
        try:
            for id, reader in self._mesh_readers.items():
                result = reader.read(file_name, storage_device)
                if(result is not None):
                    if kwargs.get("center", True):
                        # Center the mesh
                        extents = result.getExtents()
                        m = Matrix()
                        m.setByTranslation(-extents.center)
                        result = result.getTransformed(m)

                    result.setFileName(file_name)
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
            mime_types = entry["mesh_writer"].get("mime_types", [])
            if mime in mime_types:
                return self._mesh_writers[entry["id"]]

        return None

    # Get list of all supported filetypes for writing.
    # \returns Dict of extension, description with all supported filetypes.
    def getSupportedFileTypesWrite(self):
        supported_types = {}
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"type": "mesh_writer"}, active_only = True)
        for entry in meta_data:
            if "mesh_writer" in entry:
                ext = entry["mesh_writer"].get("extension", None)
                description = entry["mesh_writer"].get("description", ext)
                if ext:
                    supported_types[ext] = description
        return supported_types
    
    # Get list of all supported filetypes for reading.
    # \returns List of strings with all supported filetypes.
    def getSupportedFileTypesRead(self):
        supported_types = {}
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"type": "mesh_reader"}, active_only = True)
        for entry in meta_data:
            if "mesh_reader" in entry:
                ext = entry["mesh_reader"].get("extension", None)
                description = entry["mesh_reader"].get("description", ext)
                if ext:
                    supported_types[ext] = description

        return supported_types

    def addWriter(self, writer):
        self._mesh_writers[writer.getPluginId()] = writer

    def addReader(self, reader):
        self._mesh_readers[reader.getPluginId()] = reader
