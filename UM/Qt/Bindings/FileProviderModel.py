# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Callable, Optional

from PyQt6.QtCore import Qt
from UM.FlameProfiler import pyqtSlot
from UM.i18n import i18nCatalog
from UM.Qt.ListModel import ListModel
from UM.Logger import Logger

i18n_catalog = i18nCatalog("uranium")

class FileProviderModel(ListModel):
    NameRole = Qt.ItemDataRole.UserRole + 1
    DisplayTextRole = Qt.ItemDataRole.UserRole + 2
    FileProviderRole = Qt.ItemDataRole.UserRole + 3
    ShortcutRole = Qt.ItemDataRole.UserRole + 4

    def __init__(self, application = None, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.DisplayTextRole, "displayText")
        self.addRoleName(self.FileProviderRole, "fileProvider")
        self.addRoleName(self.ShortcutRole, "shortcut")
        self._application = application

    def initialize(self, file_provider_enabled_call_function: Optional[Callable]) -> None:
        """
        Initializes the file provider model.
        This is achieved by connecting the enabledChanged signal of all the file_providers to the given function.

        :param file_provider_enabled_call_function: The function which will be called when a file provider gets enabled
                                                    or disabled
        """
        for file_provider in self._application.getFileProviders():
            file_provider.enabledChanged.connect(file_provider_enabled_call_function)
        self.update()

    def update(self) -> None:
        """
        Updates the FileProviderModel to contain only the enabled file providers.
        """
        self.clear()

        # Always add the local file provider to the list. Since it is not really a plugin, fake an entry in the file providers
        # list and handle it in the front-end by triggering the openAction when that item is selected
        self.appendItem({
            "name"         : "LocalFileProvider",
            "displayText"  : i18n_catalog.i18nc("@menu", "From Disk"),
            "fileProvider" : None,  # it's not loaded via a plugin, so its FileProvider is empty
            "shortcut"     : "Ctrl+O",
            "priority"     : 99,  # Assign a high value to make sure it appears on top in the File->Open File(s) submenu
        })

        for file_provider in self._application.getFileProviders():
            plugin_id = file_provider.getPluginId()
            meta_data = self._application.getPluginRegistry().getMetaData(plugin_id)

            if "plugin" in meta_data and file_provider.enabled:

                self.appendItem({
                    "name": plugin_id,
                    "displayText" : file_provider.menu_item_display_text,
                    "fileProvider": file_provider,
                    "shortcut": file_provider.shortcut,
                    "priority": file_provider.priority,
                })

        self.sort(lambda x: -float(x["priority"]))

    @pyqtSlot(str)
    def trigger(self, file_provider_name) -> None:
        """
        Safely triggers the run function of the given file_provider_name

        :param file_provider_name: The file provider which was requested to be triggered
        """
        for item in self._items:
            if item["name"] == file_provider_name:
                try:
                    item["fileProvider"].run()
                except Exception:
                    # Yes, we really want a broad exception here. These items are always plugins, and those should be
                    # kept from crashing the main application as much as possible.
                    Logger.logException("w", "Failed to activate the file provider '{}'".format(file_provider_name))
