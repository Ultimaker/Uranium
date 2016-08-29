# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QAbstractListModel, QCoreApplication, Qt, QVariant

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.PluginRegistry import PluginRegistry

class ViewModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4
    IconRole = Qt.UserRole + 5

    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.viewsChanged.connect(self._onViewsChanged)
        self._controller.activeViewChanged.connect(self._onViewsChanged)
        self._onViewsChanged()  

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.IconRole, "icon")

    def _onViewsChanged(self):
        items = []
        views = self._controller.getAllViews()

        for id in views:
            viewMetaData = PluginRegistry.getInstance().getMetaData(id).get("view", {})

            # Skip view modes that are marked as not visible
            if "visible" in viewMetaData and not viewMetaData["visible"]:
                continue

            # Metadata elements
            name = viewMetaData.get("name", id)
            description = viewMetaData.get("description", "")
            iconName = viewMetaData.get("icon", "")
            weight = viewMetaData.get("weight", 0)

            currentView = self._controller.getActiveView()
            items.append({ "id": id, "name": name, "active": id == currentView.getPluginId(), "description": description, "icon": iconName, "weight": weight })

        items.sort(key = lambda t: t["weight"])
        self.setItems(items)