# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter

@signalemitter
class SettingInstance:
    def __init__(self, definition, container, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._definition = definition
        self._container = container

    def getDefinition(self):
        return self._definition

    def getContainer(self):
        return self._container

    def getValue(self):
        pass

    def setValue(self):
        pass

    valueChanged = Signal()

    def isEnabled(self):
        pass

    def setEnabled(self):
        pass

    enabledChanged = Signal()

    def getValidationState(self):
        pass

    def setValidationState(self):
        pass

    validationStateChanged = Signal()

    def isVisible(self):
        pass

    def setVisible(self, visible):
        pass

    visibleChanged = Signal()
