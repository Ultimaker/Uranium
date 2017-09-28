# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Application import Application
from UM.i18n import i18nCatalog
from UM.Scene.Selection import Selection
from UM.Message import Message
from UM.OutputDevice import OutputDeviceError
from UM.Logger import Logger

catalog = i18nCatalog("uranium")

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
    #   \param kwargs Keyword arguments:
    #       limit_mimetypes: Limit the possible mimetypes to use for writing to these types.
    @pyqtSlot(str, str, "QVariantMap")
    def requestWriteToDevice(self, device_id, file_name, kwargs):
        limit_mimetypes = kwargs.get("limit_mimetypes", None)
        file_type = kwargs.get("file_type", "mesh")
        preferred_mimetype = kwargs.get("preferred_mimetype", None)
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        Application.getInstance().callLater(self._writeToDevice, [Application.getInstance().getController().getScene().getRoot()], device_id, file_name, limit_mimetypes, file_type, preferred_mimetype = preferred_mimetype)

    ##  Request that the current selection is written to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param device_id \type{string} The handle of the device to write to.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param kwargs Keyword arguments:
    #       limit_mimetypes: Limit the possible mimetypes to use for writing to these types.
    @pyqtSlot(str, str, "QVariantMap")
    def requestWriteSelectionToDevice(self, device_id, file_name, kwargs):
        if not Selection.hasSelection():
            return

        limit_mimetypes = kwargs.get("limit_mimetypes", False)
        preferred_mimetype = kwargs.get("preferred_mimetype", None)
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        Application.getInstance().callLater(self._writeToDevice, Selection.getAllSelectedObjects(), device_id, file_name, limit_mimetypes, preferred_mimetype = preferred_mimetype)

    def _onActiveDeviceChanged(self):
        self.activeDeviceChanged.emit()

    ##  Writes the specified node to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param nodes The scene nodes that must be written to the device.
    #   \param device_id \type{string} The handle of the device to write to.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param limit_mimetypes: Limit the possible mimetypes to use for writing to these types.
    #   \param file_handler What file handler to get the writer from.
    def _writeToDevice(self, nodes, device_id, file_name, limit_mimetypes, file_type = "mesh", **kwargs):
        device = self._device_manager.getOutputDevice(device_id)
        if not device:
            return
        if file_type == "mesh":
            file_handler = Application.getInstance().getMeshFileHandler()
        elif file_type == "workspace":
            file_handler = Application.getInstance().getWorkspaceFileHandler()
        else:
            # Unrecognised type
            file_handler = None

        try:
            device.requestWrite(nodes, file_name, limit_mimetypes, file_handler, **kwargs)
        except OutputDeviceError.UserCanceledError:
            pass
        except OutputDeviceError.DeviceBusyError:
            pass
        except OutputDeviceError.WriteRequestFailedError as e:
            message = Message(str(e), title = catalog.i18nc("@info:title", "Error"))
            message.show()
        except Exception as e:
            Logger.logException("e", "Unable to write to file %s: %s", file_name, e)


def createOutputDeviceManagerProxy(engine, script_engine):
    return OutputDeviceManagerProxy()
