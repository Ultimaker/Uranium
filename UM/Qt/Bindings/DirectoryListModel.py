from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, QUrl

import os
import os.path

class DirectoryListModel(ListModel):
    NameRole = Qt.UserRole + 1
    UrlRole = Qt.UserRole + 2

    def __init__(self):
        super().__init__()

        self.addRoleName(self.NameRole, 'name')
        self.addRoleName(self.UrlRole, 'url')

        self._directory = None

    directoryChanged = pyqtSignal()

    def getDirectory(self):
        return self._directory

    def setDirectory(self, path):
        if path != self._directory:
            if path.startswith('file://'):
                path = path[7:]
            self._directory = os.path.dirname(path)

            self.clear()
            extensions = Application.getInstance().getMeshFileHandler().getSupportedFileTypesRead()
            for entry in os.listdir(self._directory):
                if os.path.splitext(entry)[1] in extensions:
                    self.appendItem({ 'name': os.path.basename(entry), 'url': QUrl.fromLocalFile(os.path.join(self._directory, entry)) })

        self.sort(lambda e: e['name'])

    directory = pyqtProperty(str, fget = getDirectory, fset = setDirectory, notify = directoryChanged)
