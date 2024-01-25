# Copyright (c) 2024 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtQml import QQmlEngine

from UM.Application import Application
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.OutputDevice.ProjectOutputDevice import ProjectOutputDevice
from UM.Qt.ListModel import ListModel


class MeshWritersModel(ListModel):
    """A list model providing a list of all registered MeshWriters that can export meshes.

    Exposes the following roles:
    * mime_type - The associated writable file mime type
    * description - The human-readable name of the file format

    """

    MimeTypeRole = Qt.ItemDataRole.UserRole + 1
    DescriptionRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, parent = None):
        super().__init__(parent)
        # Ensure that this model doesn't get garbage collected (Now the bound object is destroyed when the wrapper is)
        QQmlEngine.setObjectOwnership(self, QQmlEngine.ObjectOwnership.CppOwnership)

        self.addRoleName(self.MimeTypeRole, "mime_type")
        self.addRoleName(self.DescriptionRole, "description")

        self.setItems(Application.getInstance().getMeshFileHandler().getSupportedFileTypesWrite())
