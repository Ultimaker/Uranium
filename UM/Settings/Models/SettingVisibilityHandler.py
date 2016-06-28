# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSignal

class SettingVisibilityHandler(QObject):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self._visible = set()

    visibilityChanged = pyqtSignal()

    def setVisible(self, visible):
        if visible != self._visible:
            self._visible = visible
            self.visibilityChanged.emit()

    def getVisible(self):
        return self._visible.copy()

