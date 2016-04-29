# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

import UM.Settings
import UM.PluginRegistry
import UM.Settings.DefinitionContainer

from UM.Resources import Resources
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase

##  Fake container class to add to the container registry.
#
#   This allows us to test the container registry without testing the container
#   class. If something is wrong in the container class it won't influence this
#   test.
class MockContainer(UM.Settings.DefinitionContainer):
    ##  Initialise a new definition container.
    #
    #   The container will have the specified ID and all metadata in the
    #   provided dictionary.
    def __init__(self, id, metadata):
        self._id = id
        self._metadata = metadata

    ##  Gets the ID that was provided at initialisation.
    #
    #   \return The ID of the container.
    def getId(self):
        return self._id

    ##  Gets a metadata entry from the metadata dictionary.
    #
    #   \param key The key of the metadata entry.
    #   \return The value of the metadata entry, or None if there is no such
    #   entry.
    def getMetaDataEntry(self, entry, default = None):
        if entry in self._metadata:
            return self._metadata[entry]
        return default

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

##  Individual test cases for test_findDefinitionContainers.
#
#   Each entry has a descriptive name for debugging.
#   Each entry also has a list of "containers", each of which is an arbitrary
#   dictionary of metadata. Each dictionary MUST have an ID entry, which will be
#   taken out and used as ID for the container.
#   Each entry also has a "filter" dictionary, which is used as filter for the
#   metadata of the containers.
#   Each entry also has an "answer", which is a list of dictionaries again
#   representing the containers that must be returned by the search.
test_findDefinitionContainers_data = [
    {
        "name": "No containers",
        "containers": [

        ],
        "filter": { "id": "a" },
        "result": [
            # Empty.
        ]
    },
    {
        "name": "Single ID match",
        "containers": [
            { "id": "a" },
            { "id": "b" }
        ],
        "filter": { "id": "a" },
        "result": [
            { "id": "a" }
        ]
    },
    {
        "name": "Double ID match",
        "containers": [
            { "id": "a" },
            { "id": "b" },
            { "id": "a" }
        ],
        "filter": { "id": "a" },
        "result": [
            { "id": "a" },
            { "id": "a" }
        ]
    },
    {
        "name": "Multiple constraints",
        "containers": [
            { "id": "a", "number": 1, "bool": False },
            { "id": "b", "number": 2, "bool": False },
            { "id": "c", "number": 2, "bool": True },
            { "id": "d", "number": 2, "bool": False }
        ],
        "filter": { "number": 2, "bool": False },
        "result": [
            { "id": "b", "number": 2, "bool": False },
            { "id": "d", "number": 2, "bool": False }
        ]
    },
    {
        "name": "Mixed Type",
        "containers": [
            { "id": "a", "number": 1, "mixed": "z" },
            { "id": "b", "number": 1, "mixed": 9 },
            { "id": "c", "number": 2, "mixed": 9 }
        ],
        "filter": { "number": 1, "mixed": 9 },
        "result": [
            { "id": "b", "number": 1, "mixed": 9 }
        ]
    }
]

@pytest.mark.parametrize("data", test_findDefinitionContainers_data)
def test_findDefinitionContainers(container_registry, data):
    for container in data["containers"]: # Fill the registry with mock containers.
        id = container["id"]
        del container["id"]
        mock_container = MockContainer(id, container)
        container_registry._containers.append(mock_container) # TODO: This is a private field we're adding to here...

    result = container_registry.findDefinitionContainers(data["filter"]) # The actual function call we're testing.

    for required_result in data["result"]:
        # Each of these required results must appear somewhere in the result.
        for observed_result in range(0, len(result)): # Need to iterate by index so we can delete the item if we found it.
            for key, value in required_result.items():
                if key == "id":
                    if result[observed_result].getId() != value:
                        break # No match.
                else:
                    if not result[observed_result].getMetaDataEntry(key):
                        break # No match.
                    if result[observed_result].getMetaDataEntry(key) != value:
                        break # No match.
            else: # Not exited via a break, so it's a match!
                del result[observed_result] # Delete it so we won't find it again.
                break
        else:
            assert False # Didn't find any match.
    assert len(result) == 0 # We've deleted all containers that were a match. There can be none left over.

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
