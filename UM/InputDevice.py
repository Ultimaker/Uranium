# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject


@signalemitter
class InputDevice(PluginObject):
    """Abstract base class for all input devices (Human Input Devices)

    Examples of this are mouse & keyboard
    """

    def __init__(self) -> None:
        super().__init__()

    event = Signal()
    """Emitted whenever the device produces an event.

    All actions performed with the device should be seen as an event.
    :param event: The event that is emitted.
    """
