# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt
from UM.FlameProfiler import pyqtSlot
from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.Logger import Logger


class ExtensionModel(ListModel):
    NameRole = Qt.UserRole + 1
    ActionsRole = Qt.UserRole + 2
    ExtensionRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActionsRole, "actions")
        self.addRoleName(self.ExtensionRole, "extension")
        self._updateExtensionList()

    def _updateExtensionList(self):
        # Active_plugins = self._plugin_registry.getActivePlugins()
        for extension in Application.getInstance().getExtensions():
            meta_data = Application.getInstance().getPluginRegistry().getMetaData(extension.getPluginId())

            if "plugin" in meta_data:
                menu_name = extension.getMenuName()

                if not menu_name:
                    menu_name = meta_data["plugin"].get("name", None)

                self.appendItem({
                    "name": menu_name,
                    "actions": self.createActionsModel(extension.getMenuItemList()),
                    "extension": extension
                })

    def createActionsModel(self, options):
        model = ListModel()
        model.addRoleName(self.NameRole, "text")
        for option in options:
            model.appendItem({"text": str(option)})
        if len(options) != 0:
            return model
        return None

    @pyqtSlot(str, str)
    def subMenuTriggered(self, extension_name, option_name):
        for item in self._items:
            if extension_name == item["name"]:
                try:
                    item["extension"].activateMenuItem(option_name)
                except Exception:
                    # Yes, we really want a broad exception here. These items are always plugins, and those should be
                    # kept from crashing the main application as much as possible.
                    Logger.logException("w", "Failed to activate the menu item")

    @pyqtSlot(str, str)
    def callExtensionMethod(self, extension_name, method_name):
        for item in self._items:
            if extension_name == item["name"]:
                if hasattr(item["extension"], method_name):
                    getattr(item["extension"], method_name)()
