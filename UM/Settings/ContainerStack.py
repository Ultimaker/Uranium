# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter

from . import ContainerInterface

##  A stack of setting containers to handle setting value retrieval.
@signalemitter
class ContainerStack(ContainerInterface.ContainerInterface):
    Version = 1

    ##  Constructor
    #
    #   \param stack_id \type{string} A unique, machine readable/writable ID.
    def __init__(self, stack_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = stack_id
        self._name = stack_id
        self._metadata = {}
        self._containers = []
        self._next_stack = None

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self):
        return self._id

    ##  \copydoc ContainerInterface::getName
    #
    #   Reimplemented from ContainerInterface
    def getName(self):
        return self._name

    nameChanged = Signal()

    def setName(self, name):
        if name != self._name:
            self._name = name
            self.nameChanged.emit()

    ##  \copydoc ContainerInterface::getMetaData
    #
    #   Reimplemented from ContainerInterface
    def getMetaData(self):
        return self._metadata

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry, default = None):
        return self._metadata.get(entry, default)

    ##  \copydoc ContainerInterface::getValue
    #
    #   Reimplemented from ContainerInterface.
    #
    #   getValue will start at the top of the stack and try to get the value
    #   specified. If that container returns no value, the next container on the
    #   stack will be tried and so on until the bottom of the stack is reached.
    #   If a next stack is defined for this stack it will then try to get the
    #   value from that stack. If no next stack is defined, None will be returned.
    def getValue(self, key):
        return None

    ##  \copydoc ContainerInterface::serialize
    #
    #   Reimplemented from ContainerInterface
    def serialize(self):
        return ""

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    def deserialize(self, serialized):
        pass

    ##  Get a list of all containers in this stack.
    #
    #   \return \type{list} A list of all containers in this stack.
    def getContainers(self):
        return self._containers

    ##  Get a container by index.
    #
    #   \param index \type{int} The index of the container to get.
    #
    #   \return The container at the specified index.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    def getContainer(self, index):
        return None

    ##  Find a container matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing key and value pairs that need to match the container.
    #
    #   \return The first container that matches the filter criteria or None if not found.
    def findContainer(self, filter):
        return None

    ##  Add a container to the top of the stack.
    #
    #   \param container The container to add to the stack.
    def addContainer(self, container):
        pass

    ##  Replace a container in the stack.
    #
    #   \param index \type{int} The index of the container to replace.
    #   \param container The container to replace the existing entry with.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    def replaceContainer(self, index, container):
        pass

    ##  Remove a container from the stack.
    #
    #   \param index \type{int} The index of the container to remove.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    def removeContainer(self, index = 0):
        pass

    ##  Get the next stack
    #
    #   The next stack is the stack that is searched for a setting value if the
    #   bottom of the stack is reached when searching for a value.
    #
    #   \return \type{ContainerStack} The next stack or None if not set.
    def getNextStack(self):
        return self._next_stack

    ##  Set the next stack
    #
    #   \param stack \type{ContainerStack} The next stack to set. Can be None.
    #
    #   \sa getNextStack
    def setNextStack(self, stack):
        self._next_stack = stack
