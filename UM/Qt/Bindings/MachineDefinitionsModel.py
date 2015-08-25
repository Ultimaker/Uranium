# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Qt.ListModel import ListModel
from UM.Application import Application

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
                "author": machine.getAuthor(),
                "pages": machine.getPages()
            })
