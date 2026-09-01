# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import Qt

from UM.Application import Application
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.Qt.ListModel import ListModel


class ProjectOutputDevicesModel(ListModel):
    """A list model providing a list of all registered OutputDevices that can save projects."""

    ModelDataRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent = None):
        super().__init__(parent)
        self._device_manager: OutputDeviceManager = Application.getInstance().getOutputDeviceManager()

        self.addRoleName(self.ModelDataRole, "modelData")

        self._device_manager.projectOutputDeviceAdded.connect(self._onProjectOutputDeviceAdded)
        self._device_manager.projectOutputDeviceRemoved.connect(self._onProjectOutputDeviceRemoved)

        items = []
        for device in self._device_manager.getProjectOutputDevices():
            items.append({"modelData": device})
        self.setItems(items)
        self.sort(lambda x: -float(x["modelData"].getPriority()))

    def _onProjectOutputDeviceAdded(self, device):
        new_item = {"modelData": device}
        actual_devices = self._device_manager.getProjectOutputDevices()
        if actual_devices:
            insert_position = None
            for index, actual_device in enumerate(actual_devices):
                if actual_device.getPriority() < device.getPriority():
                    insert_position = index
                    break

            if insert_position is not None:
                self.insertItem(insert_position, new_item)
            else:
                self.appendItem(new_item)
        else:
            self.appendItem(new_item)

    def _onProjectOutputDeviceRemoved(self, device):
        for index, item in enumerate(self.items):
            if item["modelData"] is device:
                self.removeItem(index)
                return
