# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Set
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


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

    @pyqtSlot(str, result = bool)
    def getSettingVisible(self, key: str) -> bool:
        """Convenience method for QML to query the visibility of a single setting."""
        return key in self._visible

    @pyqtSlot(str, bool)
    def setSettingVisible(self, key: str, visible: bool) -> None:
        """Convenience method for QML to toggle the visibility of a single setting."""
        if visible == (key in self._visible):
            return

        visible_settings = self.getVisible()
        if visible:
            visible_settings.add(key)
        else:
            visible_settings.remove(key)
        self.setVisible(visible_settings)
