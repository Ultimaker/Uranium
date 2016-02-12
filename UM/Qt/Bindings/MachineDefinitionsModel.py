# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Settings.MachineInstance import MachineInstance

class MachineDefinitionsModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    VariantNameRole = Qt.UserRole + 3
    ManufacturerRole = Qt.UserRole + 4
    AuthorRole = Qt.UserRole + 5
    PagesRole = Qt.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.VariantNameRole, "variantName")
        self.addRoleName(self.ManufacturerRole, "manufacturer")
        self.addRoleName(self.AuthorRole, "author")
        self.addRoleName(self.PagesRole, "pages")

        self._manager = Application.getInstance().getMachineManager()

        self._show_variants = True

        self._manager.machineDefinitionsChanged.connect(self._onMachinesChanged)
        self._onMachinesChanged()

    showVariantsChanged = pyqtSignal()

    def setShowVariants(self, show):
        if show != self._show_variants:
            self._show_variants = show
            self._onMachinesChanged()
            self.showVariantsChanged.emit()

    @pyqtProperty(bool, fset = setShowVariants, notify = showVariantsChanged)
    def showVariants(self):
        return self._show_variants

    @pyqtSlot(str, str)
    def createInstance(self, name, definition_id):
        definition = self._manager.findMachineDefinition(definition_id)

        instance = MachineInstance(self._manager, name = self._manager.makeUniqueMachineInstanceName(name, definition.getName()), definition = definition)
        self._manager.addMachineInstance(instance)

        # Workaround for an issue on OSX where directly calling setActiveMachineInstance would
        # crash in the QML garbage collector.
        Application.getInstance().callLater(self._manager.setActiveMachineInstance, instance)

    def _onMachinesChanged(self):
        self.clear()

        definitions = self._manager.getMachineDefinitions(include_variants = self._show_variants)
        definitions = filter(lambda s: s.isVisible(), definitions)
        definitions = sorted(definitions)

        for machine in definitions:
            self.appendItem({
                "id": machine.getId(),
                "name": machine.getName(),
                "variantName": machine.getVariantName(),
                "manufacturer": machine.getManufacturer(),
                "author": machine.getAuthor(),
                "pages": machine.getPages()
            })
