# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import Qt
from UM.Qt.ListModel import ListModel


class FileProviderModel(ListModel):
    ModelDataRole = Qt.ItemDataRole.UserRole

    def __init__(self, application = None, parent = None):
        super().__init__(parent)
        self.addRoleName(self.ModelDataRole, "modelData")

        self._application = application

    def initialize(self) -> None:
        """ Initializes the file provider model. """

        for file_provider in self._application.getFileProviders():
            plugin_id = file_provider.getPluginId()
            meta_data = self._application.getPluginRegistry().getMetaData(plugin_id)

            if "plugin" in meta_data:
                self.appendItem({ "modelData": file_provider })

        self.sort(lambda x: -float(x["modelData"].priority))
