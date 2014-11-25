from Cura.Signal import Signal

##  Abstract base class for all input devices
class InputDevice(object):
    def __init__(self):
        super(InputDevice, self).__init__()
        self.event = Signal()

    ## Signal. Emitted whenever the device produces an event.
    #  \param event The event that is emitted.
    event = None
