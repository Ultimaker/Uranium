# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os.path

import pytest

import UM.Resources
import UM.Settings
import UM.PluginRegistry

##  Creates a brand new container registry.
#
#   To force a new container registry, the registry is first set to None and
#   then re-requested.
#
#   \return A brand new container registry.
@pytest.fixture
def container_registry():
    UM.Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))
    UM.Settings.ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time
    UM.PluginRegistry.getInstance().removeType("settings_container")

    instance = UM.Settings.ContainerRegistry.getInstance()
    instance.addResourceType(UM.Resources.InstanceContainers)
    instance.load()

    return instance
