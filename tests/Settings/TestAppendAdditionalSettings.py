# Copyright (c) 2023 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import pytest
from unittest.mock import MagicMock, patch

from UM.Settings.AdditionalSettingDefinitionsAppender import AdditionalSettingDefinitionsAppender
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.VersionUpgradeManager import VersionUpgradeManager


class PluginTestClass(AdditionalSettingDefinitionsAppender):
    def __init__(self) -> None:
        super().__init__()
        self._plugin_id = "RealityPerforator"
        self._version = "7.8.9"
        self.appender_type = "CLOWNS"
        self.definition_file_paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "additional_settings", "append_extra_settings.def.json")]


def test_AdditionalSettingNames():
    plugin = PluginTestClass()
    settings = plugin.getAdditionalSettingDefinitions()

    assert "test_setting" in settings
    assert "category_too" in settings
    assert "children" in settings["test_setting"]
    assert "children" in settings["category_too"]

    assert "_clowns__realityperforator__7_8_9__glombump" in settings["test_setting"]["children"]
    assert "_clowns__realityperforator__7_8_9__zharbler" in settings["category_too"]["children"]


def test_AdditionalSettingContainer(upgrade_manager: VersionUpgradeManager):
    plugin = PluginTestClass()
    settings = plugin.getAdditionalSettingDefinitions()

    definition_container = DefinitionContainer("TheSunIsADeadlyLazer")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", "children.def.json"), encoding = "utf-8") as data:
        definition_container.deserialize(data.read())
    definition_container.appendAdditionalSettingDefinitions(settings)

    # 'merged' setting-categories should definitely be in the relevant container (as well as the original ones):
    assert len(definition_container.findDefinitions(key="test_setting")) == 1
    kid_keys = [x.key for x in definition_container.findDefinitions(key="test_setting")[0].children]
    assert "test_child_0" in kid_keys
    assert "test_child_1" in kid_keys
    assert "_clowns__realityperforator__7_8_9__glombump" in kid_keys

    # other settings (from new categories) are added 'dry' to the container:
    assert "_clowns__realityperforator__7_8_9__zharbler" in definition_container.getAllKeys()
