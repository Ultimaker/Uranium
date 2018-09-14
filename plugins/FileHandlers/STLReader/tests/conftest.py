# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest
import Arcus #Prevents error: "PyCapsule_GetPointer called with incorrect name" with conflicting SIP configurations between Arcus and PyQt: Import Arcus first!
from UM.Qt.QtApplication import QtApplication # QT application import is required, even though it isn't used.
from UM.Application import Application
from UM.Signal import Signal

# This mock application must extend from Application and not QtApplication otherwise some QObjects are created and
# a segfault is raised.
class FixtureApplication(Application):
    def __init__(self):
        super().__init__(name = "test", version = "1.0")
        super().initialize()
        Signal._signalQueue = self

    def functionEvent(self, event):
        event.call()

    def parseCommandLine(self):
        pass

    def processEvents(self):
        pass

@pytest.fixture()
def application():
    # Since we need to use it more that once, we create the application the first time and use its instance the second
    application = FixtureApplication.getInstance()
    if application is None:
        application = FixtureApplication()
    return application

