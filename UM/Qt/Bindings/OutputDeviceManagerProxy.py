# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Application import Application
from UM.Event import CallFunctionEvent
from UM.Scene.Selection import Selection
from UM.Message import Message
from UM.OutputDevice.OutputSubject import OutputSubject
from UM.OutputDevice import OutputDeviceError

class OutputDeviceManagerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._device_manager = Application.getInstance().getOutputDeviceManager()
        self._device_manager.activeDeviceChanged.connect(self._onActiveDeviceChanged)
        self._onActiveDeviceChanged()

    activeDeviceChanged = pyqtSignal()
    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDevice(self):
        return self._device_manager.getActiveDevice().getId()

    @pyqtSlot(str)
    def setActiveDevice(self, device_id):
        self._device_manager.setActiveDevice(device_id)

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceName(self):
        return self._device_manager.getActiveDevice().getName()

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceIconName(self):
        return self._device_manager.getActiveDevice().getIconName()

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceShortDescription(self):
        return self._device_manager.getActiveDevice().getShortDescription()

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceDescription(self):
        return self._device_manager.getActiveDevice().getDescription()

    @pyqtSlot(str, str)
    def requestWriteMeshToDevice(self, device_id, file_name):
        #On Windows, calling requestWrite() on LocalFileOutputDevice crashes
        #when called from a signal handler attached to a QML MenuItem. So
        #instead, defer the call to the next run of the event loop, since that
        #does work.
        event = CallFunctionEvent(self._writeToDevice, [Application.getInstance().getController().getScene().getRoot(), device_id, OutputSubject.MESH, file_name], {})
        Application.getInstance().functionEvent(event)

    @pyqtSlot(str, str)
    def requestWriteBackendOutputToDevice(self, device_id, file_name):
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        event = CallFunctionEvent(self._writeToDevice, [Application.getInstance().getController().getScene().getRoot(), device_id, OutputSubject.BACKEND_OUTPUT, file_name], {})
        Application.getInstance().functionEvent(event)

    @pyqtSlot(str, str)
    def requestWriteSelectionToDevice(self, device_id, file_name):
        if not Selection.hasSelection():
            return

        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        event = CallFunctionEvent(self._writeToDevice, [Selection.getSelectedObject(0), device_id, file_name], {})
        Application.getInstance().functionEvent(event)

    def _onActiveDeviceChanged(self):
        self.activeDeviceChanged.emit()

    def _writeToDevice(self, node, device_id, output_subject, file_name):
        device = self._device_manager.getOutputDevice(device_id)
        if not device:
            return

        try:
            device.requestWrite(node, output_subject, file_name)
        except OutputDeviceError.UserCanceledError:
            pass
        except OutputDeviceError.DeviceBusyError:
            pass
        except OutputDeviceError.WriteRequestFailedError as e:
            message = Message(str(e))
            message.show()

def createOutputDeviceManagerProxy(engine, script_engine):
    return OutputDeviceManagerProxy()
