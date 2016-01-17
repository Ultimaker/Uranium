# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot

class MachineMaterialsModel(ListModel):
    NameRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")

        self._manager = Application.getInstance().getMachineManager()

        self._manager.activeMachineInstanceChanged.connect(self._onInstanceChanged)
        self._onInstanceChanged()

    def _onInstanceChanged(self):
        self.clear()

        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return

        definitions = self._manager.getAllMachineMaterials(instance.getMachineDefinition().getId())
        if len(definitions) <= 1:
            return

        definitions.sort(key = lambda k: k.getMaterialName())

        for definition in definitions:
            self.appendItem({
                "name": definition.getMaterialName(),
                "active": definition.getMaterialName() == instance.getMachineDefinition().getMaterialName()
            })
