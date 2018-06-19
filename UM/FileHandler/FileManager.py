# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Dict, Optional, TYPE_CHECKING, cast

from UM.i18n import i18nCatalog
from UM.Logging.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase

if TYPE_CHECKING:
    from UM.Application import Application
    from .FileReader import FileReader
    from .FileWriter import FileWriter

i18n_catalog = i18nCatalog("uranium")


class FileManager:

    def __init__(self, application: "Application") -> None:
        if cast(FileManager, self.__class__).__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        cast(FileManager, self.__class__).__instance = self

        super().__init__()

        self._application = application
        self._readers = {}  # type: Dict[str, FileReader]
        self._writers = {}  # type: Dict[str, FileWriter]

    def addReader(self, reader: "FileReader") -> None:
        for file_ext in reader.supported_extensions:
            if file_ext in self._readers:
                Logger.log("w", "File extension %s has already been registered by reader %s, ignore reader %s",
                           file_ext, self._readers[file_ext], reader)
            self._readers[file_ext] = reader
            reader.initialize()

    def addWriter(self, writer: "FileWriter") -> None:
        for file_ext in writer.supported_extensions:
            if file_ext in self._writers:
                Logger.log("w", "File extension %s has already been registered by reader %s, ignore reader %s",
                           file_ext, self._writers[file_ext], writer)
            self._writers[file_ext] = writer

    def getWriterByMimeType(self, mime_type_name: str) -> Optional["FileWriter"]:
        mime_type = MimeTypeDatabase.getMimeType(mime_type_name)

        writer = None
        for suffix in mime_type.suffixes:
            print("!!!!!!!!!!!! suffix  = %s" % suffix)
            suffix = "." + suffix.lstrip(".")
            writer = self._writers.get(suffix)
            if writer is not None:
                break

        print("!!!!!!!!!!!! mime_type_name = %s  reader  = %s" % (mime_type_name, writer))
        return writer

    def getReaderForFileName(self, file_name: str) -> Optional["FileReader"]:
        the_reader = None
        for reader in self._readers.values():
            try:
                if reader.acceptsFile(file_name):
                    the_reader = reader
                    break
            except:
                Logger.logException("e", "Failed to check if reader %s accepts file name '%s'", reader, file_name)
        return the_reader

    __instance = None   # type: FileManager

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "FileManager":
        return cls.__instance
