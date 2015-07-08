# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, SignalEmitter

class OutputDevice(SignalEmitter):
    def __init__(self, device_id):
        super().__init__()

        self._id = device_id
        self._name = "Unknown Device"
        self._short_description = "Unknown Device"
        self._description = "Do something with an unknown device"
        self._icon_name = "generic_device"
        self._supported_mime_types = []
        self._priority = 0

    metaDataChanged = Signal()

    def getId(self):
        return self._id

    def getName(self):
        return self._name

    def setName(self, name):
        if name != self._name:
            self._name = name
            self.metaDataChanged.emit(self)

    def getShortDescription(self):
        return self._short_description

    def setShortDescription(self, description):
        if description != self._short_description:
            self._short_description = description
            self.metaDataChanged.emit(self)

    def getDescription(self):
        return self._description

    def setDescription(self, description):
        if description != self._description:
            self._description = description
            self.metaDataChanged.emit(self)

    def getIconName(self):
        return self._icon_name

    def setIconName(self, name):
        if name != self._icon_name:
            self._icon_name = name
            self.metaDataChanged.emit(self)

    def getSupportedMimeTypes(self):
        return self._supported_mime_types

    def setSupportedMimeTypes(self, types):
        if types != self._supported_mime_types:
            self._supported_mime_types = types
            self.metaDataChanged.emit(self)

    def getPriority(self):
        return self._priority

    def setPriority(self, priority):
        if priority != self._priority:
            self._priority = priority
            self.metaDataChanged.emit(self)

    def requestWrite(self, node):
        raise NotImplementedError("requestWrite needs to be implemented")

    writeStarted = Signal()
    writeProgress = Signal()
    writeFinished = Signal()
    writeError = Signal()
    writeSuccess = Signal()
