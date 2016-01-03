# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from UM.Backend.OutputWriter import OutputWriter

##  Central class for managing where the backend output goes.
#
#   This class is created by Application.
class OutputHandler(object):
    def __init__(self):
        super().__init__()

        self._output_writers = {}
        PluginRegistry.addType("output_writer", self.addWriter)

    ##  Get an instance of an output writer by ID.
    #
    #   \param writer_id The ID of the output writer to find.
    def getWriter(self, writer_id):
        if not writer_id in self._output_writers:
            return None

        return self._output_writers[writer_id]

    ##  Get an output writer object that supports writing the specified MIME
    #   type.
    #
    #   \param mime The MIME type that should be supported.
    #   \return An OutputWriter instance or None if no output writer supports
    #   the specified MIME type. If there are multiple writers that support the
    #   specified MIME type, the first entry is returned.
    def getWriterByMimeType(self, mime):
        writer_data = PluginRegistry.getInstance().getAllMetaData(filter = {"output_writer": {}}, active_only = True)
        for entry in writer_data: #Search through all output writers.
            for output in entry["output_writer"].get("output", []):
                if mime == output["mime_type"]: #MIME type is correct.
                    return self._output_writers[entry["id"]]
        return None #No writer was found to support the MIME type.

    ##  Get list of all supported filetypes for writing.
    #
    #   \return List of dictionaries containing a plugin ID, extension,
    #   description and MIME type for all supported file types.
    def getSupportedFileTypesWrite(self):
        supported_types = []
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"output_writer": {}}, active_only = True)
        for entry in meta_data: #Search through all output writers.
            for output in entry["output_writer"].get("output", []):
                extension = output.get("extension", "")
                description = output.get("description", extension)
                mime_type = output.get("mime_type", "text/plain")
                supported_types.append({
                    "id": entry["id"],
                    "extension": extension,
                    "description": description,
                    "mime_type": mime_type,
                })
        return supported_types

    def addWriter(self, writer):
        self._output_writers[writer.getPluginId()] = writer
