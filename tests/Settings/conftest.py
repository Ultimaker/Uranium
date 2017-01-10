# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os.path

import pytest

import UM.Resources
import UM.Settings
import UM.PluginRegistry

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase

##  Creates a brand new container registry.
#
#   To force a new container registry, the registry is first set to None and
#   then re-requested.
#
#   \return A brand new container registry.
@pytest.fixture
def container_registry():
    MimeTypeDatabase.addMimeType(
        MimeType(
            name = "application/x-uranium-definitioncontainer",
            comment = "Uranium Definition Container",
            suffixes = ["def.json"]
        )
    )

    MimeTypeDatabase.addMimeType(
        MimeType(
            name = "application/x-uranium-instancecontainer",
            comment = "Uranium Instance Container",
            suffixes = [ "inst.cfg" ]
        )
    )

    MimeTypeDatabase.addMimeType(
        MimeType(
            name = "application/x-uranium-containerstack",
            comment = "Uranium Container Stack",
            suffixes = [ "stack.cfg" ]
        )
    )

    UM.Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))
    UM.Settings.ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time
    UM.PluginRegistry.getInstance().removeType("settings_container")

    instance = UM.Settings.ContainerRegistry.getInstance()
    instance.addResourceType(UM.Resources.InstanceContainers)
    instance.load()

    return instance
