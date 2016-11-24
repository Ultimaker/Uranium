# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Message import Message
from UM.Math.Vector import Vector
from UM.Preferences import Preferences
from UM.Logger import Logger
from UM.Mesh.MeshReader import MeshReader

import time
import math

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
        if self._handler is None:
            Logger.log("e", "FileHandler was not set.")
            return None
        reader = self._handler.getReaderForFile(self._filename)
        if not reader:
            result_message = Message(i18n_catalog.i18nc("@info:status", "Cannot open file type <filename>{0}</filename>", self._filename), lifetime=0)
            result_message.show()
            return

        # Give the plugin a chance to display a dialog before showing the loading UI
        pre_read_result = reader.preRead(self._filename)

        if pre_read_result != MeshReader.PreReadResult.accepted:
            if pre_read_result == MeshReader.PreReadResult.failed:
                result_message = Message(i18n_catalog.i18nc("@info:status", "Failed to load <filename>{0}</filename>", self._filename), lifetime=0)
                result_message.show()
            return

        self._loading_message = Message(i18n_catalog.i18nc("@info:status", "Loading <filename>{0}</filename>", self._filename), lifetime=0, dismissable=False)
        self._loading_message.setProgress(-1)
        self._loading_message.show()

        Job.yieldThread()  # Yield to any other thread that might want to do something else.

        try:
            begin_time = time.time()
            self.setResult(self._handler.readerRead(reader, self._filename))
            end_time = time.time()
            Logger.log("d", "Loading file took %s seconds", end_time - begin_time)
        except:
            Logger.logException("e", "Exception occurred while loading file %s", self._filename)
        finally:
            if self._result is None:
                self._loading_message.hide()
                result_message = Message(i18n_catalog.i18nc("@info:status", "Failed to load <filename>{0}</filename>", self._filename), lifetime=0)
                result_message.show()
                return
            self._loading_message.hide()