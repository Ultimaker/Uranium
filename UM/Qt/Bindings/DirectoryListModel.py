# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, QUrl

import os
import os.path
import platform

class DirectoryListModel(ListModel):
    NameRole = Qt.UserRole + 1
    UrlRole = Qt.UserRole + 2

    def __init__(self):
        super().__init__()

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.UrlRole, "url")

        self._directory = None

    directoryChanged = pyqtSignal()

    def getDirectory(self):
        return self._directory

    def setDirectory(self, path):
        if path != self._directory:
            if path.startswith("file://"):
                if platform.system() == "Windows" and path.startswith("file:///"):
                    path = path[8:]
                else:
                    path = path[7:]
            self._directory = os.path.dirname(path)

            items = []
            extensions = Application.getInstance().getMeshFileHandler().getSupportedFileTypesRead()
            for entry in os.listdir(self._directory):
                if os.path.splitext(entry)[1] in extensions:
                    items.append({ "name": os.path.basename(entry), "url": QUrl.fromLocalFile(os.path.join(self._directory, entry)) })

        items.sort(key = lambda e: e["name"])
        self.setItems(items)

    directory = pyqtProperty(str, fget = getDirectory, fset = setDirectory, notify = directoryChanged)
