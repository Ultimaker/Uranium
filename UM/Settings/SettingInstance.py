# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter

##  Encapsulates all state of a setting.
#
#
@signalemitter
class SettingInstance:
    ##  Constructor.
    #
    #   \param definition The SettingDefinition object this is an instance of.
    #   \param container The container of this instance. Defaults to None.
    def __init__(self, definition, container = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._definition = definition
        self._container = container

    ##  Get the SettingDefintion of this instance.
    def getDefinition(self):
        return self._definition

    ##  Get the container of this instance.
    def getContainer(self):
        return self._container

    ##  Get the value of this instance.
    def getValue(self):
        pass

    ##  Set the value of this instance.
    def setValue(self, value):
        pass

    ##  Emitted whenever this instance's value changes.
    valueChanged = Signal()

    ##  Check if this instance is enabled.
    def isEnabled(self):
        pass

    ##  Set if this instance should be enabled.
    def setEnabled(self, enabled):
        pass

    ##  Emitted whenever this instance's enabled property changes.
    enabledChanged = Signal()

    ##  Get the state of validation of this instance.
    def getValidationState(self):
        pass

    ##  Set the state of validation of this instance.
    def setValidationState(self):
        pass

    ##  Emitted whenever this instance's validationState property changes.
    validationStateChanged = Signal()

    ##  Check if this instance should be visible.
    def isVisible(self):
        pass

    ##  Set if this instance should be visible.
    def setVisible(self, visible):
        pass

    ##  Emitted whenever this instance's visible property changes.
    visibleChanged = Signal()
