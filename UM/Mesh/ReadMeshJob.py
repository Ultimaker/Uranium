# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Message import Message

import os.path

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

##  A Job subclass that performs mesh loading.
#
#   The result of this Job is a MeshData object.
class ReadMeshJob(Job):
    def __init__(self, filename):
        super().__init__()
        self._filename = filename
        self._handler = Application.getInstance().getMeshFileHandler()
        self._device = Application.getInstance().getStorageDevice("LocalFileStorage")

    def getFileName(self):
        return self._filename

    def run(self):
        loading_message = Message(i18n_catalog.i18nc("Loading mesh message, {0} is file name", "Loading {0}".format(self._filename)), lifetime = 0, dismissable = False)
        loading_message.setProgress(-1)
        loading_message.show()
        self.setResult(self._handler.read(self._filename, self._device))
        loading_message.hide()
        result_message = Message(i18n_catalog.i18nc("Finished loading mesh message, {0} is file name", "Loaded {0}".format(self._filename)))
        result_message.show()