# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.OutputDevice import OutputDeviceError
from UM.Logger import Logger
from UM.Message import Message

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

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ShortDescriptionRole, "short_description")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.IconNameRole, "icon_name")
        self.addRoleName(self.PriorityRole, "priority")

        self._device_manager.outputDevicesChanged.connect(self._update)
        self._device_manager.activeDeviceChanged.connect(self._onActiveDeviceChanged)
        self._update()
        self._onActiveDeviceChanged()

    activeDeviceChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", notify = activeDeviceChanged)
    def activeDevice(self):
        return self._active_device

    @pyqtSlot(str)
    def setActiveDevice(self, device_id):
        self._device_manager.setActiveDevice(device_id)

    @pyqtSlot(str)
    def requestWriteToDevice(self, device_id):
        device = self._device_manager.getOutputDevice(device_id)
        if not device:
            return

        try:
            device.requestWrite(Application.getInstance().getController().getScene().getRoot())
        except OutputDeviceError.UserCancelledError:
            pass
        except OutputDeviceError.PermissionDeniedError as e:
            message = Message("Could not write to {0}: Permission Denied".format(device.getName()))
            message.show()
        except OutputDeviceError.DeviceBusyError:
            message = Message("Could not write to {0}: Device is Busy".format(device.getName()))
            message.show()
        except OutputDeviceError.WriteRequestFailedError as e:
            message = Message("Could not write to {0}: {1}".format(device.getName(), str(e)))
            message.show()

    def _update(self):
        self.clear()

        devices = self._device_manager.getOutputDevices()
        for device in devices:
            self.appendItem({
                "id": device.getId(),
                "name": device.getName(),
                "short_description": device.getShortDescription(),
                "description": device.getDescription(),
                "icon_name": device.getIconName(),
                "priority": device.getPriority()
            })

        self.sort(lambda i: -i["priority"])

    def _onActiveDeviceChanged(self):
        device = self._device_manager.getActiveDevice()
        self._active_device = self.getItem(self.find("id", device.getId()))
        self.activeDeviceChanged.emit()
