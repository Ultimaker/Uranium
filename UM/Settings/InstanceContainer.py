# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter

from . import ContainerInterface

@signalemitter
class InstanceContainer(ContainerInterface.ContainerInterface):
    def __init__(self):
        pass

    valueChanged = Signal()
