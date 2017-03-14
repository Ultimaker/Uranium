# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter


##  Base class for output devices.
#
#   This class provides a base class for output devices. An output device can be
#   anything we want to output to, like a local file, an USB connected printer but
#   also an HTTP web service.
#
#   Each subclass must implement requestWrite(). requestWrite() is expected to raise
#   errors from OutputDeviceError when certain conditions occur, like insufficient
#   permissions. For the rest, output device subclasses are completely free to implement
#   writing however they want, though you should emit writeStarted and related signals
#   whenever certain events happen related to the write process.
#
#   For example, when implementing a web service as output device, it would be completely
#   acceptable to show a login dialog when calling requestWrite() if there are no saved
#   login credentials.
@signalemitter
class OutputDevice():
    def __init__(self, device_id, **kwargs):
        super().__init__()

        self._id = device_id
        self._name = "Unknown Device"
        self._short_description = "Unknown Device"
        self._description = "Do something with an unknown device"
        self._icon_name = "generic_device"
        self._priority = 0

    metaDataChanged = Signal()

    ##  Get the device id
    def getId(self):
        return self._id

    ##  Get a human-readable name for this device.
    def getName(self):
        return self._name

    ##  Set the human-readable name of this device.
    #
    #   \param name The new name of this device.
    def setName(self, name):
        if name != self._name:
            self._name = name
            self.metaDataChanged.emit(self)

    ##  Get a short description for this device.
    #
    #   The short description can be used as a button label or similar
    #   and should thus be only a few words at most. For example,
    #   "Save to File", "Print with USB".
    def getShortDescription(self):
        return self._short_description

    ##  Set the short description for this device.
    #
    #   \param description The new short description to set.
    def setShortDescription(self, description):
        if description != self._short_description:
            self._short_description = description
            self.metaDataChanged.emit(self)

    ##  Get a full description for this device.
    #
    #   The full description describes what would happen when writing
    #   to this device. For example, "Save to Removable Drive /media/sdcard",
    #   "Upload to YouMagine with account User".
    def getDescription(self):
        return self._description

    ##  Set the full description for this device.
    #
    #   \param description The description of this device.
    def setDescription(self, description):
        if description != self._description:
            self._description = description
            self.metaDataChanged.emit(self)

    ##  Get the name of an icon that can be used to identify this device.
    #
    #   This icon should be available in the theme.
    def getIconName(self):
        return self._icon_name

    ##  Set the name of an icon to identify this device.
    #
    #   \param name The name of the icon to use.
    def setIconName(self, name):
        if name != self._icon_name:
            self._icon_name = name
            self.metaDataChanged.emit(self)

    ##  The priority of this device.
    #
    #   Priority indicates which device is most likely to be used as the
    #   default device to write to. It should be a number and higher numbers
    #   indicate that the device should be preferred over devices with
    #   lower numbers.
    def getPriority(self):
        return self._priority

    ##  Set the priority of this device.
    #
    #   \param priority \type{int} The priority to use.
    def setPriority(self, priority):
        if priority != self._priority:
            self._priority = priority
            self.metaDataChanged.emit(self)

    ##  Request performing a write operation on this device.
    #
    #   This method should be implemented by subclasses. It should write the
    #   given SceneNode forest to a destination relevant for the device. It is
    #   recommended to perform the actual writing asynchronously and rely on
    #   the write signals to properly indicate state.
    #
    #   \param nodes A collection of scene nodes that should be written to the
    #   device.
    #   \param file_name \type{string} A suggestion for the file name to write
    #   to. Can be freely ignored if providing a file name makes no sense.
    #   \param limit_mimetype Limit output to these mime types.
    #   \param file_handler The filehandler to use to write the file with.
    #   \param kwargs Keyword arguments.
    #   \exception OutputDeviceError.WriteRequestFailedError
    def requestWrite(self, nodes, file_name = None, limit_mimetypes = False, file_handler = None, **kwargs):
        raise NotImplementedError("requestWrite needs to be implemented")

    writeStarted = Signal()
    writeProgress = Signal()
    writeFinished = Signal()
    writeError = Signal()
    writeSuccess = Signal()
