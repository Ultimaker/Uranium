# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

# The purpose of this class is to create fixtures or methods that can be shared
# among all settings tests.

import os.path
import pytest
import unittest.mock #For mocking the container provider priority.

from UM.Resources import Resources
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Settings.ContainerProvider import ContainerProvider #To provide the fixtures for container providers.
from UM.Settings.ContainerRegistry import ContainerRegistry
import UM.Settings.ContainerStack
from UM.Settings.DefinitionContainer import DefinitionContainer #To provide definition containers in the registry fixtures.
import UM.Settings.InstanceContainer

##  Creates a brand new container registry.
#
#   To force a new container registry, the registry is first set to None and
#   then re-requested.
#
#   \return A brand new container registry.
@pytest.fixture
def container_registry(application, test_containers_provider):
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

    ContainerRegistry.setApplication(application)

    ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time
    registry = ContainerRegistry.getInstance()

    #We need to mock the "priority" plug-in metadata field, but preferably without mocking an entire plug-in.
    with unittest.mock.patch("UM.PluginRegistry.PluginRegistry.getMetaData", unittest.mock.MagicMock(return_value = {"container_provider": {}})):
        registry.addProvider(test_containers_provider)

    UM.Settings.ContainerStack.setContainerRegistry(registry)
    UM.Settings.InstanceContainer.setContainerRegistry(registry)
    return registry

@pytest.fixture
def loaded_container_registry(container_registry: ContainerRegistry, test_containers_provider: ContainerProvider):
    container_registry.addResourceType(Resources.InstanceContainers)
    container_registry.load()

    return container_registry

##  Empty container provider which returns nothing.
@pytest.fixture
def container_provider():
    return ContainerProvider()

##  Container provider which provides the containers that are in the setting
#   test directory.
@pytest.fixture
def test_containers_provider(container_provider: ContainerProvider) -> ContainerProvider:
    my_folder = os.path.dirname(os.path.abspath(__file__))

    definition_ids = {"basic_definition", "children", "functions", "inherits", "metadata_definition", "multiple_settings", "single_setting"}
    for definition_id in definition_ids:
        container = DefinitionContainer(definition_id)
        container.deserialize(open(os.path.join(my_folder, "definitions", definition_id + ".def.json")).read())
        container_provider._containers[definition_id] = container
        container_provider.addMetadata(container.getMetaData())

    instance_ids = {"basic_instance", "metadata_instance", "setting_values"}
    for instance_id in instance_ids:
        container = UM.Settings.InstanceContainer.InstanceContainer(instance_id)
        container.deserialize(open(os.path.join(my_folder, "instances", instance_id + ".inst.cfg")).read())
        container_provider._containers[instance_id] = container
        container_provider.addMetadata(container.getMetaData())

    #Some replacement methods to put in our temporary provider.

    def getAllIds(cls, self, *args, **kwargs):
        return self._containers.keys()
    container_provider.getAllIds = getAllIds

    def isReadOnly(self, *args, **kwargs):
        return True
    container_provider.isReadOnly = isReadOnly

    def loadContainer(self, container_id, *args, **kwargs):
        return self._containers[container_id]
    container_provider.loadContainer = loadContainer

    def loadMetadata(self, container_id, *args, **kwargs):
        return self._metadata[container_id]
    container_provider.loadMetadata = loadMetadata

    return container_provider