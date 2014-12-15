from UM.Signal import Signal, SignalEmitter

##  Abstract base class for all input devices
class InputDevice(SignalEmitter):
    def __init__(self):
        super().__init__()

    ## Emitted whenever the device produces an event.
    #  \param event The event that is emitted.
    event = Signal()
