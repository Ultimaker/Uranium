# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest
import os

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.PluginError import PluginNotFoundError, InvalidMetaDataError
from UM.Version import Version


valid_plugin_json_data = [
    "{\"name\": \"TestPlugin1\", \"api\": 5, \"version\": \"1.0.0\"}",
    "{\"name\": \"TestPlugin2\", \"supported_sdk_versions\": [5], \"version\": \"1.0.0\"}",
    "{\"name\": \"TestPlugin3\", \"api\": 5, \"supported_sdk_versions\": [5], \"version\": \"1.0.0\"}",
    "{\"name\": \"TestPlugin3\", \"supported_sdk_versions\": [5, 6, \"2\"], \"version\": \"1.0.0\"}"
]

invalid_plugin_json_data = [
    "",  # Invalid JSON
    "{\"name\": \"TestPlugin1\", \"api\": 5}",  # No version
    "{\"name\": \"TestPlugin2\", \"version\": \"1.0.0\"}"  # No API or supported_sdk_version set.
]


class FixtureRegistry(PluginRegistry):

    def __init__(self, application: "Application"):
        PluginRegistry._PluginRegistry__instance = None
        super().__init__(application)
        self._api_version = Version("5.5.0")

    def registerTestPlugin(self, plugin):
        self._test_plugin = plugin

    def getTestPlugin(self):
        if hasattr(self, "_test_plugin"):
            return self._test_plugin

        return None


@pytest.fixture
def registry(application):
    registry = FixtureRegistry(application)
    registry.addPluginLocation(os.path.dirname(os.path.abspath(__file__)))
    registry.addType("test", registry.registerTestPlugin)
    return registry


class TestPluginRegistry():
    def test_metaData(self, registry):
        metadata = registry.getMetaData("TestPlugin")
        assert metadata == {"id": "TestPlugin",
                            "plugin": {"name": "TestPlugin",
                                       "api": 5,
                                       "supported_sdk_versions": [Version(5)],
                                       "version": "1.0.0"},
                            "location": os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/TestPlugin"),
                            }

    def test_getPluginLocation(self, registry):
        # Plugin is not loaded yet, so it should raise a KeyError
        with pytest.raises(KeyError):
            registry.getPluginPath("TestPlugin")

        registry.loadPlugin("TestPlugin")
        assert registry.getPluginPath("TestPlugin") == os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/TestPlugin")

    @pytest.mark.parametrize("plugin_data", valid_plugin_json_data)
    def test_valid_plugin_json(self, plugin_data, registry):
        registry._parsePluginInfo("beep", plugin_data, {})

    @pytest.mark.parametrize("plugin_data", invalid_plugin_json_data)
    def test_invalid_plugin_json(self, plugin_data, registry):
        with pytest.raises(InvalidMetaDataError):
            registry._parsePluginInfo("beep", plugin_data, {})

    def test_load(self, registry):
        registry.loadPlugin("TestPlugin")

        assert registry.getTestPlugin().getPluginId() == "TestPlugin"
    
    def test_loadNested(self, registry):
        registry.loadPlugin("TestPlugin2")

        assert registry.getTestPlugin().getPluginId() == "TestPlugin2"
        
    def test_findAllPlugins(self, registry):
        names = registry._findInstalledPlugins()
        assert sorted(names) == ["EmptyPlugin", "OldTestPlugin", "PluginNoVersionNumber", "TestPlugin", "TestPlugin2"]
        
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
        with pytest.raises(PluginNotFoundError):
            registry.getPluginObject("EmptyPlugin")

    def test_invalidVersionNumber(self, registry):
        registry.loadPlugin("PluginNoVersionNumber")
        assert registry.getTestPlugin() is None

    def test_ignoreOldApi(self, registry):
        registry.loadPlugin("OldTestPlugin")
        assert registry.getTestPlugin() is None

    def test_isPluginApiVersionCompatible(self, registry):
        # Same version is compatible
        assert registry._isPluginApiVersionCompatible(registry._api_version)

        # Lower major version is not compatible
        api_version = Version("4.0.0")
        assert not registry._isPluginApiVersionCompatible(api_version)

        # Higher major version is not compatible
        api_version = Version("6.0.0")
        assert not registry._isPluginApiVersionCompatible(api_version)

        # Same major version but higher minor version is not compatible
        api_version = Version("5.7.0")
        assert not registry._isPluginApiVersionCompatible(api_version)

        # Same major version but lower minor version is compatible
        api_version = Version("5.3.0")
        assert registry._isPluginApiVersionCompatible(api_version)

        # Same major version but different patch version should not matter, it should be compatible
        api_version = Version("5.0.5")
        assert registry._isPluginApiVersionCompatible(api_version)
