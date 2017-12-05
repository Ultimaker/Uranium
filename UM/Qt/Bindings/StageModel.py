# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from PyQt5.QtCore import Qt

from UM.Application import Application
from UM.Qt.ListModel import ListModel


class StageModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.viewsChanged.connect(self._onViewsChanged)
        self._controller.activeViewChanged.connect(self._onViewsChanged)
        self._onViewsChanged()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")

    def _onViewsChanged(self):
        print("test")
