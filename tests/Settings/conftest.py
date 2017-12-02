# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os.path

import pytest

from UM.Resources import Resources
from UM.PluginRegistry import PluginRegistry
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Settings.ContainerRegistry import ContainerRegistry
import UM.Settings.ContainerStack
import UM.Settings.InstanceContainer

##  Creates a brand new container registry.
#
#   To force a new container registry, the registry is first set to None and
#   then re-requested.
#
#   \return A brand new container registry.
@pytest.fixture
def container_registry(application):
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

    Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))
    ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time

    ContainerRegistry.setApplication(application)

    UM.Settings.ContainerStack.setContainerRegistry(ContainerRegistry.getInstance())
    UM.Settings.InstanceContainer.setContainerRegistry(ContainerRegistry.getInstance())
    return ContainerRegistry.getInstance()

@pytest.fixture
def loaded_container_registry(container_registry):
    instance = ContainerRegistry.getInstance()
    instance.addResourceType(Resources.InstanceContainers)
    instance.load()

    return instance
