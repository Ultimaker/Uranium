# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlEngine, QJSEngine #For typing.
from typing import List, Mapping, Optional, TYPE_CHECKING

from UM.Application import Application
from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.Message import Message
from UM.OutputDevice import OutputDeviceError
import UM.Qt.QtApplication
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection

if TYPE_CHECKING:
    from UM.FileHandler.FileHandler import FileHandler
    from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager

catalog = i18nCatalog("uranium")

class OutputDeviceManagerProxy(QObject):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._device_manager = Application.getInstance().getOutputDeviceManager() #type: OutputDeviceManager
        self._device_manager.activeDeviceChanged.connect(self._onActiveDeviceChanged)
        self._onActiveDeviceChanged()

    activeDeviceChanged = pyqtSignal()
    
    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDevice(self) -> str:
        return self._device_manager.getActiveDevice().getId()

    @pyqtSlot(str)
    def setActiveDevice(self, device_id: str) -> None:
        self._device_manager.setActiveDevice(device_id)

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceName(self) -> str:
        return self._device_manager.getActiveDevice().getName()

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceIconName(self) -> str:
        return self._device_manager.getActiveDevice().getIconName()

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceShortDescription(self) -> str:
        return self._device_manager.getActiveDevice().getShortDescription()

    @pyqtProperty(str, notify = activeDeviceChanged)
    def activeDeviceDescription(self) -> str:
        return self._device_manager.getActiveDevice().getDescription()

    @pyqtSlot(str)
    def addManualDevice(self, address: str) -> None:
        self._device_manager.addManualDevice(address)

    @pyqtSlot(str)
    @pyqtSlot(str, str)
    def removeManualDevice(self, key: str, address: str = None) -> None:
        self._device_manager.removeManualDevice(key, address)

    ##  Request that the current scene is written to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param device_id The handle of the device to write to.
    #   \param file_name A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param kwargs Keyword arguments:
    #       limit_mimetypes: Limit the possible mimetypes to use for writing to these types.
    @pyqtSlot(str, str, "QVariantMap")
    def requestWriteToDevice(self, device_id: str, file_name: str, kwargs: Mapping[str, str]) -> None:
        limit_mimetypes = kwargs.get("limit_mimetypes", None)
        file_type = kwargs.get("file_type", "mesh")
        preferred_mimetypes = kwargs.get("preferred_mimetypes", None)
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        Application.getInstance().callLater(self._writeToDevice, [Application.getInstance().getController().getScene().getRoot()], device_id, file_name, limit_mimetypes, file_type, preferred_mimetypes = preferred_mimetypes)

    ##  Request that the current selection is written to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param device_id The handle of the device to write to.
    #   \param file_name A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param kwargs Keyword arguments:
    #       limit_mimetypes: Limit the possible mimetypes to use for writing to these types.
    @pyqtSlot(str, str, "QVariantMap")
    def requestWriteSelectionToDevice(self, device_id: str, file_name: str, kwargs: Mapping[str, str]) -> None:
        if not Selection.hasSelection():
            return

        limit_mimetypes = kwargs.get("limit_mimetypes", False)
        preferred_mimetypes = kwargs.get("preferred_mimetypes", None)
        # On Windows, calling requestWrite() on LocalFileOutputDevice crashes when called from a signal
        # handler attached to a QML MenuItem. So instead, defer the call to the next run of the event 
        # loop, since that does work.
        Application.getInstance().callLater(self._writeToDevice, Selection.getAllSelectedObjects(), device_id, file_name, limit_mimetypes, preferred_mimetypes = preferred_mimetypes)

    def _onActiveDeviceChanged(self) -> None:
        self.activeDeviceChanged.emit()

    ##  Writes the specified node to the output device.
    #
    #   The output device to write with will be selected based on the device_id.
    #   A file format is chosen from the list of available file formats by the
    #   output device.
    #
    #   \param nodes The scene nodes that must be written to the device.
    #   \param device_id The handle of the device to write to.
    #   \param file_name A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param limit_mimetypes: Limit the possible mimetypes to use for writing to these types.
    #   \param file_type What file handler to get the writer from.
    def _writeToDevice(self, nodes: List[SceneNode], device_id: str, file_name: str, limit_mimetypes: bool, file_type: str = "mesh", **kwargs) -> None:
        device = self._device_manager.getOutputDevice(device_id)
        if not device:
            return
        file_handler = None #type: Optional[FileHandler]
        if file_type == "mesh":
            file_handler = UM.Qt.QtApplication.QtApplication.getInstance().getMeshFileHandler()
        elif file_type == "workspace":
            file_handler = UM.Qt.QtApplication.QtApplication.getInstance().getWorkspaceFileHandler()

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


def createOutputDeviceManagerProxy(engine: QQmlEngine, script_engine: QJSEngine) -> OutputDeviceManagerProxy:
    return OutputDeviceManagerProxy()
