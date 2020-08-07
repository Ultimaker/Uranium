# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import cast
from unittest.mock import MagicMock

import pytest
import Arcus #Prevents error: "PyCapsule_GetPointer called with incorrect name" with conflicting SIP configurations between Arcus and PyQt: Import Arcus first!
from UM.Qt.QtApplication import QtApplication #QTApplication import is required, even though it isn't used.
from UM.Application import Application
from UM.Qt.QtRenderer import QtRenderer
from UM.Signal import Signal
from UM.PluginRegistry import PluginRegistry
from UM.VersionUpgradeManager import VersionUpgradeManager


# This mock application must extend from Application and not QtApplication otherwise some QObjects are created and
# a segfault is raised.
class FixtureApplication(Application):
    engineCreatedSignal = Signal()

    def __init__(self):
        super().__init__(name = "test", version = "1.0", api_version = "7.3.0")
        super().initialize()
        Signal._signalQueue = self

    def functionEvent(self, event):
        event.call()

    def parseCommandLine(self):
        pass

    def processEvents(self):
        pass

    def getRenderer(self):
        return MagicMock()

    def showMessage(self, message):
        pass

@pytest.fixture()
def application():
    # Since we need to use it more that once, we create the application the first time and use its instance the second
    application = FixtureApplication.getInstance()
    if application is None:
        application = FixtureApplication()
    return application

@pytest.fixture()
def plugin_registry(application):
    PluginRegistry._PluginRegistry__instance = None
    plugin_registry = PluginRegistry(application)
    plugin_registry._plugin_locations = [] # Clear pre-defined plugin locations
    return plugin_registry

@pytest.fixture()
def upgrade_manager(application):
    VersionUpgradeManager._VersionUpgradeManager__instance = None
    upgrade_manager = VersionUpgradeManager(application)
    return upgrade_manager

