# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

#!/usr/bin/env python2

import pytest
import os

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.PluginError import PluginNotFoundError

class FixtureRegistry(PluginRegistry):
    def registerTestPlugin(self, plugin):
        self._test_plugin = plugin

    def getTestPlugin(self):
        if hasattr(self, "_test_plugin"):
            return self._test_plugin

        return None

@pytest.fixture
def registry(application):
    registry = FixtureRegistry()
    registry.addPluginLocation(os.path.dirname(os.path.abspath(__file__)))
    registry.addType("test", registry.registerTestPlugin)
    registry.setApplication(application)
    return registry

class TestPluginRegistry():
    def test_metaData(self, registry):
        metadata = registry.getMetaData("TestPlugin")
        assert metadata == { "id": "TestPlugin", "plugin": { "name": "TestPlugin", "api": 4, "version": "1.0.0" } }

    def test_load(self, registry):
        registry.loadPlugin("TestPlugin")

        assert registry.getTestPlugin().getPluginId() == "TestPlugin"
    
    def test_loadNested(self, registry):
        registry.loadPlugin("TestPlugin2")

        assert registry.getTestPlugin().getPluginId() == "TestPlugin2"
        
    def test_findAllPlugins(self, registry):
        names = registry._findAllPlugins()
        assert sorted(names) == ["EmptyPlugin","OldTestPlugin", "PluginNoVersionNumber", "TestPlugin", "TestPlugin2"]
        
    def test_pluginNotFound(self, registry):
        with pytest.raises(PluginNotFoundError):
            registry.loadPlugin("NoSuchPlugin")

    def test_disabledPlugin(self, registry):
        # Disabled plugin should not be loaded
        registry._disabled_plugins = ["TestPlugin"]
        registry.loadPlugin("TestPlugin")
        assert registry.getTestPlugin() is None

        # Other plugins should load.
        registry.loadPlugin("TestPlugin2")
        assert registry.getTestPlugin().getPluginId() == "TestPlugin2"

    def test_emptyPlugin(self, registry):
        registry.loadPlugin("EmptyPlugin")
        with pytest.raises(KeyError):
            registry.getPluginObject("EmptyPlugin")

    def test_invalidVersionNumber(self, registry):
        registry.loadPlugin("PluginNoVersionNumber")
        assert registry.getTestPlugin() is None

    def test_ignoreOldApi(self, registry):
        registry.loadPlugin("OldTestPlugin")
        assert registry.getTestPlugin() is None
