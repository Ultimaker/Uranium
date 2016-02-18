# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Application import Application
from UM.Scene.Selection import Selection
from UM.Message import Message
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

    ##  Request that the current scene is written to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param device_id \type{string} The handle of the device to write to.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param kwargs Key-word arguments:
    #       filter_by_machine: If the file name is ignored, should the file
    #                          format that the output device chooses be limited
    #                          to the formats that are supported by the
    #                          currently active machine?
    @pyqtSlot(str, str, "QVariantMap")
    def requestWriteToDevice(self, device_id, file_name, kwargs):
        filter_by_machine = kwargs.get("filter_by_machine", False)
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        Application.getInstance().callLater(self._writeToDevice, Application.getInstance().getController().getScene().getRoot(), device_id, file_name, filter_by_machine)

    ##  Request that the current selection is written to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param device_id \type{string} The handle of the device to write to.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param kwargs Key-word arguments:
    #       filter_by_machine: If the file name is ignored, should the file
    #                          format that the output device chooses be limited
    #                          to the formats that are supported by the
    #                          currently active machine?
    @pyqtSlot(str, str, "QVariantMap")
    def requestWriteSelectionToDevice(self, device_id, file_name, kwargs):
        if not Selection.hasSelection():
            return

        filter_by_machine = kwargs.get("filter_by_machine", False)
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        Application.getInstance().callLater(self._writeToDevice, Selection.getSelectedObject(0), device_id, file_name, filter_by_machine)

    def _onActiveDeviceChanged(self):
        self.activeDeviceChanged.emit()

    ##  Writes the specified node to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param node \type{SceneNode} The root of a tree of scene nodes that
    #   should be written to the device.
    #   \param device_id \type{string} The handle of the device to write to.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param filter_by_machine \type{bool} If the file name is ignored, should
    #   the file format that the output device chooses be limited to the formats
    #   that are supported by the currently active machine?
    def _writeToDevice(self, node, device_id, file_name, filter_by_machine):
        device = self._device_manager.getOutputDevice(device_id)
        if not device:
            return

        try:
            device.requestWrite(node, file_name, filter_by_machine)
        except OutputDeviceError.UserCanceledError:
            pass
        except OutputDeviceError.DeviceBusyError:
            pass
        except OutputDeviceError.WriteRequestFailedError as e:
            message = Message(str(e))
            message.show()

def createOutputDeviceManagerProxy(engine, script_engine):
    return OutputDeviceManagerProxy()
