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
        self._machine_settings = None
        Application.getInstance().activeMachineChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IconRole, "icon")
        self.addRoleName(self.VisibleRole, "visible")
        self.addRoleName(self.SettingsRole, "settings")

    def _onActiveMachineChanged(self):
        self.clear()
        if self._machine_settings:
            for category in self._machine_settings.getAllCategories():
                category.visibleChanged.disconnect(self._onCategoryVisibleChanged)

        self._machine_settings = Application.getInstance().getActiveMachine()

        if self._machine_settings:
            for category in self._machine_settings.getAllCategories():
                self.appendItem({
                    "id": category.getKey(),
                    "name": category.getLabel(),
                    "icon": category.getIcon(),
                    "visible": category.isVisible(),
                    "settings": SettingsFromCategoryModel.SettingsFromCategoryModel(category)
                })
                category.visibleChanged.connect(self._onCategoryVisibleChanged)

    def _onCategoryVisibleChanged(self, category):
        for index in range(len(self.items)):
            if self.getItem(index)['id'] == category.getKey():
                self.setProperty(index, "visible", category.isVisible())

