# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.
import configparser
import io

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject

from . import ContainerInterface


class IncorrectVersionError(Exception):
    pass


class InvalidContainerStackError(Exception):
    pass


##  A stack of setting containers to handle setting value retrieval.
@signalemitter
class ContainerStack(ContainerInterface.ContainerInterface, PluginObject):
    Version = 2

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
        return str(self._name)

    ##  Emitted whenever the name of this stack changes.
    nameChanged = Signal()

    ##  Set the name of this stack.
    #
    #   \param name \type{string} The new name of the stack.
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
        for container in self._containers:
            value = container.getValue(key)
            if value is not None:
                return value

        if self._next_stack:
            return self._next_stack.getValue(key)
        else:
            return None

    ##  \copydoc ContainerInterface::serialize
    #
    #   Reimplemented from ContainerInterface
    def serialize(self):
        parser = configparser.ConfigParser(interpolation = None, empty_lines_in_values = False)

        parser["general"] = {}
        parser["general"]["version"] = str(self.Version)
        parser["general"]["name"] = str(self._name)
        parser["general"]["id"] = str(self._id)

        parser["metadata"] = {}
        for key, value in self._metadata.items():
            parser["metadata"][key] = str(value)

        parser["containers"] = {}
        parser["containers"]["length"] = str(len(self._containers))
        for index, container in enumerate(self._containers):
            parser["containers"][str(index)] = container.serialize()

        stream = io.StringIO()
        parser.write(stream)
        return stream.getvalue()

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    def deserialize(self, serialized):
        parser = configparser.ConfigParser(interpolation=None, empty_lines_in_values=False)
        parser.read_string(serialized)

        if not "general" in parser or not "version" in parser["general"] or not "name" in parser["general"] or not "id" in parser["general"]:
            raise InvalidContainerStackError("Missing required section 'general' or 'version' property")

        if parser["general"].getint("version") != self.Version:
            raise IncorrectVersionError

        self._name = parser["general"].get("name")
        self._id = parser["general"].get("id")

        if "metadata" in parser:
            self._metadata = dict(parser["metadata"])

        ## TODO; Deserialize the containers.

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
        if index == -1:
            raise IndexError
        return self._containers[index]

    ##  Find a container matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing key and value pairs that need to match the container.
    #
    #   \return The first container that matches the filter criteria or None if not found.
    def findContainer(self, filter):
        for container in self._containers:
            meta_data = container.getMetaData()
            match = True
            print(filter, meta_data)
            for key in filter:
                try:
                    if meta_data[key] == filter[key]:
                        continue
                    else:
                        match = False
                        break
                except KeyError:
                    match = False
                    break

            if match:
                return container

        return None

    ##  Add a container to the top of the stack.
    #
    #   \param container The container to add to the stack.
    def addContainer(self, container):
        if container is not self:
            self._containers.insert(0, container)
        else:
            raise Exception("Unable to add stack to itself.")

    ##  Replace a container in the stack.
    #
    #   \param index \type{int} The index of the container to replace.
    #   \param container The container to replace the existing entry with.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    #   \exception Exception when trying to replace container ContainerStack.
    def replaceContainer(self, index, container):
        if index == -1:
            raise IndexError
        if container == self:
            raise Exception("Unable to replace container with ContainerStack (self) ")
        self._containers[index] = container

    ##  Remove a container from the stack.
    #
    #   \param index \type{int} The index of the container to remove.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    def removeContainer(self, index = 0):
        if index == -1:
            raise IndexError
        try:
            del self._containers[index]
        except TypeError:
            raise IndexError("Can't delete container with intex %s" % index)

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
