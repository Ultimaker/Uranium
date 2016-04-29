# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

import UM.Settings
import UM.PluginRegistry

from UM.Resources import Resources
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase

@pytest.fixture
def container_registry():
    Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))
    UM.Settings.ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time
    UM.PluginRegistry.PluginRegistry.getInstance().removeType("settings_container")

    return UM.Settings.ContainerRegistry.getInstance()

##  Tests the creation of the container registry.
#
#   This is tested using the fixture to create a container registry.
#
#   \param container_registry A newly created container registry instance, from
#   a fixture.
def test_create(container_registry):
    assert container_registry != None

def test_load(container_registry):
    container_registry.load()

    definitions = container_registry.findDefinitionContainers({ "id": "single_setting" })
    assert len(definitions) == 1

    definition = definitions[0]
    assert definition.getId() == "single_setting"

    definitions = container_registry.findDefinitionContainers({ "author": "Ultimaker" })
    assert len(definitions) == 3

    ids_found = []
    for definition in definitions:
        ids_found.append(definition.getId())

    assert "metadata" in ids_found
    assert "single_setting" in ids_found
    assert "inherits" in ids_found
