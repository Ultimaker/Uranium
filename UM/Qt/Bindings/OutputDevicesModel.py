# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.OutputDevice import OutputDeviceError
from UM.Event import CallFunctionEvent

import time

##  A list model providing a list of all registered OutputDevice instances.
#
#   This list model wraps OutputDeviceManager's list of OutputDevice instances.
#   Additionally it provides a function to set OutputDeviceManager's active device.
#
#   Exposes the following roles:
#   * id - The device ID
#   * name - The human-readable name of the device
#   * short_description - The short description of the device
#   * description - The full description of the device
#   * icon_name - The name of the icon used to identify the device
#   * priority - The device priority
#
class OutputDevicesModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ShortDescriptionRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4
    IconNameRole = Qt.UserRole + 5
    PriorityRole = Qt.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)

        self._device_manager = Application.getInstance().getOutputDeviceManager()

        self._active_device = None
        self._active_device_index = -1

        self._time_since_update = 0
        self._timer = None

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

    def _update(self):
        # Workaround for Qt issues on Windows
        # It seems menu items are created asynchronously on Windows, which causes
        # crashes when the model changes quickly in succession. To prevent that,
        # check the last time _update was called and if it was called recently
        # start a timer and return.
        now = time.time()
        if now - self._time_since_update < 2:
            self._timer = self.startTimer(2000)
            return
        self._time_since_update = now

        self.beginResetModel()

        self._items.clear()
        devices = self._device_manager.getOutputDevices()
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

    def timerEvent(self, event):
        self.killTimer(self._timer)
        self._timer = None
        self._update()
