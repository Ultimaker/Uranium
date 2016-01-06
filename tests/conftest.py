# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

from UM.Application import Application

class FixtureApplication(Application):
    def __init__(self):
        Application._instance = None
        super().__init__("test", "1.0")

    def functionEvent(self, event):
        pass

    def parseCommandLine(self):
        pass

@pytest.fixture()
def application():
    return FixtureApplication()

