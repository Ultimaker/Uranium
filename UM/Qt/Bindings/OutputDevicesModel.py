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

        self._current_device = None

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ShortDescriptionRole, "short_description")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.IconNameRole, "icon_name")
        self.addRoleName(self.PriorityRole, "priority")

        Application.getInstance().getOutputDeviceManager().outputDevicesChanged.connect(self._update)
        self._update()

    currentDeviceChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", notify = currentDeviceChanged)
    def currentDevice(self):
        return self._current_device

    @pyqtSlot(str)
    def setCurrentDevice(self, id):
        if not self._current_device or self._current_device["id"] != id:
            self._current_device = self.getItem(self.find("id", id))
            self.currentDeviceChanged.emit()

    @pyqtSlot(str)
    def requestWriteToDevice(self, device_id):
        device = Application.getInstance().getOutputDeviceManager().getOutputDevice(device_id)
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

        devices = Application.getInstance().getOutputDeviceManager().getOutputDevices()
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

        if self._current_device == None:
            self._current_device = self.getItem(0)
