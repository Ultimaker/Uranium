# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Set
from PyQt5.QtCore import QObject, pyqtSignal


class SettingVisibilityHandler(QObject):
    def __init__(self, parent = None, *args, **kwargs) -> None:
        super().__init__(parent = parent, *args, **kwargs)

        self._visible = set()  # type: Set[str]

    visibilityChanged = pyqtSignal()

    def setVisible(self, visible: Set[str]) -> None:
        if visible != self._visible:
            self._visible = visible
            self.visibilityChanged.emit()

    def getVisible(self) -> Set[str]:
        return self._visible.copy()

    def forceVisibilityChanged(self) -> None:
        self.visibilityChanged.emit()


