# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
from unittest.mock import MagicMock

import pytest

from UM.Resources import Resources
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.ContainerStack import ContainerStack

from .MockContainer import MockContainer

Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))


##  Tests adding a container to the registry.
#
#   \param container_registry A new container registry from a fixture.
def test_addContainer(container_registry):
    definition_container_0 = DefinitionContainer("a")
    assert definition_container_0.getMetaData() not in container_registry.findDefinitionContainersMetadata() # Sanity check.
    assert definition_container_0 not in container_registry.findDefinitionContainers()
    container_registry.addContainer(definition_container_0)
    assert definition_container_0.getMetaData() in container_registry.findDefinitionContainersMetadata()
    assert definition_container_0 in container_registry.findDefinitionContainers()

    # Add a second one of the same type.
    definition_container_1 = DefinitionContainer("b")
    assert definition_container_1.getMetaData() not in container_registry.findDefinitionContainersMetadata() # Sanity check.
    assert definition_container_1 not in container_registry.findDefinitionContainers() # Sanity check.
    container_registry.addContainer(definition_container_1)
    assert definition_container_1.getMetaData() in container_registry.findDefinitionContainersMetadata()
    assert definition_container_1 in container_registry.findDefinitionContainers()
    assert definition_container_0.getMetaData() in container_registry.findDefinitionContainersMetadata()
    assert definition_container_0 in container_registry.findDefinitionContainers()

    # Add a container with the same type and same ID.
    definition_container_1_clone = DefinitionContainer("b")
    container_registry.addContainer(definition_container_1_clone)
    #Since comparing metadata is a deep comparison, you'll find that the metadata of the clone got in there. But it's not, it's just exactly the same as the original metadata so it appears as if it's in there.
    assert definition_container_1_clone not in container_registry.findDefinitionContainers()

    # For good measure, add a container with a different type too.
    instance_container_1 = InstanceContainer("a")
    assert instance_container_1.getMetaData() not in container_registry.findDefinitionContainersMetadata() # Sanity check.
    assert instance_container_1 not in container_registry.findDefinitionContainers()
    container_registry.addContainer(instance_container_1)
    assert instance_container_1.getMetaData() not in container_registry.findDefinitionContainersMetadata()
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


def test_readOnly(container_registry):
    assert not container_registry.isReadOnly("NotAContainerThatIsLoaded")

    test_container = DefinitionContainer("omgzomg")
    container_registry.addContainer(test_container)

    mock_provider = MagicMock()
    mock_provider.isReadOnly = MagicMock(return_value = True)
    container_registry.source_provider = {"omgzomg": mock_provider}
    assert container_registry.isReadOnly("omgzomg")


def test_getContainerFilePathByID(container_registry):
    # There is no provider and the container isn't even there.
    assert container_registry.getContainerFilePathById("NotAContainerThatIsLoaded") is None

    test_container = DefinitionContainer("omgzomg")
    container_registry.addContainer(test_container)

    mock_provider = MagicMock()
    mock_provider.getContainerFilePathById = MagicMock(return_value="")
    container_registry.source_provider = {"omgzomg": mock_provider}
    assert container_registry.getContainerFilePathById("omgzomg") == ""


def test_isLoaded(container_registry):
    assert not container_registry.isLoaded("NotAContainerThatIsLoaded")
    test_container = DefinitionContainer("omgzomg")
    container_registry.addContainer(test_container)
    assert container_registry.isLoaded("omgzomg")


def test_removeContainer(container_registry):
    # Removing a container that isn't added shouldn't break
    container_registry.removeContainer("NotAContainerThatIsLoaded")

    test_container = DefinitionContainer("omgzomg")
    container_registry.addContainer(test_container)
    container_registry.removeContainer("omgzomg")
    assert not container_registry.isLoaded("omgzomg")


def test_removeNotLoadedContainer(container_registry):
    # Removing a partial (only metadata) loaded container should not break
    test_container = InstanceContainer("omgzomg")
    container_registry.addContainer(test_container)
    container_registry._containers["omgzomg"] = None  # Emulates as partial loaded container
    assert container_registry.isLoaded("omgzomg")

    def _onContainerRemoved(container: "ContainerInterface") -> None:
        assert isinstance(container, InstanceContainer)
        assert container.getName() == "omgzomg"

    container_registry.containerRemoved.connect(_onContainerRemoved)
    container_registry.removeContainer("omgzomg")
    assert not container_registry.isLoaded("omgzomg")
    
    
def test_renameContainer(container_registry):
    # Ensure that renaming an unknown container doesn't break
    container_registry.renameContainer("ContainerThatDoesntExist", "whatever")

    test_container = InstanceContainer("omgzomg")
    container_registry.addContainer(test_container)

    # Attempting a rename to the same name should not mark the container as dirty.
    container_registry.renameContainer("omgzomg", "omgzomg")
    assert "omgzomg" not in [container.getId() for container in container_registry.findDirtyContainers()]

    container_registry.renameContainer("omgzomg", "BEEP")
    assert test_container.getMetaDataEntry("name") == "BEEP"
    # Ensure that the container is marked as dirty
    assert "omgzomg" in [container.getId() for container in container_registry.findDirtyContainers()]

    # Rename the container and also try to give it a new ID
    container_registry.renameContainer("omgzomg", "BEEPz", "omgzomg2")
    assert "omgzomg2" in [container.getId() for container in container_registry.findDirtyContainers()]
    # The old ID should not be in the list of dirty containers now.
    assert "omgzomg" not in [container.getId() for container in container_registry.findDirtyContainers()]


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
        definition_container = DefinitionContainer(container["id"])
        for key, value in container.items(): # Copy data into metadata.
            definition_container.getMetaData()[key] = value
        container_registry.addContainer(definition_container)

    results = container_registry.findDefinitionContainers(**data["filter"]) # The actual function call we're testing.

    _verifyMetaDataMatches(results, data["result"])

    metadata_results = container_registry.findDefinitionContainersMetadata(**data["filter"])
    assert metadata_results == metadata_results

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

    metadata_results = container_registry.findInstanceContainersMetadata(**data["filter"])
    assert metadata_results == metadata_results

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

    metadata_results = container_registry.findContainerStacksMetadata(**data["filter"])
    assert metadata_results == metadata_results

def test_addGetResourceType(container_registry):
    container_registry.addResourceType(12, "zomg")

    assert container_registry.getResourceTypes()["zomg"] == 12

def test_getMimeTypeForContainer(container_registry):
    # We shouldn't get a mimetype if it's unknown
    assert container_registry.getMimeTypeForContainer(type(None)) is None

    mimetype = container_registry.getMimeTypeForContainer(InstanceContainer)
    assert mimetype is not None
    assert mimetype.name == "application/x-uranium-instancecontainer"

    # Check if the reverse also works
    assert container_registry.getContainerForMimeType(mimetype) == InstanceContainer


def test_saveContainer(container_registry):
    mocked_provider = MagicMock()
    mocked_container = MagicMock()
    container_registry.saveContainer(mocked_container, mocked_provider)
    mocked_provider.saveContainer.assert_called_once_with(mocked_container)

    container_registry.getDefaultSaveProvider().saveContainer = MagicMock()

    container_registry.saveContainer(mocked_container)
    container_registry.getDefaultSaveProvider().saveContainer.assert_called_once_with(mocked_container)


##  Tests the loading of containers into the registry.
#
#   \param container_registry A new container registry from a fixture.
def test_load(container_registry):
    container_registry.load()

    definitions = container_registry.findDefinitionContainersMetadata(id = "single_setting")
    assert len(definitions) == 1

    definition = definitions[0]
    assert definition["id"] == "single_setting"

    definitions = container_registry.findDefinitionContainersMetadata(author = "Ultimaker")
    assert len(definitions) == 3

    ids_found = []
    for definition in definitions:
        ids_found.append(definition["id"])

    assert "metadata_definition" in ids_found
    assert "single_setting" in ids_found
    assert "inherits" in ids_found


##  Test that uses the lazy loading part of the registry. Instead of loading
#   everything, we load the metadata so that the containers can be loaded just
#   in time.
def test_loadAllMetada(container_registry):
    # Although we get different mocked ContainerRegistry objects every time, queries are done via ContainerQuery, which
    # has a class-wide built-in cache. The cache is not cleared between each test, so it can happen that the cache's
    # state from the last test will affect this test.
    from UM.Settings.ContainerQuery import ContainerQuery
    ContainerQuery.cache.clear()

    # Before we start, the container should not even be there.
    instances_before = container_registry.findInstanceContainersMetadata(author = "Ultimaker")
    assert len(instances_before) == 0

    container_registry.loadAllMetadata()

    instances = container_registry.findInstanceContainersMetadata(author = "Ultimaker")
    assert len(instances) == 1

    # Since we only loaded the metadata, the actual container should not be loaded just yet.
    assert not container_registry.isLoaded(instances[0].get("id"))

    # As we asked for it, the lazy loading should kick in and actually load it.
    container_registry.findInstanceContainers(id = instances[0].get("id"))
    assert container_registry.isLoaded(instances[0].get("id"))


def test_findLazyLoadedContainers(container_registry):
    container_registry.loadAllMetadata()
    container_registry.containerLoadComplete.emit = MagicMock()
    # Only metadata should be loaded at this moment, so no loadComplete signals should have been fired.
    assert container_registry.containerLoadComplete.emit.call_count == 0
    result = container_registry.findContainers(id = "single_setting")
    assert len(result) == 1
    assert container_registry.containerLoadComplete.emit.call_count == 1


##  Tests the making of a unique name for containers in the registry.
#
#   \param container_registry A new container registry from a fixture.
def test_uniqueName(container_registry):
    assert container_registry.uniqueName("test") == "test" #No collisions.

    mock_container = MockContainer(metadata = {"id": "test"})
    container_registry.addContainer(mock_container)
    assert container_registry.uniqueName("test") == "test #2" #One collision.
    assert container_registry.uniqueName("test") == "test #2" #The check for unique name doesn't have influence on the registry.
    assert container_registry.uniqueName("test #2") == "test #2"
    assert container_registry.uniqueName("TEST").lower() == "test #2"

    mock_container = MockContainer(metadata = {"id": "test #2"})
    container_registry.addContainer(mock_container)
    assert container_registry.uniqueName("test") == "test #3" #Two collisions.
    assert container_registry.uniqueName("test #2") == "test #3" #The ' #2' shouldn't count towards the index.
    assert container_registry.uniqueName("test #3") == "test #3"

    assert container_registry.uniqueName("") == "Profile" #Empty base names should be filled in with a default base name 'profile'.
    assert container_registry.uniqueName(" #2") == "Profile"

    mock_container = MockContainer(metadata = {"id": "Profile"})
    container_registry.addContainer(mock_container)
    assert container_registry.uniqueName("") == "Profile #2" #Empty base names should be filled in with a default base name 'profile'.
    assert container_registry.uniqueName(" #2") == "Profile #2"
    assert container_registry.uniqueName("Profile #2") == "Profile #2"

    # Reproduce steps for issue CURA-2165 to verify the behaviour is still correct.
    mock_container = MockContainer(metadata = {"id": "carlo #3"})
    container_registry.addContainer(mock_container)
    mock_container = MockContainer(metadata = {"id": "carlo #4"})
    container_registry.addContainer(mock_container)
    mock_container = MockContainer(metadata = {"id": "carlo #6"})
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
        for required in ground_truth:
            if result.getMetaData().items() >= required.items():
                # If the metadata matches, we know this entry is valid.
                # Note that this requires specifying all metadata in the expected results.
                matches += 1
                break # We have a valid match.
    assert matches == len(ground_truth)
