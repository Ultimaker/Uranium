# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import re #For finding containers with asterisks in the constraints.
import urllib

from UM.PluginRegistry import PluginRegistry
from UM.Resources import Resources, UnsupportedStorageTypeError
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Logger import Logger
from UM.SaveFile import SaveFile
from UM.Signal import Signal, signalemitter

from . import DefinitionContainer
from . import InstanceContainer
from . import ContainerStack

##  Central class to manage all Setting containers.
#
#
@signalemitter
class ContainerRegistry:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mime = MimeType(
            name = "application/x-uranium-definitioncontainer",
            comment = "Uranium Definition Container",
            suffixes = [ "def.json" ]
        )
        MimeTypeDatabase.addMimeType(mime)
        mime = MimeType(
            name = "application/x-uranium-instancecontainer",
            comment = "Uranium Instance Container",
            suffixes = [ "inst.cfg" ]
        )
        MimeTypeDatabase.addMimeType(mime)
        mime = MimeType(
            name = "application/x-uranium-containerstack",
            comment = "Uranium Container Stack",
            suffixes = [ "stack.cfg" ]
        )
        MimeTypeDatabase.addMimeType(mime)

        self._emptyInstanceContainer = _EmptyInstanceContainer("empty")

        self._containers = [ self._emptyInstanceContainer ]

        self._resource_types = [Resources.DefinitionContainers]

    containerAdded = Signal()
    containerRemoved = Signal()

    def addResourceType(self, type):
        self._resource_types.append(type)

    ##  Find all DefinitionContainer objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the
    #   DefinitionContainer. An asterisk in the values can be used to denote a
    #   wildcard.
    def findDefinitionContainers(self, **kwargs):
        return self.findContainers(DefinitionContainer.DefinitionContainer, **kwargs)

    ##  Find all InstanceContainer objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the
    #   InstanceContainer. An asterisk in the values can be used to denote a
    #   wildcard.
    def findInstanceContainers(self, **kwargs):
        return self.findContainers(InstanceContainer.InstanceContainer, **kwargs)

    ##  Find all ContainerStack objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the ContainerStack.
    #   An asterisk in the values can be used to denote a wildcard.
    def findContainerStacks(self, **kwargs):
        return self.findContainers(ContainerStack.ContainerStack, **kwargs)

    ##  Find all container objects matching certain criteria.
    #
    #   \param container_type If provided, return only objects that are
    #   instances or subclasses of container_type.
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the container. An
    #   asterisk can be used to denote a wildcard.
    #
    #   \return A list of containers matching the search criteria, or an empty
    #   list if nothing was found.
    def findContainers(self, container_type = None, **kwargs):
        containers = []
        for container in self._containers:
            if container_type and not isinstance(container, container_type):
                continue

            matches_container = True
            for key, value in kwargs.items():
                try:
                    value = re.escape(value) #Escape for regex patterns.
                    value = "^" + value.replace("\\*", ".*") + "$" #Instead of (now escaped) asterisks, match on any string. Also add anchors for a complete match.
                    value_pattern = re.compile(value)
                    if key == "id":
                        if not value_pattern.match(container.getId()):
                            matches_container = False
                        continue
                    if key == "name":
                        if not value_pattern.match(container.getName()):
                            matches_container = False
                        continue
                    if key == "definition":
                        try:
                            if not value_pattern.match(container.getDefinition().getId()):
                                matches_container = False
                            continue
                        except AttributeError:  # Only instanceContainers have a get definition. We can ignore all others.
                            pass
                    if not value_pattern.match(str(container.getMetaDataEntry(key))):
                        matches_container = False
                except TypeError: #Value was not a string.
                    if key == "id":
                        if value != container.getId():
                            matches_container = False
                        continue
                    if key == "name":
                        if container.getName() != value:
                            matches_container = False
                        continue
                    if key == "definition":
                        try:
                            if value != container.getDefinition().getId():
                                matches_container = False
                            continue
                        except AttributeError:
                            pass
                    if value != container.getMetaDataEntry(key):
                        matches_container = False
                    continue

            if matches_container:
                containers.append(container)

        return containers

    ##  This is a small convenience to make it easier to support complex structures in ContainerStacks.
    def getEmptyInstanceContainer(self):
        return self._emptyInstanceContainer

    ##  Add a container type that will be used to serialize/deserialize containers.
    #
    #   \param container An instance of the container type to add.
    @classmethod
    def addContainerType(cls, container):
        plugin_id = container.getPluginId()
        cls.__container_types[plugin_id] = container.__class__

        metadata = PluginRegistry.getInstance().getMetaData(plugin_id)
        cls.__mime_type_map[metadata["settings_container"]["mimetype"]] = container.__class__

    ##  Load all available definition containers, instance containers and
    #   container stacks.
    #
    #   If this function is called again, it will clear the old data and reload.
    def load(self):
        files = []
        files_resource_type = []
        for resource_type in self._resource_types:
            resources = Resources.getAllResourcesOfType(resource_type)
            files.extend(resources)
            files_resource_type.extend([resource_type]*len(resources))

        for file_path, resource_type in zip(files, files_resource_type):
            try:
                mime = MimeTypeDatabase.getMimeTypeForFile(file_path)
                container_type = self.__mime_type_map.get(mime.name)
                container_id = mime.stripExtension(os.path.basename(file_path))

                ## Ensure that all special characters are encoded back.
                container_id = urllib.parse.unquote_plus(container_id)

                read_only = True
                try:
                    read_only = os.path.dirname(file_path) != (Resources.getStoragePathForType(resource_type))
                except UnsupportedStorageTypeError:
                    pass

                if container_type is None:
                    Logger.log("w", "Unable to detect container type for %s", mime.name)
                    continue

                new_container = container_type(container_id)
                with open(file_path, encoding = "utf-8") as f:
                    new_container.deserialize(f.read())
                new_container.setReadOnly(read_only)
                self._containers.append(new_container)
            except Exception as e:
                Logger.logException("e", "Could not deserialize container %s", container_id)

    def addContainer(self, container):
        containers = self.findContainers(container_type = container.__class__, id = container.getId())
        if containers:
            Logger.log("w", "Container of type %s and id %s already added", repr(container.__class__), container.getId())
            return

        self._containers.append(container)
        self.containerAdded.emit(container)

    def removeContainer(self, container_id):
        containers = self.findContainers(None, id = container_id)
        if containers:
            container = containers[0]

            self._containers.remove(container)
            self._deleteFiles(container)
            self.containerRemoved.emit(container)

            Logger.log("d", "Removed container %s", container.getId())

        else:
            Logger.log("w", "Could not remove container with id %s, as no container with that ID is known")

    def saveAll(self):

        for instance in self.findInstanceContainers():
            if not instance.isDirty():
                continue

            try:
                data = instance.serialize()
            except NotImplementedError:
                # Serializing is not supported so skip this container
                continue
            except Exception:
                Logger.logException("e", "An exception occurred trying to serialize container %s", instance.getId())
                continue

            file_name = urllib.parse.quote_plus(instance.getId()) + ".inst.cfg"
            path = Resources.getStoragePath(Resources.InstanceContainers, file_name)
            with SaveFile(path, "wt", -1, "utf-8") as f:
                f.write(data)

        for stack in self.findContainerStacks():
            if not stack.isDirty():
                continue

            try:
                data = stack.serialize()
            except NotImplementedError:
                # Serializing is not supported so skip this container
                continue
            except Exception:
                Logger.logException("e", "An exception occurred trying to serialize container %s", stack.getId())
                continue

            file_name = urllib.parse.quote_plus(stack.getId()) + ".stack.cfg"
            path = Resources.getStoragePath(Resources.ContainerStacks, file_name)
            with SaveFile(path, "wt", -1, "utf-8") as f:
                f.write(data)

        for definition in self.findDefinitionContainers():
            try:
                data = definition.serialize()
            except NotImplementedError:
                # Serializing is not supported so skip this container
                continue
            except Exception:
                Logger.logException("e", "An exception occurred trying to serialize container %s", instance.getId())
                continue

            file_name = urllib.parse.quote_plus(definition.getId()) + ".def.cfg"
            path = Resources.getStoragePath(Resources.DefinitionContainers, file_name)
            with SaveFile(path, "wt", -1, "utf-8") as f:
                f.write(data)

    ##  Creates a new unique name for a container that doesn't exist yet.
    #
    #   It tries if the original name you provide exists, and if it doesn't
    #   it'll add a " #1" or " #2" after the name to make it unique.
    #
    #   \param original The original name that may not be unique.
    #   \return A unique name that looks a lot like the original but may have
    #   a number behind it to make it unique.
    def uniqueName(self, original):
        name = original.strip()
        num_check = re.compile("(.*?)\s*#\d$").match(name)
        if num_check: #There is a number in the name.
            name = num_check.group(1) #Filter out the number.
        if name == "": #Wait, that deleted everything!
            name = "Profile"
        unique_name = name

        i = 1
        while self.findContainers(id = unique_name) or self.findContainers(name = unique_name): #A container already has this name.
            i += 1 #Try next numbering.
            unique_name = "%s #%d" % (name, i) #Fill name like this: "Extruder #2".
        return unique_name

    # Remove all files related to a container located in a storage path
    #
    # Since we cannot assume we can write to any other path, we can only support removing from
    # a storage path. This effectively "resets" a container that is located in another resource
    # path.
    def _deleteFiles(self, container):
        for resource_type in self._resource_types:
            mime_type_name = ""
            for name, container_type in self.__mime_type_map.items():
                if container_type == container.__class__:
                    mime_type_name = name
                    break
            else:
                return

            mime_type = MimeTypeDatabase.getMimeType(mime_type_name)

            for suffix in mime_type.suffixes:
                try:
                    path = Resources.getStoragePath(resource_type, urllib.parse.quote_plus(container.getId()) + "." + suffix)
                    if os.path.isfile(path):
                        os.remove(path)
                except Exception:
                    continue

    ##  Get the singleton instance for this class.
    @classmethod
    def getInstance(cls):
        # Note: Explicit use of class name to prevent issues with inheritance.
        if ContainerRegistry.__instance is None:
            ContainerRegistry.__instance = cls()
        return ContainerRegistry.__instance

    __instance = None

    __container_types = {
        "definition": DefinitionContainer.DefinitionContainer,
        "instance": InstanceContainer.InstanceContainer,
        "stack": ContainerStack.ContainerStack,
    }

    __mime_type_map = {
        "application/x-uranium-definitioncontainer": DefinitionContainer.DefinitionContainer,
        "application/x-uranium-instancecontainer": InstanceContainer.InstanceContainer,
        "application/x-uranium-containerstack": ContainerStack.ContainerStack,
    }

PluginRegistry.addType("settings_container", ContainerRegistry.addContainerType)

class _EmptyInstanceContainer(InstanceContainer.InstanceContainer):
    def isDirty(self):
        return False

    def getProperty(self, key, property_name):
        return None

    def setProperty(self, key, property_name, property_value):
        return
