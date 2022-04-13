# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Qt.ListModel import ListModel

from PyQt6.QtQml import QQmlEngine


class OutputDevicesModel(ListModel):
    """A list model providing a list of all registered OutputDevice instances.

    This list model wraps OutputDeviceManager's list of OutputDevice instances.
    Additionally it provides a function to set OutputDeviceManager's active device.

    Exposes the following roles:
    * id - The device ID
    * name - The human-readable name of the device
    * short_description - The short description of the device
    * description - The full description of the device
    * icon_name - The name of the icon used to identify the device
    * priority - The device priority

    """

    IdRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    ShortDescriptionRole = Qt.ItemDataRole.UserRole + 3
    DescriptionRole = Qt.ItemDataRole.UserRole + 4
    IconNameRole = Qt.ItemDataRole.UserRole + 5
    PriorityRole = Qt.ItemDataRole.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)
        # Ensure that this model doesn't get garbage collected (Now the bound object is destroyed when the wrapper is)
        QQmlEngine.setObjectOwnership(self, QQmlEngine.ObjectOwnership.CppOwnership)
        self._device_manager = Application.getInstance().getOutputDeviceManager()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ShortDescriptionRole, "short_description")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.IconNameRole, "icon_name")
        self.addRoleName(self.PriorityRole, "priority")

        self._device_manager.outputDevicesChanged.connect(self._update)
        self._update()

    @pyqtSlot(str, result = "QVariantMap")
    def getDevice(self, device_id):
        index = self.find("id", device_id)
        if index != -1:
            return self.getItem(index)

        return { "id": "", "name": "", "short_description": "", "description": "", "icon_name": "save", "priority": -1 }

    outputDevicesChanged = pyqtSignal()

    @pyqtProperty(int, notify = outputDevicesChanged)
    def deviceCount(self):
        return self.count

    def _update(self):
        try:
            self.beginResetModel()
        except RuntimeError:
            # Don't break if the object was garbage collected.
            return

        self._items.clear()
        devices = list(self._device_manager.getOutputDevices())[:]  # Make a copy here, because we could discover devices during iteration.
        for device in devices:
            self._items.append({
                "id": device.getId(),
                "name": device.getName(),
                "short_description": device.getShortDescription(),
                "description": device.getDescription(),
                "icon_name": device.getIconName(),
                "priority": device.getPriority()
            })

        self.sort(lambda i: -i["priority"])
        self.endResetModel()

        self.outputDevicesChanged.emit()
