# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Resources import Resources
from UM.Application import Application

from . import SettingsFromCategoryModel

class SettingCategoriesModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    IconRole = Qt.UserRole + 3
    VisibleRole = Qt.UserRole + 4
    SettingsRole = Qt.UserRole + 5

    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_instance = None
        Application.getInstance().getMachineManager().activeMachineInstanceChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IconRole, "icon")
        self.addRoleName(self.VisibleRole, "visible")
        self.addRoleName(self.SettingsRole, "settings")

    def _onActiveMachineChanged(self):
        self.clear()
        if self._machine_instance:
            for category in self._machine_instance.getMachineDefinition().getAllCategories():
                category.visibleChanged.disconnect(self._onCategoryVisibleChanged)

        self._machine_instance = Application.getInstance().getMachineManager().getActiveMachineInstance()

        if self._machine_instance:
            for category in self._machine_instance.getMachineDefinition().getAllCategories():
                self.appendItem({
                    "id": category.getKey(),
                    "name": category.getLabel(),
                    "icon": category.getIcon(),
                    "visible": category.isVisible(),
                    "settings": SettingsFromCategoryModel.SettingsFromCategoryModel(category)
                })
                category.visibleChanged.connect(self._onCategoryVisibleChanged)

    def _onCategoryVisibleChanged(self, category):
        index = self.find("id", category.getKey())
        self.setProperty(index, "visible", category.isVisible())
