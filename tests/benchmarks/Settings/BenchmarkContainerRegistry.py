
import os.path
import pytest

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
import UM
import UM.Settings

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

    UM.Resources.addSearchPath(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "Settings")))
    UM.Settings.ContainerRegistry._ContainerRegistry__instance = None # Reset the private instance variable every time
    UM.PluginRegistry.getInstance().removeType("settings_container")

    UM.Settings.ContainerRegistry.getInstance().load()

    return UM.Settings.ContainerRegistry.getInstance()


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
