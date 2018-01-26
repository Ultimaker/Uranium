# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

class PluginsModel(ListModel):
    def __init__(self, view, parent = None):
        super().__init__(parent)

        self._registry = Application.getInstance().getPluginRegistry()
        self._required_plugins = Application.getInstance().getRequiredPlugins()

        # Static props:
        # These should be defined in plugin.json and are read-only.
        self.addRoleName(Qt.UserRole + 1, "id")
        self.addRoleName(Qt.UserRole + 2, "name")
        self.addRoleName(Qt.UserRole + 3, "version")
        self.addRoleName(Qt.UserRole + 4, "author")
        self.addRoleName(Qt.UserRole + 5, "author_email")
        self.addRoleName(Qt.UserRole + 6, "description")

        # Computed props:
        # These are computed based on the user's system and interactions.
        self.addRoleName(Qt.UserRole + 7, "external")
        self.addRoleName(Qt.UserRole + 8, "file_location")
        self.addRoleName(Qt.UserRole + 9, "status")
        self.addRoleName(Qt.UserRole + 10, "enabled")
        self.addRoleName(Qt.UserRole + 11, "required")
        self.addRoleName(Qt.UserRole + 12, "can_upgrade")
        self.addRoleName(Qt.UserRole + 13, "update_url")


        if view == "installed":
            self._plugins = self._registry.getInstalledPlugins()
            self._update(view)

        if view == "available":
            self._plugins = self._registry.getAvailablePlugins()
            self._update(view)

    def _update(self, view):
        items = []
        # Get all active plugins from registry (list of strings):
        active_plugins = self._registry.getActivePlugins()
        installed_plugins = self._registry.getInstalledPlugins()

        # Metadata is used as the official list of "all plugins":
        for plugin_id in self._plugins:

            metadata = self._registry.getMetaData(plugin_id)

            if "plugin" not in metadata:
                Logger.log("e", "Plugin is missing a plugin metadata entry")
                continue

            props = metadata["plugin"]

            items.append({
                # Static props from above are taken from the plugin's metadata:
                "id": metadata["id"],
                "name": props.get("name", props.get("label", metadata["id"])),
                "version": props.get("version", "Unknown"),
                "author": props.get("author", "Anonymous"),
                "author_email": props.get("author_email", "author@gmail.com"),
                "description": props.get("description", props.get("short_description", "No description provided...")),

                # Computed props from above are computed
                "external": True if metadata["id"] in self._registry._plugins_external else False,
                "file_location": props.get("file_location", "/"),
                "status": "installed" if metadata["id"] in installed_plugins else "available",
                "enabled": True if view == "available" else metadata["id"] in active_plugins,
                "required": metadata["id"] in self._required_plugins,
                "can_upgrade": False, # Default, potentially overwritten by plugin browser
                "update_url": None # Default, potentially overwritten by plugin browser

            })

        items.sort(key = lambda k: k["name"])
        self.setItems(items)
