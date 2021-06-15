# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from unittest.mock import patch, mock_open, MagicMock

import pytest
import os

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.PluginError import PluginNotFoundError, InvalidMetaDataError
from UM.Version import Version
import json


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
        self._plugin_config_filename = "test_file"

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

    def test_init(self, registry):
        # Without loading anything, this shouldn't fail.
        registry.initializeBeforePluginsAreLoaded()
        registry.initializeAfterPluginsAreLoaded()

    def test_savePluginData(self, registry):
        with patch("builtins.open", mock_open()) as mock_file:
            registry._savePluginData()
            handle = mock_file()

            writen_data = json.loads(handle.write.call_args[0][0])
            expected_data = json.loads('{"disabled": [], "to_install": {}, "to_remove": []}')
            assert writen_data == expected_data

    def test_uninstallPlugin(self, registry):
        with patch("builtins.open", mock_open()) as mock_file:
            registry.uninstallPlugin("BLARG")  # It doesn't exist, so don't do anything.
            handle = mock_file()
            handle.write.assert_not_called()

            registry.loadPlugins()
            registry.uninstallPlugin("TestPlugin")
            writen_data = json.loads(handle.write.call_args[0][0])
            expected_data = json.loads('{"disabled": [], "to_install": {}, "to_remove": ["TestPlugin"]}')
            assert writen_data == expected_data

            assert "TestPlugin" not in registry.getInstalledPlugins()

    def test_isBundledPlugin(self, registry):
        assert registry.isBundledPlugin("NOPE") == False
        # The result will be cached the second time, so ensure we test that path as well.
        assert registry.isBundledPlugin("NOPE") == False

    def test_addSupportedPluginExtension(self, registry):
        registry.addSupportedPluginExtension("blarg", "zomg")
        description_added = False
        extension_added = False

        for file_type in registry.supportedPluginExtensions:
            if "blarg" in file_type:
                extension_added = True
            if "zomg" in file_type:
                description_added = True

        assert extension_added
        assert description_added

    def test_installPlugin(self, registry):
        path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/UraniumExampleExtensionPlugin.umplugin")
        if not path.startswith("/"):
            path = "/" + path
        path = "file://" + path
        result = registry.installPlugin(path)
        assert result.get("status") == "ok"

        # Ensure that the plugin is now marked as installed (although the actual installation happens on next restart!)
        assert "UraniumExampleExtensionPlugin" in registry.getInstalledPlugins()

    def test__installPlugin(self, registry):
        # This tests that the unpacking of the plugin doesn't fail.
        path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/UraniumExampleExtensionPlugin.umplugin")
        registry._installPlugin("UraniumExampleExtensionPlugin", path)

    def test__subsetInDict(self, registry):
        assert not registry._subsetInDict({}, {"test": "test"})
        assert not registry._subsetInDict( {"test": "omg"}, {"test": "test"})
        assert registry._subsetInDict({"test": "test", "zomg": "omg"}, {"test": "test"})

    def test_requiredPlugins(self, registry):
        assert registry.checkRequiredPlugins(["EmptyPlugin", "OldTestPlugin", "PluginNoVersionNumber", "TestPlugin", "TestPlugin2"])

        assert not registry.checkRequiredPlugins(["TheNotLoadedPlugin"])

    def test_metaData(self, registry):
        expected_metadata = {"id": "TestPlugin",
                            "plugin": {"name": "TestPlugin",
                                       "api": 5,
                                       "supported_sdk_versions": [Version(5)],
                                       "version": "1.0.0",
                                        "i18n-catalog": "bla",
                                       "description": "test"},
                            "location": os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/TestPlugin"),
                            }

        metadata = registry.getMetaData("TestPlugin")

        assert metadata == expected_metadata
        registry.loadPlugins()
        all_metadata = registry.getAllMetaData()
        test_plugin_found = False
        for plugin_metadata in all_metadata:
            if plugin_metadata.get("id") == "TestPlugin":
                test_plugin_found = True
                assert plugin_metadata == metadata
        assert test_plugin_found

    def test_getPluginLocation(self, registry):
        # Plugin is not loaded yet, so it should raise a KeyError
        with pytest.raises(KeyError):
            registry.getPluginPath("TestPlugin")

        registry.loadPlugin("TestPlugin")
        assert registry.getPluginPath("TestPlugin") == os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/TestPlugin")

    @pytest.mark.parametrize("plugin_data", valid_plugin_json_data)
    def test_validPluginJson(self, plugin_data, registry):
        registry._parsePluginInfo("beep", plugin_data, {})

    @pytest.mark.parametrize("plugin_data", invalid_plugin_json_data)
    def test_invalidPluginJson(self, plugin_data, registry):
        with pytest.raises(InvalidMetaDataError):
            registry._parsePluginInfo("beep", plugin_data, {})


    def test_populateMetadata_unknownPlugin(self, registry):
        assert not registry._populateMetaData("TheGreatUnknown")


    def test_populateMetadata_locationNotFound(self, registry):
        registry._findPlugin = MagicMock(return_value = True)
        registry._locatePlugin = MagicMock(return_value = None)
        assert not registry._populateMetaData("Waldo")

    def test_populateMetadata_PluginWitIdentityCrisis(self, registry):
        registry._findPlugin = MagicMock(return_value="Not a plugin, but i was found!")
        registry._locatePlugin = MagicMock(return_value="yaaay")

        with pytest.raises(InvalidMetaDataError):
            registry._populateMetaData("Whatever")

    def test_populateMetadata_PluginWithNoMetadata(self, registry):
        plugin = MagicMock(name = "plugin")
        plugin.getMetaData = MagicMock(return_value = None)
        registry._findPlugin = MagicMock(return_value= plugin)
        registry._locatePlugin = MagicMock(return_value="yaaay")
        registry._parsePluginInfo = MagicMock(return_value = None)
        with pytest.raises(InvalidMetaDataError):
            with patch("builtins.open", mock_open()) as mock_file:
                registry._populateMetaData("Whatever")

    def test_getInstalledPlugins(self, registry):
        assert registry.getInstalledPlugins() == []  # Should be empty by default
        registry.loadPlugins()
        # All the plugins in this test should be marked as installed.
        assert sorted(registry.getInstalledPlugins()) == sorted(['PluginNoVersionNumber', 'EmptyPlugin', 'TestPlugin', 'TestPlugin2'])

    def test_isActivePlugin(self, registry):
        # The plugins shouldn't be active yet (because they aren't loaded)
        assert not registry.isActivePlugin("TestPlugin")
        assert not registry.isActivePlugin("PluginNoVersionNumber")

        registry.loadPlugins()  # Load them up

        assert registry.isActivePlugin("TestPlugin")
        # Doesn't have a version number, so should not be active.
        assert not registry.isActivePlugin("PluginNoVersionNumber")

        # Should no longer be active after we disable it.
        registry.disablePlugin("TestPlugin")
        assert not registry.isActivePlugin("TestPlugin")

    def test_allActivePlugins(self, registry):
        registry.loadPlugins()  # Load them up
        all_active_plugin_ids = registry.getActivePlugins()

        all_plugins_found = True
        for plugin_id in ['EmptyPlugin', 'TestPlugin', 'TestPlugin2']:
            if plugin_id not in all_active_plugin_ids:
                all_plugins_found = False

        assert all_plugins_found

    def test_load(self, registry):
        registry.loadPlugin("TestPlugin")

        assert registry.getTestPlugin().getPluginId() == "TestPlugin"

        assert registry.getPluginObject("TestPlugin") == registry.getTestPlugin()

    def test_loadTwice(self, registry):
        registry.loadPlugin("TestPlugin")

        registry._findPlugin = MagicMock()
        registry.loadPlugin("TestPlugin")
        assert registry._findPlugin.call_count == 0

    def test_loadNested(self, registry):
        registry.loadPlugin("TestPlugin2")

        assert registry.getTestPlugin().getPluginId() == "TestPlugin2"

    def test_findAllPlugins(self, registry):
        names = registry._findInstalledPlugins()
        assert sorted(names) == ["EmptyPlugin", "OldTestPlugin", "PluginNoVersionNumber", "TestPlugin", "TestPlugin2"]

    def test_pluginNotFound(self, registry):
        with pytest.raises(PluginNotFoundError):
            registry.loadPlugin("NoSuchPlugin")

        with pytest.raises(PluginNotFoundError):
            registry.getPluginObject("ThisPluginDoesntExist!")

    def test_disabledPlugin(self, registry):
        # Disabled plugin should not be loaded
        registry._disabled_plugins = ["TestPlugin"]
        registry.loadPlugin("TestPlugin")
        assert registry.getTestPlugin() is None
        assert registry.getDisabledPlugins() == ["TestPlugin"]

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
        with pytest.raises(PluginNotFoundError):
            registry.loadPlugin("OldTestPlugin")

    def test_isPluginApiVersionCompatible(self, registry):
        # Same version is compatible
        assert registry.isPluginApiVersionCompatible(registry._api_version)

        # Lower major version is not compatible
        api_version = Version("4.0.0")
        assert not registry.isPluginApiVersionCompatible(api_version)

        # Higher major version is not compatible
        api_version = Version("6.0.0")
        assert not registry.isPluginApiVersionCompatible(api_version)

        # Same major version but higher minor version is not compatible
        api_version = Version("5.7.0")
        assert not registry.isPluginApiVersionCompatible(api_version)

        # Same major version but lower minor version is compatible
        api_version = Version("5.3.0")
        assert registry.isPluginApiVersionCompatible(api_version)

        # Same major version but different patch version should not matter, it should be compatible
        api_version = Version("5.0.5")
        assert registry.isPluginApiVersionCompatible(api_version)
