# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import cast
from unittest.mock import MagicMock

import pytest
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
        super().__init__(name="test", version="1.0", latest_url="", api_version="8.4.0")
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

def pytest_collection_modifyitems(items):
    """ Modifies test items in place to ensure test classes run in a given order.
        See: https://stackoverflow.com/questions/70738211/run-pytest-classes-in-custom-order/70758938#70758938
    """
    CLASS_ORDER = ["TestActiveToolProxy"]  # All classes that need to be run in-order, in that order -- all others will run _before_.
    class_mapping = {item: (item.cls.__name__ if item.cls else "") for item in items}

    sorted_items = items.copy()
    # Iteratively move tests of each class to the end of the test queue
    for class_ in CLASS_ORDER:
        sorted_items = [it for it in sorted_items if class_mapping[it] != class_] + [
            it for it in sorted_items if class_mapping[it] == class_
        ]
    items[:] = sorted_items
