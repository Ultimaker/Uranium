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
    ##  Gets an arbitrary ID.
    #
    #   \return Some integer.
    def getId(self):
        return 42

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
    #   Since the container is always the same, a constant string suffices. For
    #   a functional serialisation, please use an actual implementation rather
    #   than this mock, because this container can't contain any items. This
    #   choice was made because making this work for the mock container would
    #   have a high risk of bugs, which would distract development time.
    #
    #   \return A static string representing a container.
    def serialize(self):
        return "x"

    ##  Deserialises a string to a container.
    #
    #   Since this mock container is always the same, no deserialising can be
    #   done and it only checks if the serialized string "has the proper
    #   format". For a functional deserialisation, please use an actual
    #   implementation rather than this mock, because this container can't
    #   contain any items. This choice was made because making this work for the
    #   mock container would have a high risk of bugs, which would distract
    #   development time.
    #
    #   \param serialized A serialised mock container.
    def deserialize(self, serialized):
        if serialized != "x":
            raise Exception("This serialisation doesn't have the correct format.")

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

##  Tests getting and changing the metadata of the container stack.
#
#   \param container_stack A new container stack from a fixture.
def test_getMetaData(container_stack):
    meta_data = container_stack.getMetaData()
    assert meta_data != None

    meta_data["foo"] = "bar" #Try adding an entry.
    assert container_stack.getMetaDataEntry("foo") == "bar"