# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import uuid # For creating unique ID's for each container stack.
import os

from UM.PluginRegistry import PluginRegistry
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Signal import Signal
from UM.Resources import Resources

from UM.Settings.Interfaces import ContainerInterface
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.ContainerStack import IncorrectVersionError
from UM.Settings.ContainerStack import InvalidContainerStackError

##  A fake container class that implements ContainerInterface.
#
#   This allows us to test the container stack independent of any actual
#   implementation of the containers. If something were to go wrong in the
#   actual implementations, the tests in this suite are unaffected.
class MockContainer(ContainerInterface):
    ##  Creates a mock container with a new unique ID.
    def __init__(self, container_id: str = None):
        self._id = str(uuid.uuid4() if container_id is None else container_id)
        self._metadata = {}
        self.items = {}

    ##  Gets the unique ID of the container.
    #
    #   \return A unique identifier for this container.
    def getId(self):
        return self._id

    ##  Gives an arbitrary name.
    #
    #   \return Some string.
    def getName(self):
        return "Fred"

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

    ##  Returns the metadata dictionary.
    #
    #   \return A dictionary containing metadata for this container stack.
    def getMetaData(self):
        return self._metadata

    ##  Gets an entry from the metadata.
    #
    #   \param entry The entry to get from the metadata.
    #   \param default The default value in case the entry is missing.
    #   \return The value belonging to the requested entry, or the default if no
    #   such key exists.
    def getMetaDataEntry(self, entry, default = None):
        if entry in self._metadata:
            return self._metadata["entry"]
        return default

    ##  Gets the value of a container item property.
    #
    #   If the key doesn't exist, returns None.
    #
    #   \param key The key of the item to get.
    def getProperty(self, key, property_name, context = None):
        if key in self.items:
            return self.items[key]
        return None

    propertyChanged = Signal()

    metaDataChanged = Signal()

    def hasProperty(self, key, property_name):
        return key in self.items

    ##  Serialises this container.
    #
    #   The serialisation of the mock needs to be kept simple, so it only
    #   serialises the ID. This makes the tests succeed if the serialisation
    #   creates different instances (which is desired).
    #
    #   \return A static string representing a container.
    def serialize(self, ignored_metadata_keys = None):
        return str(self._id)

    ##  Deserialises a string to a container.
    #
    #   The serialisation of the mock needs to be kept simple, so it only
    #   deserialises the ID. This makes the tests succeed if the serialisation
    #   creates different instances (which is desired).
    #
    #   \param serialized A serialised mock container.
    def deserialize(self, serialized):
        self._id = int(serialized)

    def getConfigurationTypeFromSerialized(self, serialized):
        raise NotImplementedError()

    def getVersionFromSerialized(self, serialized):
        raise NotImplementedError()


##  Creates a brand new container stack to test with.
#
#   The container stack will get a new, unique ID.
@pytest.fixture
def container_stack():
    return ContainerStack(str(uuid.uuid4()))

##  Tests the creation of a container stack.
#
#   The actual creation is done in a fixture though.
#
#   \param container_stack A new container stack from a fixture.
def test_container_stack(container_stack):
    assert container_stack is not None

##  Tests adding a container to the stack.
#
#   \param container_stack A new container stack from a fixture.
def test_addContainer(container_stack):
    assert container_stack.getContainers() == [] # First nothing.
    container = MockContainer()
    container_stack.addContainer(container)
    assert container_stack.getContainers() == [container] # Then something!

    with pytest.raises(Exception):
        container_stack.addContainer(container_stack) # Adding itself gives an exception.
    assert container_stack.getContainers() == [container] # Make sure that adding itself didn't change the state, even if it raises an exception.

##  Tests deserialising a container stack from a corrupted string.
def test_deserialize_syntax_error(container_stack):
    serialised = "["
    with pytest.raises(Exception):
        container_stack.deserialize(serialised)

##  Tests deserialising a container stack when the version number is wrong.
#
#   \param container_stack A new container stack from a fixture.
#   \param container_registry A new container registry from a fixture.
def test_deserialize_wrong_version(container_stack, container_registry):
    container_registry.addContainer(InstanceContainer("a")) # Make sure this container isn't the one it complains about.

    serialised = """
    [general]
    name = Test
    id = testid
    version = -1

    [containers]
    0 = a
    """ # -1 should always be wrong.

    with pytest.raises(IncorrectVersionError):
        container_stack.deserialize(serialised)

##  Tests deserialising a container stack from files that are missing entries.
#
#   Sorry for the indenting.
#
#   \param container_stack A new container stack from a fixture.
#   \param container_registry A new container registry from a fixture.
def test_deserialize_missing_items(container_stack, container_registry):
    container_registry.addContainer(InstanceContainer("a")) # Make sure this container isn't the one it complains about.

    serialised_no_name = """
    [general]
    id = testid
    version = {version}

    [containers]
    0 = a
    """.format(version = ContainerStack.Version)

    with pytest.raises(InvalidContainerStackError):
        container_stack.deserialize(serialised_no_name)

    serialised_no_id = """
    [general]
    name = Test
    version = {version}

    [containers]
    0 = a
    """.format(version = ContainerStack.Version)

    with pytest.raises(InvalidContainerStackError):
        container_stack.deserialize(serialised_no_id)

    serialised_no_version = """
    [general]
    name = Test
    id = testid

    [containers]
    0 = a
    """

    with pytest.raises(InvalidContainerStackError):
        container_stack.deserialize(serialised_no_version)

    serialised_no_containers = """
    [general]
    name = Test
    id = testid
    version = {version}
    """.format(version = ContainerStack.Version)

    container_stack.deserialize(serialised_no_containers) # Missing containers is allowed.
    assert container_stack.getContainers() == [] # Deserialize of an empty stack should result in an empty stack

    serialised_no_general = """
    [metadata]
    foo = bar
    """

    with pytest.raises(InvalidContainerStackError):
        container_stack.deserialize(serialised_no_general)

##  Tests deserialising a container stack with various subcontainers.
#
#   Sorry for the indenting.
#
#   \param container_stack A new container stack from a fixture.
#   \param container_registry A new container registry from a fixture.
def test_deserialize_containers(container_stack, container_registry):
    container = InstanceContainer("a")
    container_registry.addContainer(container)

    serialised = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    0 = a
    """.format(version = ContainerStack.Version) # Test case where there is a container.

    container_stack.deserialize(serialised)
    assert container_stack.getContainers() == [container]

    container_stack = ContainerStack(str(uuid.uuid4()))
    serialised = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    """.format(version = ContainerStack.Version) # Test case where there is no container.

    container_stack.deserialize(serialised)
    assert container_stack.getContainers() == []

    container_stack = ContainerStack(str(uuid.uuid4()))
    serialised = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    0 = a
    1 = a
    """.format(version = ContainerStack.Version) # Test case where there are two of the same containers.

    container_stack.deserialize(serialised)
    assert container_stack.getContainers() == [container, container]

    container_stack = ContainerStack(str(uuid.uuid4()))
    serialised = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    0 = a
    1 = b
    """.format(version = ContainerStack.Version) # Test case where a container doesn't exist.

    with pytest.raises(Exception):
        container_stack.deserialize(serialised)

    container_stack = ContainerStack(str(uuid.uuid4()))
    container_b = InstanceContainer("b") # Add the missing container and try again.
    ContainerRegistry.getInstance().addContainer(container_b)
    container_stack.deserialize(serialised)
    assert container_stack.getContainers() == [container, container_b]

##  Individual test cases for test_findContainer.
#
#   Each test case has:
#   * A description for debugging.
#   * A list of dictionaries for containers to search in.
#   * A filter to search with.
#   * A required result.
test_findContainer_data = [
    {
        "description": "Search empty",
        "containers": [
            { },
            { }
        ],
        "filter": { },
        "result": { }
    },
    {
        "description": "Not found",
        "containers": [
            { "foo": "baz" }
        ],
        "filter": { "foo": "bar" },
        "result": None
    },
    {
        "description": "Key not found",
        "containers": [
            { "loo": "bar" }
        ],
        "filter": { "foo": "bar" },
        "result": None
    },
    {
        "description": "Multiple constraints",
        "containers": [
            { "id": "a", "number": 1, "string": "foo", "mixed": 10 },
            { "id": "b", "number": 2, "string": "foo", "mixed": "bar" },
            { "id": "c", "number": 1, "string": "loo", "mixed": 10 }
        ],
        "filter": { "number": 1, "string": "foo", "mixed": 10 },
        "result": { "id": "a", "number": 1, "string": "foo", "mixed": 10 }
    },
    {
        "description": "Wildcard Number",
        "containers": [
            { "id": "a", "string": "foo" },
            { "id": "b", "number": 1 },
            { "id": "c", "number": 2 },
        ],
        "filter": { "number": "*" },
        "result": { "id": "c", "number": 2 }
    },
    {
        "description": "Wildcard String",
        "containers": [
            { "id": "a", "number": 1 },
            { "id": "b", "string": "foo" },
            { "id": "c", "string": "boo" }
        ],
        "filter": { "string": "*" },
        "result": { "id": "c", "string": "boo" }
    }
]

##  Tests finding a container by a filter.
#
#   \param container_stack A new container stack from a fixture.
#   \param data Individual test cases, provided from test_findContainer_data.
@pytest.mark.parametrize("data", test_findContainer_data)
def test_findContainer(container_stack, data):
    for container in data["containers"]: # Add all containers.
        mockup = MockContainer()
        for key, value in container.items(): # Copy the data to the metadata of the mock-up.
            mockup.getMetaData()[key] = value
        container_stack.addContainer(mockup)

    answer = container_stack.findContainer(data["filter"]) # The actual method to test.

    if data["result"] is None:
        assert answer is None
    else:
        assert answer is not None
        assert data["result"] == answer.getMetaData()

##  Tests getting a container by index.
#
#   \param container_stack A new container stack from a fixture.
def test_getContainer(container_stack):
    with pytest.raises(IndexError):
        container_stack.getContainer(0)

    # Fill with data.
    container1 = MockContainer()
    container_stack.addContainer(container1)
    container2 = MockContainer()
    container_stack.addContainer(container2)
    container3 = MockContainer()
    container_stack.addContainer(container3)

    assert container_stack.getContainer(2) == container1
    assert container_stack.getContainer(1) == container2
    assert container_stack.getContainer(0) == container3
    with pytest.raises(IndexError):
        container_stack.getContainer(3)
    with pytest.raises(IndexError):
        container_stack.getContainer(-1)

##  Tests getting and changing the metadata of the container stack.
#
#   \param container_stack A new container stack from a fixture.
def test_getMetaData(container_stack):
    meta_data = container_stack.getMetaData()
    assert meta_data is not None

    meta_data["foo"] = "bar" #Try adding an entry.
    assert container_stack.getMetaDataEntry("foo") == "bar"

##  Individual test cases for test_getValue.
#
#   Each test case has:
#   * A description, for debugging.
#   * A list of containers. Each container is a dictionary of the items that
#     will be set in that container. Note that this list is ordered in the order
#     of the stack. The first item should be referenced first.
#   * A key to search for.
#   * The expected result that should be returned when querying that key.
test_getValue_data = [
    {
        "description": "Empty stack",
        "containers": [
        ],
        "key": "foo",
        "result": None
    },
    {
        "description": "Nonexistent key",
        "containers": [
            { "boo": "bar" }
        ],
        "key": "foo",
        "result": None
    },
    {
        "description": "First hit",
        "containers": [
            { "foo": "bar" },
            { "foo": "baz" }
        ],
        "key": "foo",
        "result": "bar"
    },
    {
        "description": "Third hit",
        "containers": [
            { "boo": "baz" },
            { "zoo": "bam" },
            { "foo": "bar" }
        ],
        "key": "foo",
        "result": "bar"
    }
]

##  Tests getting item values from the container stack.
#
#   \param container_stack A new container stack from a fixture.
#   \param data Individual test cases as loaded from test_getValue_data.
@pytest.mark.parametrize("data", test_getValue_data)
def test_getValue(container_stack, data):
    # Fill the container stack with the containers.
    for container in reversed(data["containers"]): # Reverse order to make sure the last-added item is the top of the list.
        mockup = MockContainer()
        mockup.items = container
        container_stack.addContainer(mockup)

    answer = container_stack.getProperty(data["key"], "value") # Do the actual query.

    assert answer == data["result"]

##  Tests removing containers from the stack.
#
#   \param container_stack A new container stack from a fixture.
def test_removeContainer(container_stack):
    # First test the empty case.
    with pytest.raises(IndexError):
        container_stack.removeContainer(0)

    # Now add data.
    container0 = MockContainer()
    container_stack.addContainer(container0)
    with pytest.raises(IndexError):
        container_stack.removeContainer(1)
    with pytest.raises(IndexError):
        container_stack.removeContainer(-1)
    with pytest.raises(TypeError): # Curveball!
        container_stack.removeContainer("test")
    container_stack.removeContainer(0)
    assert container_stack.getContainers() == []

    # Multiple subcontainers.
    container0 = MockContainer()
    container1 = MockContainer()
    container2 = MockContainer()
    container_stack.addContainer(container0)
    container_stack.addContainer(container1)
    container_stack.addContainer(container2)
    container_stack.removeContainer(1)
    assert container_stack.getContainers() == [container2, container0]

##  Tests replacing a container in the stack.
#
#   \param container_stack A new container stack from a fixture.
def test_replaceContainer(container_stack):
    # First test the empty case.
    with pytest.raises(IndexError):
        container_stack.replaceContainer(0, MockContainer())

    # Now add data.
    container0 = MockContainer()
    container_stack.addContainer(container0)
    container0_replacement = MockContainer()
    with pytest.raises(IndexError):
        container_stack.replaceContainer(1, container0_replacement)
    with pytest.raises(IndexError):
        container_stack.replaceContainer(-1, container0_replacement)
    container_stack.replaceContainer(0, container0_replacement)
    assert container_stack.getContainers() == [container0_replacement]

    # Add multiple containers.
    container1 = MockContainer()
    container_stack.addContainer(container1)
    container2 = MockContainer()
    container_stack.addContainer(container2)
    container1_replacement = MockContainer()
    container_stack.replaceContainer(1, container1_replacement)
    assert container_stack.getContainers() == [container2, container1_replacement, container0_replacement]

    # Try to replace a container with itself.
    with pytest.raises(Exception):
        container_stack.replaceContainer(2, container_stack)
    assert container_stack.getContainers() == [container2, container1_replacement, container0_replacement]

##  Tests serialising and deserialising the container stack.
#
#   \param container_stack A new container stack from a fixture.
def test_serialize(container_stack):
    registry = ContainerRegistry.getInstance() # All containers need to be registered in order to be recovered again after deserialising.

    # First test the empty container stack.
    _test_serialize_cycle(container_stack)

    # Case with one subcontainer.
    container = InstanceContainer(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)
    _test_serialize_cycle(container_stack)

    # Case with two subcontainers.
    container = InstanceContainer(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container) # Already had one, if all previous assertions were correct.
    _test_serialize_cycle(container_stack)

    # Case with all types of subcontainers.
    container = DefinitionContainer(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)
    container = ContainerStack(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)
    _test_serialize_cycle(container_stack)

    # With some metadata.
    container_stack.getMetaData()["foo"] = "bar"
    _test_serialize_cycle(container_stack)

    # With a changed name.
    container_stack.setName("Fred")
    _test_serialize_cycle(container_stack)

    # A name with special characters, to test the encoding.
    container_stack.setName("ルベン")
    _test_serialize_cycle(container_stack)

    # Just to bully the one who implements this, a name with special characters in JSON and CFG.
    container_stack.setName("=,\"")
    _test_serialize_cycle(container_stack)

    # A container that is not in the registry.
    container_stack.addContainer(DefinitionContainer(str(uuid.uuid4())))
    serialised = container_stack.serialize()
    container_stack = ContainerStack(str(uuid.uuid4())) # Completely fresh container stack.
    with pytest.raises(Exception):
        container_stack.deserialize(serialised)


##  Tests serialising and deserialising the container stack with certain metadata keys ignored.
#
#   \param container_stack A new container stack from a fixture.
def test_serialize_with_ignored_metadata_keys(container_stack):
    ignored_metadata_keys = ["secret"]
    registry = ContainerRegistry.getInstance()  # All containers need to be registered in order to be recovered again after deserialising.

    # Case with one subcontainer.
    container = InstanceContainer(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)

    # Case with two subcontainers.
    container = InstanceContainer(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)  # Already had one, if all previous assertions were correct.

    # Case with all types of subcontainers.
    container = DefinitionContainer(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)
    container = ContainerStack(str(uuid.uuid4()))
    registry.addContainer(container)
    container_stack.addContainer(container)

    # With some metadata.
    container_stack.getMetaData()["foo"] = "bar"
    for key in ignored_metadata_keys:
        container_stack.getMetaData()[key] = "something"
    _test_serialize_cycle(container_stack, ignored_metadata_keys = ignored_metadata_keys)

    # With a changed name.
    container_stack.setName("Fred")
    _test_serialize_cycle(container_stack, ignored_metadata_keys = ignored_metadata_keys)

    # A name with special characters, to test the encoding.
    container_stack.setName("ルベン")
    _test_serialize_cycle(container_stack, ignored_metadata_keys = ignored_metadata_keys)

    # Just to bully the one who implements this, a name with special characters in JSON and CFG.
    container_stack.setName("=,\"")
    _test_serialize_cycle(container_stack, ignored_metadata_keys = ignored_metadata_keys)

    # A container that is not in the registry.
    container_stack.addContainer(DefinitionContainer(str(uuid.uuid4())))
    serialised = container_stack.serialize()
    container_stack = ContainerStack(str(uuid.uuid4()))  # Completely fresh container stack.
    with pytest.raises(Exception):
        container_stack.deserialize(serialised)


##  Tests whether changing the name of the stack has the proper effects.
#
#   \param container_stack A new container stack from a fixture.
#   \param application An application containing the thread handle for signals.
#   Must be included for the signal to check against the main thread in
#   auto-mode.
def test_setName(container_stack, application):
    name_change_counter = 0
    def increment_name_change_counter():
        nonlocal name_change_counter
        name_change_counter += 1
    container_stack.nameChanged.connect(increment_name_change_counter) # To make sure it emits the signal.

    different_name = "test"
    if container_stack.getName() == different_name:
        different_name = "tast" #Make sure it is actually different!
    container_stack.setName(different_name)
    assert container_stack.getName() == different_name # Name is correct.
    assert name_change_counter == 1 # Correctly signalled once.

    different_name += "_new" # Make it different again.
    container_stack.setName(different_name)
    assert container_stack.getName() == different_name # Name is updated again.
    assert name_change_counter == 2 # Correctly signalled once again.

    container_stack.setName(different_name) # Not different this time.
    assert container_stack.getName() == different_name
    assert name_change_counter == 2 # Didn't signal.

##  Tests the next stack functionality.
#
#   \param container_stack A new container stack from a fixture.
def test_setNextStack(container_stack):
    container = MockContainer()
    container_stack.setNextStack(container)
    assert container_stack.getNextStack() == container

    with pytest.raises(Exception):
        container_stack.setNextStack(container_stack) # Can't set itself as next stack.

##  Test backward compatibility of container config file format change
#
#   This tests whether ContainerStack can still deserialize containers using the old
#   format where we would have a single comma separated entry with the containers.
def test_backwardCompatibility(container_stack, container_registry):
    container_a = MockContainer("a")
    container_registry.addContainer(container_a) # Make sure this container isn't the one it complains about.

    serialised = """
    [general]
    name = Test
    id = testid
    version = {version}
    containers = a,a,a
    """.format(version = ContainerStack.Version) # Old-style serialized stack

    container_stack.deserialize(serialised)
    assert container_stack.getContainers() == [container_a, container_a, container_a]

##  Test serialization and deserialization of a stack with containers with special characters in their ID
#
def test_idSpecialCharacters(container_stack, container_registry):
    container_ab = MockContainer("a,b") # Comma used to break deserialize
    container_registry.addContainer(container_ab)

    serialized = """
    [general]
    name = Test
    id = testid
    version = {version}
    containers = a,b
    """.format(version = ContainerStack.Version)

    with pytest.raises(Exception):
        # Using old code, this would fail because it tries to add two containers, a and b.
        container_stack.deserialize(serialized)

    serialized = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    0 = a,b
    """.format(version = ContainerStack.Version)

    container_stack.deserialize(serialized)
    assert container_stack.getContainers() == [container_ab]

    test_container_0 = MockContainer("= TestContainer with, some? Special $ Characters #12")
    container_registry.addContainer(test_container_0)

    serialized = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    0 = = TestContainer with, some? Special $ Characters #12
    """.format(version = ContainerStack.Version)

    container_stack.deserialize(serialized)
    assert container_stack.getContainers() == [test_container_0]

    test_container_1 = MockContainer("☂℮﹩⊥ ḉ◎η☂αїη℮ґ")
    container_registry.addContainer(test_container_1)

    # Special unicode characters are handled properly
    serialized = """
    [general]
    name = Test
    id = testid
    version = {version}

    [containers]
    0 = ☂℮﹩⊥ ḉ◎η☂αїη℮ґ
    """.format(version = ContainerStack.Version)

    container_stack.deserialize(serialized)
    assert container_stack.getContainers() == [test_container_1]

    serialized = container_stack.serialize()

    # Unfortunately, we cannot check that serialized == container_stack.serialized() due to dict
    # having a random order.
    assert "id = testid" in serialized
    assert "name = Test" in serialized
    assert "0 = ☂℮﹩⊥ ḉ◎η☂αїη℮ґ" in serialized


##  Tests a single cycle of serialising and deserialising a container stack.
#
#   This will serialise and then deserialise the container stack, and sees if
#   the deserialised container stack is the same as the original one.
#
#   \param container_stack The container stack to serialise and deserialise.
#   \param ignored_metadata_keys The list of keys that should be ignored when serializing the container stack.
def _test_serialize_cycle(container_stack, ignored_metadata_keys = None):
    name = container_stack.getName()
    metadata = {key: value for key, value in container_stack.getMetaData().items()}
    containers = container_stack.getContainers()

    serialised = container_stack.serialize(ignored_metadata_keys = ignored_metadata_keys)
    container_stack = ContainerStack(str(uuid.uuid4()))  # Completely fresh container stack.
    container_stack.deserialize(serialised)

    # remove ignored keys from metadata dict
    if ignored_metadata_keys:
        for key in ignored_metadata_keys:
            if key in metadata:
                del metadata[key]

    #ID and nextStack are allowed to be different.
    assert name == container_stack.getName()
    assert metadata == container_stack.getMetaData()
    assert containers == container_stack.getContainers()
