# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot

class MachineDefinitionsModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    VariantNameRole = Qt.UserRole + 3
    ManufacturerRole = Qt.UserRole + 4
    AuthorRole = Qt.UserRole + 5

    def __init__(self):
        super().__init__()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.VariantNameRole, "variantName")
        self.addRoleName(self.ManufacturerRole, "manufacturer")
        self.addRoleName(self.AuthorRole, "author")

        self._manager = Application().getInstance().getMachineManager()

        self._manager.machineDefinitionsChanged.connect(self._onMachinesChanged)
        self._onMachinesChanged()

    def _onMachinesChanged(self):
        self.clear()

        definitions = self._manager.getMachineDefinitions()
        definitions.sort(key = lambda k: k.getName())

        for machine in definitions:
            self.appendItem({
                "id": machine.getId(),
                "name": machine.getName(),
                "variantName": machine.getVariantName(),
                "manufacturer": machine.getManufacturer(),
                "author": machine.getAuthor()
            })
