# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

class PluginsModel(ListModel):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._registry = Application.getInstance().getPluginRegistry()
        self._required_plugins = Application.getInstance().getRequiredPlugins()

        # Static props:
        self.addRoleName(Qt.UserRole + 1, "id")
        self.addRoleName(Qt.UserRole + 2, "name")
        self.addRoleName(Qt.UserRole + 3, "version")
        self.addRoleName(Qt.UserRole + 4, "author")
        self.addRoleName(Qt.UserRole + 5, "author_email")
        self.addRoleName(Qt.UserRole + 6, "description")

        # Computed props:
        self.addRoleName(Qt.UserRole + 7, "file_location")
        self.addRoleName(Qt.UserRole + 8, "status")
        self.addRoleName(Qt.UserRole + 9, "enabled")
        self.addRoleName(Qt.UserRole + 10, "required")
        self.addRoleName(Qt.UserRole + 11, "can_upgrade")

        self._update()

    def _update(self):
        items = []

        # Get all active plugins from registry (list of strings):
        active_plugins = self._registry.getActivePlugins()

        # Metadata is used as the official list of "all plugins."
        for plugin in self._registry.getAllMetaData():

            if "plugin" not in plugin:
                Logger.log("e", "Plugin is missing a plugin metadata entry")
                continue

            props = plugin["plugin"]

            items.append({
                # Static props from above are taken from the plugin's metadata:
                "id": plugin["id"],
                "name": props.get("name", plugin["id"]),
                "version": props.get("version", "Unknown"),
                "author": props.get("author", "John Doe"),
                "author_email": "author@gmail.com",
                "description": props.get("description", ""),

                # Computed props from above are computed
                "file_location": "/users/i.paschal",
                "status": "installed",
                "enabled": plugin["id"] in active_plugins,
                "required": plugin["id"] in self._required_plugins,
                "can_upgrade": True
            })

        items.sort(key = lambda k: k["name"])
        self.setItems(items)

    @pyqtSlot(str,bool)
    def setEnabled(self, name, enabled):
        if enabled:
            self._plugin_registery.addActivePlugin(name)
        else:
            self._plugin_registery.removeActivePlugin(name)
