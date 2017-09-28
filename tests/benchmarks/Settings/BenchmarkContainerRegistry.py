# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os.path
import pytest

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Resources import Resources
from UM.PluginRegistry import PluginRegistry
from UM.Settings.ContainerRegistry import ContainerRegistry

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

    Resources.addSearchPath(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "Settings")))
    ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time
    PluginRegistry.getInstance().removeType("settings_container")

    ContainerRegistry.getInstance().load()

    return ContainerRegistry.getInstance()


benchmark_findContainers_data = [
    { "id": "basic" },
    { "name": "Test"},
    { "name": "T*" },
    { "name": "Test", "category": "Test" },
    { "name": "*", "category": "*" },
    { "id": "*setting*" }
]

@pytest.mark.parametrize("query_args", benchmark_findContainers_data)
def benchmark_findContainers(benchmark, container_registry, query_args):
    result = benchmark(container_registry.findDefinitionContainers, **query_args)
    assert len(result) >= 1
