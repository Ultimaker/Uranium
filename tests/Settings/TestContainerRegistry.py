# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

import UM.PluginObject
from UM.PluginRegistry import PluginRegistry
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.ContainerStack import ContainerStack
from UM.Signal import Signal

from UM.Resources import Resources
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase

##  Fake container class to add to the container registry.
#
#   This allows us to test the container registry without testing the container
#   class. If something is wrong in the container class it won't influence this
#   test.
from UM.Settings.Interfaces import ContainerInterface

class MockContainer(ContainerInterface, UM.PluginObject.PluginObject):
    ##  Initialise a new definition container.
    #
    #   The container will have the specified ID and all metadata in the
    #   provided dictionary.
    def __init__(self, id, metadata):
        self._id = id
        self._metadata = metadata
        self._plugin_id = "MockContainerPlugin"

    ##  Gets the ID that was provided at initialisation.
    #
    #   \return The ID of the container.
    def getId(self):
        return self._id

    ##  Gets all metadata of this container.
    #
    #   This returns the metadata dictionary that was provided in the
    #   constructor of this mock container.
    #
    #   \return The metadata for this container.
    def getMetaData(self):
        return self._metadata

    ##  Gets a metadata entry from the metadata dictionary.
    #
    #   \param key The key of the metadata entry.
    #   \return The value of the metadata entry, or None if there is no such
    #   entry.
    def getMetaDataEntry(self, entry, default = None):
        if entry in self._metadata:
            return self._metadata[entry]
        return default

    ##  Gets a human-readable name for this container.
    #
    #   \return Always returns "MockContainer".
    def getName(self):
        return "MockContainer"

    ##  Get whether the container item is stored on a read only location in the filesystem.
    #
    #   \return Always returns False
    def isReadOnly(self):
        return False

    ##  Mock get path
    def getPath(self):
        return "/path/to/the/light/side"

    ##  Mock set path
    def setPath(self, path):
        pass

    ##  Gets the value of a property of a container item.
    #
    #   This method is not implemented in the mock container.
    def getProperty(self, key, property_name, context = None):
        raise NotImplementedError()

    ##  Get the value of a container item.
    #
    #   Since this mock container cannot contain any items, it always returns
    #   None.
    #
    #   \return Always returns None.
    def getValue(self, key):
        pass

    ##  Get whether the container item has a specific property.
    #
    #   This method is not implemented in the mock container.
    def hasProperty(self, key, property_name):
        raise NotImplementedError()

    ##  Serializes the container to a string representation.
    #
    #   This method is not implemented in the mock container.
    def serialize(self, ignored_metadata_keys = None):
        raise NotImplementedError()

    ##  Deserializes the container from a string representation.
    #
    #   This method is not implemented in the mock container.
    def deserialize(self, serialized):
        raise NotImplementedError()

    def getConfigurationTypeFromSerialized(self, serialized):
        raise NotImplementedError()

    def getVersionFromSerialized(self, serialized):
        raise NotImplementedError()

    metaDataChanged = Signal()

##  Tests adding a container to the registry.
#
#   \param container_registry A new container registry from a fixture.
def test_addContainer(container_registry):
    definition_container_0 = DefinitionContainer("a", {})
    assert definition_container_0 not in container_registry.findDefinitionContainers() # Sanity check.
    container_registry.addContainer(definition_container_0)
    assert definition_container_0 in container_registry.findDefinitionContainers()

    # Add a second one of the same type.
    definition_container_1 = DefinitionContainer("b", {})
    assert definition_container_1 not in container_registry.findDefinitionContainers() # Sanity check.
    container_registry.addContainer(definition_container_1)
    assert definition_container_1 in container_registry.findDefinitionContainers()
    assert definition_container_0 in container_registry.findDefinitionContainers()

    # Add a container with the same type and same ID.
    definition_container_1_clone = DefinitionContainer("b", {})
    container_registry.addContainer(definition_container_1_clone)
    assert definition_container_1_clone not in container_registry.findDefinitionContainers() # Didn't get added!

    # For good measure, add a container with a different type too.
    instance_container_1 = InstanceContainer("a")
    assert instance_container_1 not in container_registry.findDefinitionContainers() # Sanity check.
    container_registry.addContainer(instance_container_1)
    assert instance_container_1 not in container_registry.findDefinitionContainers()

##  Tests adding a container type to the registry.
#
#   This adds the path to this file to the search paths for plug-ins, then lets
#   the plug-ins load. There is a plug-in in the relative path to this. Then it
#   checks if that plug-in gets added (by checking the length of
#   _container_types).
#
#   \param container_registry A new container registry from a fixture.
def test_addContainerType(container_registry, plugin_registry):
    old_container_type_count = len(container_registry._ContainerRegistry__container_types)
    plugin_registry.addPluginLocation(os.path.dirname(os.path.abspath(__file__))) # Load plug-ins relative to this file.
    plugin_registry.loadPlugins()
    # The __init__ script now adds itself to the container registry.
    assert len(container_registry._ContainerRegistry__container_types) == old_container_type_count + 1

    with pytest.raises(Exception):
        container_registry.addContainerType(None)

##  Tests the creation of the container registry.
#
#   This is tested using the fixture to create a container registry.
#
#   \param container_registry A newly created container registry instance, from
#   a fixture.
def test_create(container_registry):
    assert container_registry is not None

##  Individual test cases for test_findDefinitionContainers as well as
#   test_findInstanceContainers.
#
#   Each entry has a descriptive name for debugging.
#   Each entry also has a list of "containers", each of which is an arbitrary
#   dictionary of metadata. Each dictionary MUST have an ID entry, which will be
#   taken out and used as ID for the container.
#   Each entry also has a "filter" dictionary, which is used as filter for the
#   metadata of the containers.
#   Each entry also has an "answer", which is a list of dictionaries again
#   representing the containers that must be returned by the search.
test_findContainers_data = [
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
        "name": "Double match",
        "containers": [
            { "id": "a", "number": 1 },
            { "id": "b", "number": 2 },
            { "id": "c", "number": 1 }
        ],
        "filter": { "number": 1 },
        "result": [
            { "id": "a", "number": 1 },
            { "id": "c", "number": 1 }
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
    },
    {
        "name": "Asterisk Filter",
        "containers": [
            { "id": "a", "curseword": "fuck" },
            { "id": "b", "curseword": "shit" },
            { "id": "c", "curseword": "flabberjack" },
            { "id": "d", "curseword": "failbucket" }
        ],
        "filter": { "curseword": "f*ck" },
        "result": [
            { "id": "a", "curseword": "fuck" },
            { "id": "c", "curseword": "flabberjack" }
        ]
    }
]


##  Tests the findDefinitionContainers function.
#
#   \param container_registry A new container registry from a fixture.
#   \param data The data for the tests. Loaded from test_findContainers_data.
@pytest.mark.parametrize("data", test_findContainers_data)
def test_findDefinitionContainers(container_registry, data):
    for container in data["containers"]: # Fill the registry with mock containers.
        container = container.copy()
        container_id = container["id"]
        del container["id"]
        definition_container = DefinitionContainer(container_id)
        for key, value in container.items(): # Copy data into metadata.
            definition_container.getMetaData()[key] = value
        container_registry.addContainer(definition_container)

    results = container_registry.findDefinitionContainers(**data["filter"]) # The actual function call we're testing.

    _verifyMetaDataMatches(results, data["result"])

##  Tests the findInstanceContainers function.
#
#   \param container_registry A new container registry from a fixture.
#   \param data The data for the tests. Loaded from test_findContainers_data.
@pytest.mark.parametrize("data", test_findContainers_data)
def test_findInstanceContainers(container_registry, data):
    for container in data["containers"]: # Fill the registry with mock containers.
        container = container.copy()
        container_id = container["id"]
        del container["id"]
        instance_container = InstanceContainer(container_id)
        for key, value in container.items(): # Copy data into metadata.
            instance_container.getMetaData()[key] = value
        container_registry.addContainer(instance_container)

    results = container_registry.findInstanceContainers(**data["filter"]) # The actual function call we're testing.

    _verifyMetaDataMatches(results, data["result"])

##  Tests the findContainerStacks function.
#
#   \param container_registry A new container registry from a fixture.
#   \param data The data for the tests. Loaded from test_findContainers_data.
@pytest.mark.parametrize("data", test_findContainers_data)
def test_findContainerStacks(container_registry, data):
    for container in data["containers"]: # Fill the registry with container stacks.
        container = container.copy()
        container_id = container["id"]
        del container["id"]
        container_stack = ContainerStack(container_id)
        for key, value in container.items(): # Copy data into metadata.
            container_stack.getMetaData()[key] = value
        container_registry.addContainer(container_stack)

    results = container_registry.findContainerStacks(**data["filter"]) # The actual function call we're testing.

    _verifyMetaDataMatches(results, data["result"])

##  Tests the loading of containers into the registry.
#
#   \param container_registry A new container registry from a fixture.
def test_load(container_registry):
    container_registry.load()

    definitions = container_registry.findDefinitionContainers(id = "single_setting")
    assert len(definitions) == 1

    definition = definitions[0]
    assert definition.getId() == "single_setting"

    definitions = container_registry.findDefinitionContainers(author = "Ultimaker")
    assert len(definitions) == 3

    ids_found = []
    for definition in definitions:
        ids_found.append(definition.getId())

    assert "metadata" in ids_found
    assert "single_setting" in ids_found
    assert "inherits" in ids_found

##  Tests the making of a unique name for containers in the registry.
#
#   \param container_registry A new container registry from a fixture.
def test_uniqueName(container_registry):
    assert container_registry.uniqueName("test") == "test" #No collisions.

    mock_container = MockContainer(id = "test", metadata = { })
    container_registry.addContainer(mock_container)
    assert container_registry.uniqueName("test") == "test #2" #One collision.
    assert container_registry.uniqueName("test") == "test #2" #The check for unique name doesn't have influence on the registry.
    assert container_registry.uniqueName("test #2") == "test #2"
    assert container_registry.uniqueName("TEST").lower() == "test #2"

    mock_container = MockContainer(id = "test #2", metadata = { })
    container_registry.addContainer(mock_container)
    assert container_registry.uniqueName("test") == "test #3" #Two collisions.
    assert container_registry.uniqueName("test #2") == "test #3" #The ' #2' shouldn't count towards the index.
    assert container_registry.uniqueName("test #3") == "test #3"

    assert container_registry.uniqueName("") == "Profile" #Empty base names should be filled in with a default base name 'profile'.
    assert container_registry.uniqueName(" #2") == "Profile"

    mock_container = MockContainer(id = "Profile", metadata = { })
    container_registry.addContainer(mock_container)
    assert container_registry.uniqueName("") == "Profile #2" #Empty base names should be filled in with a default base name 'profile'.
    assert container_registry.uniqueName(" #2") == "Profile #2"
    assert container_registry.uniqueName("Profile #2") == "Profile #2"

    # Reproduce steps for issue CURA-2165 to verify the behaviour is still correct.
    mock_container = MockContainer(id = "carlo #3", metadata = {})
    container_registry.addContainer(mock_container)
    mock_container = MockContainer(id = "carlo #4", metadata = {})
    container_registry.addContainer(mock_container)
    mock_container = MockContainer(id = "carlo #6", metadata = {})
    container_registry.addContainer(mock_container)

    assert container_registry.uniqueName("carlo #7") == "carlo #7"

##  Helper function to verify if the metadata of the answers matches required
#   metadata.
#
#   This basically compares two sets. They are provided as two lists, but the
#   order doesn't matter.
#
#   \param answer A list of containers, each of which has metadata.
#   \param ground_truth A list of dictionaries, describing the metadata of each
#   required container.
def _verifyMetaDataMatches(answer, ground_truth):
    assert len(answer) == len(ground_truth)

    matches = 0
    for result in answer: # Go through all results and match them with our expected data.
        for required in list(ground_truth): # Iterate over a copy of the list so we do not modify the original data.
            if "id" in required: # Special casing for ID since that is not in the metadata.
                if result.getId() != required["id"]:
                    continue # No match.
                del required["id"] # Remove ID from the expected metadata since it is not part of the metadata.

            if result.getMetaData() == required:
                # If the metadata matches, we know this entry is valid.
                # Note that this requires specifying all metadata in the expected results.
                matches += 1
                break # We have a valid match.
    assert matches == len(ground_truth)
