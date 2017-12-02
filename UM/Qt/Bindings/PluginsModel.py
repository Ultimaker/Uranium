# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

class PluginsModel(ListModel):
    NameRole = Qt.UserRole + 1
    RequiredRole = Qt.UserRole + 2
    EnabledRole = Qt.UserRole + 3
    TypeRole = Qt.UserRole + 4
    DescriptionRole = Qt.UserRole + 5
    AuthorRole = Qt.UserRole + 6
    VersionRole = Qt.UserRole + 7
    IdRole = Qt.UserRole + 8

    def __init__(self, parent = None):
        super().__init__(parent)
        self._plugin_registery = PluginRegistry.getInstance()
        self._required_plugins = Application.getInstance().getRequiredPlugins()
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.RequiredRole, "required")
        self.addRoleName(self.EnabledRole, "enabled")

        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.AuthorRole, "author")
        self.addRoleName(self.VersionRole, "version")
        self._update()

    def _update(self):
        items = []
        active_plugins = self._plugin_registery.getActivePlugins()
        for plugin in self._plugin_registery.getAllMetaData():
            if "plugin" not in plugin:
                Logger.log("e", "Plugin is missing a plugin metadata entry")
                continue

            aboutData = plugin["plugin"]
            items.append({
                "id": plugin["id"],
                "required": plugin["id"] in self._required_plugins,
                "enabled": plugin["id"] in active_plugins,

                "name": aboutData.get("name", plugin["id"]),
                "description": aboutData.get("description", ""),
                "author": aboutData.get("author", "John Doe"),
                "version": aboutData.get("version", "Unknown")
            })
        items.sort(key = lambda k: k["name"])
        self.setItems(items)

    @pyqtSlot(str,bool)
    def setEnabled(self, name, enabled):
        if enabled:
            self._plugin_registery.addActivePlugin(name)
        else:
            self._plugin_registery.removeActivePlugin(name)
