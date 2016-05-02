# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import uuid # For creating unique ID's for each container stack.

import UM.Settings
import UM.Settings.ContainerInterface

##  A fake container class that implements ContainerInterface.
#
#   This allows us to test the container stack independent of any actual
#   implementation of the containers. If something were to go wrong in the
#   actual implementations, the tests in this suite are unaffected.
class MockContainer(UM.Settings.ContainerInterface.ContainerInterface):
    ##  Creates a mock container with a new unique ID.
    def __init__(self):
        self._id = uuid.uuid4().int

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

    ##  Gives empty metadata.
    #
    #   \return An empty dictionary representing the metadata.
    def getMetaData(self):
        return {}

    ##  Gets an entry from the metadata.
    #
    #   Since the metadata is empty, this always returns the default.
    #
    #   \param entry The entry to get from the metadata.
    #   \param default The default value in case the entry is missing.
    #   \return The provided default value (None by default).
    def getMetaDataEntry(self, entry, default = None):
        return default

    ##  Gets the value of a container item.
    #
    #   Since this container can't have any items, the result is always None. If
    #   you wish to test something with actual items in it, please use an actual
    #   implementation rather than this mock. This choice was made because
    #   making this work for the mock container would have a high risk of bugs,
    #   which would distract development time.
    #
    #   \param key The key of the item to get.
    def getValue(self, key):
        return None

    ##  Serialises this container.
    #
    #   The only different data for this container is the ID, so that is
    #   serialised. For a functional serialisation, please use an actual
    #   implementation rather than this mock, because this container can't
    #   contain any items. This choice was made because making this work for the
    #   mock container would have a high risk of bugs, which would distract
    #   development time.
    #
    #   \return A static string representing a container.
    def serialize(self):
        return str(self._id)

    ##  Deserialises a string to a container.
    #
    #   Since the only different data can be the ID, the string is parsed as an
    #   integer ID. For a functional deserialisation, please use an actual
    #   implementation rather than this mock, because this container can't
    #   contain any items. This choice was made because making this work for the
    #   mock container would have a high risk of bugs, which would distract
    #   development time.
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

    assert container_stack.getContainer(0) == container1
    assert container_stack.getContainer(1) == container2
    assert container_stack.getContainer(2) == container3
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

##  Tests serialising and deserialising the container stack.
def test_serialize(container_stack):
    # First test the empty container stack.
    _test_serialize_cycle(container_stack)

    # Case with one subcontainer.
    container_stack.addContainer(MockContainer())
    _test_serialize_cycle(container_stack)

    # Case with two subcontainers.
    container_stack.addContainer(MockContainer()) #Already had one, if all previous assertions were correct.
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

##  Tests a single cycle of serialising and deserialising a container stack.
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
    assert containers == container_stack.getContainers()