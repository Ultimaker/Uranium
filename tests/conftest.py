# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

from UM.Application import Application
from UM.Signal import Signal

class FixtureApplication(Application):
    def __init__(self):
        Application._instance = None
        super().__init__("test", "1.0")
        Signal._app = self

    def functionEvent(self, event):
        event.call()

    def parseCommandLine(self):
        pass

@pytest.fixture()
def application():
    return FixtureApplication()

