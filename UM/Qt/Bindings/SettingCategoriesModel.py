# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot, pyqtProperty, pyqtSignal

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
    HiddenValuesCountRole = Qt.UserRole + 6 # See SettingsCategory::getHiddenValuesCount()

    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_instance = None
        Application.getInstance().getMachineManager().activeMachineInstanceChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

        Application.getInstance().getMachineManager().activeProfileChanged.connect(self._onActiveProfileChanged)

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IconRole, "icon")
        self.addRoleName(self.VisibleRole, "visible")
        self.addRoleName(self.SettingsRole, "settings")
        self.addRoleName(self.HiddenValuesCountRole, "hiddenValuesCount") # Probably need a better name for this

        self._resetting = False

    @pyqtSlot(str)
    def filter(self, text):
        for item in self.items:
            item["settings"].filter(text)

    resettingChanged = pyqtSignal()
    @pyqtProperty(bool, notify = resettingChanged)
    def resetting(self):
        return self._resetting;

    @pyqtSlot()
    def reload(self):
        self._beginReset()
        self._items = []
        if self._machine_instance:
            for category in self._machine_instance.getMachineDefinition().getAllCategories():
                self._items.append({
                    "id": category.getKey(),
                    "name": category.getLabel(),
                    "icon": category.getIcon(),
                    "visible": category.isVisible(),
                    "settings": SettingsFromCategoryModel.SettingsFromCategoryModel(category),
                    "hiddenValuesCount": category.getHiddenValuesCount()
                })
        self._endReset()

    def _onActiveMachineChanged(self):
        self._beginReset()

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
                    "settings": SettingsFromCategoryModel.SettingsFromCategoryModel(category),
                    "hiddenValuesCount": category.getHiddenValuesCount()
                })
                category.visibleChanged.connect(self._onCategoryVisibleChanged)

        self._endReset()

    def _onCategoryVisibleChanged(self, category):
        index = self.find("id", category.getKey())
        self.setProperty(index, "visible", category.isVisible())
        self.setProperty(index, "hiddenValuesCount", category.getHiddenValuesCount())

    def _onActiveProfileChanged(self):
        if not self._machine_instance:
            return

        for category in self._machine_instance.getMachineDefinition().getAllCategories():
            index = self.find("id", category.getKey())
            self.setProperty(index, "hiddenValuesCount", category.getHiddenValuesCount())

    def _beginReset(self):
        self.beginResetModel()
        self._resetting = True
        self.resettingChanged.emit()

    def _endReset(self):
        self._resetting = False
        self.resettingChanged.emit()
        self.endResetModel()
