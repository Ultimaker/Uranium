# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os.path
import pytest

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Resources import Resources

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.PluginRegistry import PluginRegistry

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

    ContainerRegistry.getInstance()._containers = {} # clear containers from previous iteration

    root_plugin_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "plugins")
    PluginRegistry.getInstance().addPluginLocation(root_plugin_dir)

    PluginRegistry.getInstance().loadPlugin("LocalContainerProvider")
    plugin = PluginRegistry.getInstance().getPluginObject("LocalContainerProvider")
    ContainerRegistry.getInstance()._providers.append(plugin)

    PluginRegistry.getInstance()._plugins.clear() # remove plugins

    Resources.addSearchPath(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "Settings")))


    empty_container = ContainerRegistry.getInstance().getEmptyInstanceContainer()
    empty_definition_changes_container = empty_container
    empty_definition_changes_container.setMetaDataEntry("id", "empty_definition_changes")
    empty_definition_changes_container.setMetaDataEntry("type", "definition_changes")
    ContainerRegistry.getInstance().addContainer(empty_definition_changes_container)

    ContainerRegistry.getInstance().load()

    return ContainerRegistry.getInstance()


benchmark_findContainers_data = [
    { "id": 'basic_definition' },
    { "name": "Test"},
    { "name": "T*" },
    { "name": "Test", "category": "Test" },
    { "name": "*", "category": "*" },
    { "id": "*metadata*" }
]

@pytest.mark.parametrize("query_args", benchmark_findContainers_data)
def benchmark_findContainers(benchmark, container_registry, query_args):
    result = benchmark(container_registry.findDefinitionContainers, **query_args)
    assert len(result) >= 1
