# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject


##  Abstract base class for all input devices (Human Input Devices)
#   Examples of this are mouse & keyboard
@signalemitter
class InputDevice(PluginObject):
    def __init__(self):
        super().__init__()

    ##  Emitted whenever the device produces an event.
    #   All actions performed with the device should be seen as an event.
    #   \param event The event that is emitted.
    event = Signal()
