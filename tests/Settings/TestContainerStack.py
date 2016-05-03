# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import uuid # For creating unique ID's for each container stack.

import UM.Settings
import UM.Settings.ContainerInterface
import UM.Settings.DefinitionContainer
import UM.Settings.InstanceContainer
import UM.Settings.ContainerStack

##  A fake container class that implements ContainerInterface.
#
#   This allows us to test the container stack independent of any actual
#   implementation of the containers. If something were to go wrong in the
#   actual implementations, the tests in this suite are unaffected.
class MockContainer(UM.Settings.ContainerInterface.ContainerInterface):
    ##  Creates a mock container with a new unique ID.
    def __init__(self):
        self._id = uuid.uuid4().int
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

    ##  Gets the value of a container item.
    #
    #   If the key doesn't exist, returns None.
    #
    #   \param key The key of the item to get.
    def getValue(self, key):
        if key in self.items:
            return self.items[key]
        return None

    ##  Serialises this container.
    #
    #   The serialisation of the mock needs to be kept simple, so it only
    #   serialises the ID. This makes the tests succeed if the serialisation
    #   creates different instances (which is desired).
    #
    #   \return A static string representing a container.
    def serialize(self):
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

##  Creates a brand new container stack to test with.
#
#   The container stack will get a new, unique ID.
@pytest.fixture
def container_stack():
    return UM.Settings.ContainerStack(uuid.uuid4().int)

##  Tests the creation of a container stack.
#
#   The actual creation is done in a fixture though.
#
#   \param container_stack A new container stack from a fixture.
def test_container_stack(container_stack):
    assert container_stack != None

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
    assert meta_data != None

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

    answer = container_stack.getValue(data["key"]) # Do the actual query.

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
    with pytest.raises(IndexError): # Curveball!
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
    assert container_stack.getContainers() == [container0_replacement, container1_replacement, container2]

    # Try to replace a container with itself.
    with pytest.raises(Exception):
        container_stack.replaceContainer(2, container_stack)
    assert container_stack.getContainers() == [container0_replacement, container1_replacement, container2]

##  Tests serialising and deserialising the container stack.
#
#   \param container_stack A new container stack from a fixture.
def test_serialize(container_stack):
    # First test the empty container stack.
    _test_serialize_cycle(container_stack)

    # Case with one subcontainer.
    container_stack.addContainer(UM.Settings.InstanceContainer(uuid.uuid4()))
    _test_serialize_cycle(container_stack)

    # Case with two subcontainers.
    container_stack.addContainer(UM.Settings.InstanceContainer(uuid.uuid4())) #Already had one, if all previous assertions were correct.
    _test_serialize_cycle(container_stack)

    # Case with all types of subcontainers.
    container_stack.addContainer(UM.Settings.DefinitionContainer(uuid.uuid4()))
    container_stack.addContainer(UM.Settings.ContainerStack(uuid.uuid4()))
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

##  Tests whether changing the name of the stack has the proper effects.
#
#   \param container_stack A new container stack from a fixture.
def test_setName(container_stack):
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

##  Tests if two container lists are equal.
#
#   It doesn't test for the instances themselves to be equal, but for their data
#   to be equal.
#
#   \param containers_1 The list of containers to be checked for equality
#   against containers_2.
#   \param containers_2 The list of containers to be checked for equality
#   against containers_1.
def _test_deep_container_equality(containers_1, containers_2):
    assert len(containers_1) == len(containers_2)
    for i in range(0, len(containers_1)):
        assert containers_1[i].getId() == containers_2[i].getId()
        assert containers_1[i].getName() == containers_2[i].getName()
        assert containers_1[i].getMetaData() == containers_2[i].getMetaData()
        _test_deep_container_equality(containers_1[i].getContainers(), containers_2[i].getContainers())
        # Not checking the next container... That'd complicate the test a whole lot more!

##  Tests a single cycle of serialising and deserialising a container stack.
#
#   This will serialise and then deserialise the container stack, and sees if
#   the deserialised container stack is the same as the original one.
#
#   \param container_stack The container stack to serialise and deserialise.
def _test_serialize_cycle(container_stack):
    name = container_stack.getName()
    metadata = container_stack.getMetaData()
    containers = container_stack.getContainers()

    serialised = container_stack.serialize()
    container_stack = UM.Settings.ContainerStack(uuid.uuid4().int) # Completely fresh container stack.
    container_stack.deserialize(serialised)

    #ID and nextStack are allowed to be different.
    assert name == container_stack.getName()
    assert metadata == container_stack.getMetaData()
    new_containers = container_stack.getContainers()
    _test_deep_container_equality(containers, new_containers)