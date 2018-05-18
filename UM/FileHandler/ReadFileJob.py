# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Job import Job
from UM.Message import Message
from UM.Logger import Logger
from UM.Mesh.MeshReader import MeshReader

import time
import os

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

##  A Job subclass that performs file loading.
#
class ReadFileJob(Job):
    def __init__(self, filename, handler = None):
        super().__init__()
        self._filename = filename
        self._handler = handler
        self._loading_message = None

    def getFileName(self):
        return self._filename

    def run(self):
        # HACK: Packages shouldn't be checked for a reader. Maybe someday we build a reader. Maybe not. But for now,
        # this hack is the only solution.
        filename, file_extension = os.path.splitext(self._filename)
        if file_extension == ".curapackage":
            return

        if self._handler is None:
            Logger.log("e", "FileHandler was not set.")
            return None
        reader = self._handler.getReaderForFile(self._filename)

        if not reader:
            result_message = Message(i18n_catalog.i18nc("@info:status Don't translate the XML tag <filename>!", "Cannot open files of the type of <filename>{0}</filename>", self._filename), lifetime=0, title = i18n_catalog.i18nc("@info:title", "Invalid File"))
            result_message.show()
            return

        # Give the plugin a chance to display a dialog before showing the loading UI
        try:
            pre_read_result = reader.preRead(self._filename)
        except:
            Logger.logException("e", "Failed to pre-read the file %s", self._filename)
            pre_read_result = MeshReader.PreReadResult.failed

        if pre_read_result != MeshReader.PreReadResult.accepted:
            if pre_read_result == MeshReader.PreReadResult.failed:
                result_message = Message(i18n_catalog.i18nc("@info:status Don't translate the XML tag <filename>!", "Failed to load <filename>{0}</filename>", self._filename),
                                         lifetime=0,
                                         title = i18n_catalog.i18nc("@info:title", "Invalid File"))
                result_message.show()
            return

        self._loading_message = Message(self._filename,
                                        lifetime=0,
                                        dismissable=False,
                                        title = i18n_catalog.i18nc("@info:title", "Loading"))
        self._loading_message.setProgress(-1)
        self._loading_message.show()

        Job.yieldThread()  # Yield to any other thread that might want to do something else.

        try:
            begin_time = time.time()
            self.setResult(self._handler.readerRead(reader, self._filename))
            end_time = time.time()
            Logger.log("d", "Loading file took %0.1f seconds", end_time - begin_time)
        except:
            Logger.logException("e", "Exception occurred while loading file %s", self._filename)
        finally:
            if self._result is None:
                self._loading_message.hide()
                result_message = Message(i18n_catalog.i18nc("@info:status Don't translate the XML tag <filename>!", "Failed to load <filename>{0}</filename>", self._filename), lifetime=0, title = i18n_catalog.i18nc("@info:title", "Invalid File"))
                result_message.show()
                return
            self._loading_message.hide()
