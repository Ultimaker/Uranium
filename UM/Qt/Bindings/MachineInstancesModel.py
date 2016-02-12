# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot

class MachineInstancesModel(ListModel):
    NameRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2
    TypeNameRole = Qt.UserRole + 3
    VariantNameRole = Qt.UserRole + 4
    HasVariantsRole = Qt.UserRole + 5
    HasMaterialsRole = Qt.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")
        self.addRoleName(self.TypeNameRole, "typeName")
        self.addRoleName(self.VariantNameRole, "variantName")
        self.addRoleName(self.HasVariantsRole, "hasVariants")
        self.addRoleName(self.HasMaterialsRole, "hasMaterials")

        self._manager = Application.getInstance().getMachineManager()

        self._manager.machineInstancesChanged.connect(self._onMachinesChanged)
        self._manager.activeMachineInstanceChanged.connect(self._onActiveMachineChanged)
        self._manager.machineInstanceNameChanged.connect(self._onInstanceNameChanged)
        self._onMachinesChanged()

    @pyqtSlot()
    def requestAddMachine(self):
        self._manager.addMachineRequested.emit()

    @pyqtSlot(str)
    def removeMachineInstance(self, name):
        instance = self._manager.findMachineInstance(name)
        if not instance:
            return

        self._manager.removeMachineInstance(instance)

    @pyqtSlot(str, result = bool)
    def checkInstanceNameExists(self, name):
        instance = self._manager.findMachineInstance(name)
        if instance:
            return True
        return False

    @pyqtSlot(str, str)
    def renameMachineInstance(self, old_name, new_name):
        instance = self._manager.findMachineInstance(old_name)
        if not instance:
            return

        instance.setName(new_name)

    def _onMachinesChanged(self):
        self.clear()

        instances = self._manager.getMachineInstances()
        instances.sort(key = lambda k: k.getName())

        for machine in instances:
            self.appendItem({
                "id": id(machine),
                "name": machine.getName(),
                "active": self._manager.getActiveMachineInstance() == machine,
                "typeName": machine.getMachineDefinition().getName(),
                "variantName": machine.getMachineDefinition().getVariantName(),
                "hasVariants": machine.getMachineDefinition().hasVariants(),
                "hasMaterials": machine.hasMaterials()
            })

    def _onActiveMachineChanged(self):
        active_machine = self._manager.getActiveMachineInstance()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(active_machine) == self.items[index]["id"])

    def _onInstanceNameChanged(self, machine):
        index = self.find("id", id(machine))
        if index == -1:
            return

        self.setProperty(index, "name", machine.getName())
