# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List, Optional

from UM.FileHandler.FileHandler import FileHandler #For typing.
from UM.Scene.SceneNode import SceneNode #For typing.
from UM.Signal import Signal, signalemitter


@signalemitter
class OutputDevice():
    """Base class for output devices.

    This class provides a base class for output devices. An output device can be
    anything we want to output to, like a local file, an USB connected printer but
    also an HTTP web service.

    Each subclass must implement requestWrite(). requestWrite() is expected to raise
    errors from OutputDeviceError when certain conditions occur, like insufficient
    permissions. For the rest, output device subclasses are completely free to implement
    writing however they want, though you should emit writeStarted and related signals
    whenever certain events happen related to the write process.

    For example, when implementing a web service as output device, it would be completely
    acceptable to show a login dialog when calling requestWrite() if there are no saved
    login credentials.
    """

    def __init__(self, device_id: str, **kwargs: str) -> None:
        super().__init__()

        self._id = device_id
        self._name = "Unknown Device"
        self._short_description = "Unknown Device"
        self._description = "Do something with an unknown device"
        self._icon_name = "generic_device"
        self._priority = 0

    metaDataChanged = Signal()

    def getId(self) -> str:
        """Get the device id"""

        return self._id

    def getName(self) -> str:
        """Get a human-readable name for this device."""

        return self._name

    def setName(self, name: str) -> None:
        """Set the human-readable name of this device.

        :param name: The new name of this device.
        """

        if name != self._name:
            self._name = name
            self.metaDataChanged.emit(self)

    def getShortDescription(self) -> str:
        """Get a short description for this device.

        The short description can be used as a button label or similar
        and should thus be only a few words at most. For example,
        "Save to File", "Print with USB".
        """

        return self._short_description

    def setShortDescription(self, description: str) -> None:
        """Set the short description for this device.

        :param description: The new short description to set.
        """

        if description != self._short_description:
            self._short_description = description
            self.metaDataChanged.emit(self)

    def getDescription(self) -> str:
        """Get a full description for this device.

        The full description describes what would happen when writing
        to this device. For example, "Save to Removable Drive /media/sdcard",
        "Upload to YouMagine with account User".
        """

        return self._description

    def setDescription(self, description: str) -> None:
        """Set the full description for this device.

        :param description: The description of this device.
        """

        if description != self._description:
            self._description = description
            self.metaDataChanged.emit(self)

    def getIconName(self) -> str:
        """Get the name of an icon that can be used to identify this device.

        This icon should be available in the theme.
        """

        return self._icon_name

    def setIconName(self, name: str) -> None:
        """Set the name of an icon to identify this device.

        :param name: The name of the icon to use.
        """

        if name != self._icon_name:
            self._icon_name = name
            self.metaDataChanged.emit(self)

    def getPriority(self) -> int:
        """The priority of this device.

        Priority indicates which device is most likely to be used as the
        default device to write to. It should be a number and higher numbers
        indicate that the device should be preferred over devices with
        lower numbers.
        """

        return self._priority

    def setPriority(self, priority: int) -> None:
        """Set the priority of this device.

        :param priority: The priority to use.
        """

        if priority != self._priority:
            self._priority = priority
            self.metaDataChanged.emit(self)

    def requestWrite(self, nodes: List[SceneNode], file_name: Optional[str] = None, limit_mimetypes: bool = False,
                     file_handler: Optional[FileHandler] = None, filter_by_machine: bool = False,
                     **kwargs: str) -> None:
        """Request performing a write operation on this device.

        This method should be implemented by subclasses. It should write the
        given SceneNode forest to a destination relevant for the device. It is
        recommended to perform the actual writing asynchronously and rely on
        the write signals to properly indicate state.

        :param nodes: A collection of scene nodes that should be written to the
        device.
        :param file_name: A suggestion for the file name to write
        to. Can be freely ignored if providing a file name makes no sense.
        :param limit_mimetypes: Limit output to these mime types.
        :param file_handler: The filehandler to use to write the file with.
        :param kwargs: Keyword arguments.
        :exception OutputDeviceError.WriteRequestFailedError
        """

        raise NotImplementedError("requestWrite needs to be implemented")

    writeStarted = Signal()
    writeProgress = Signal()
    writeFinished = Signal()
    writeError = Signal()
    writeSuccess = Signal()
