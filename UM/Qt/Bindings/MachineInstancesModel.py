# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot

class MachineInstancesModel(ListModel):
    NameRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2

    def __init__(self):
        super().__init__()

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")

        self._manager = Application().getInstance().getMachineManager()

        self._manager.machineInstancesChanged.connect(self._onMachinesChanged)
        self._manager.activeMachineInstanceChanged.connect(self._onActiveMachineChanged)
        self._onMachinesChanged()

    def _onMachinesChanged(self):
        self.clear()

        instances = self._manager.getMachineInstances()
        instances.sort(key = lambda k: k.getName())

        for machine in instances:
            self.appendItem({ "id": id(machine), "name": machine.getName(), "active": self._manager.getActiveMachineInstance() == machine })

    def _onActiveMachineChanged(self):
        active_machine = self._manager.getActiveMachineInstance()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(active_machine) == self.items[index]["id"])

