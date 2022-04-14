# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtQml import QQmlEngine

from UM.Application import Application
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.OutputDevice.ProjectOutputDevice import ProjectOutputDevice
from UM.Qt.ListModel import ListModel


class ProjectOutputDevicesModel(ListModel):
    """A list model providing a list of all registered OutputDevices that can save projects.

    Exposes the following roles:
    * id - The device ID
    * name - The human-readable name of the device
    * priority - The device priority

    """

    IdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    PriorityRole = Qt.ItemDataRole.UserRole + 3
    ShortcutRole = Qt.ItemDataRole.UserRole + 4

    projectOutputDevicesChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        # Ensure that this model doesn't get garbage collected (Now the bound object is destroyed when the wrapper is)
        QQmlEngine.setObjectOwnership(self, QQmlEngine.ObjectOwnership.CppOwnership)
        self._device_manager = Application.getInstance().getOutputDeviceManager()  # type: OutputDeviceManager

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.PriorityRole, "priority")
        self.addRoleName(self.ShortcutRole, "shortcut")

        self._device_manager.projectOutputDevicesChanged.connect(self._update)
        self._update()

    def _update(self):

        self.clear()
        items = []

        # Make a copy here, because we could discover devices during iteration.
        devices = [device for device in self._device_manager.getProjectOutputDevices() if device.enabled]  # type: List[ProjectOutputDevice]
        for device in devices:
            items.append({
                "id": device.getId(),
                "name": device.menu_entry_text,
                "priority": device.getPriority(),
                "shortcut": device.shortcut
            })

        items.sort(key = lambda i: -i["priority"])
        self.setItems(items)

        self.projectOutputDevicesChanged.emit()
