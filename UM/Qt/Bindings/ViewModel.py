# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.PluginRegistry import PluginRegistry


class ViewModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4
    IconRole = Qt.UserRole + 5

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.viewsChanged.connect(self._update)
        self._controller.activeViewChanged.connect(self._update)
        self._update()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.IconRole, "icon")

    def _update(self) -> None:
        items = []
        views = self._controller.getAllViews()
        current_view = self._controller.getActiveView()
        if current_view is None:
            return

        for view_id in views:
            view_meta_data = PluginRegistry.getInstance().getMetaData(view_id).get("view", {})

            # Skip view modes that are marked as not visible
            if "visible" in view_meta_data and not view_meta_data["visible"]:
                continue

            # Metadata elements
            name = view_meta_data.get("name", view_id)
            description = view_meta_data.get("description", "")
            icon_name = view_meta_data.get("icon", "")
            weight = view_meta_data.get("weight", 0)

            items.append({
                "id": view_id,
                "name": name,
                "active": view_id == current_view.getPluginId(),
                "description": description,
                "icon": icon_name,
                "weight": weight
            })

        items.sort(key = lambda t: t["weight"])
        self.setItems(items)
