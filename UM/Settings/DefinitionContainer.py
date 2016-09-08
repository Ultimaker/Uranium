# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import json
import collections
import copy

from UM.Resources import Resources
from UM.PluginObject import PluginObject
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType
from UM.Signal import Signal

from . import ContainerInterface
from . import SettingDefinition
from . import SettingRelation
from . import SettingFunction

class InvalidDefinitionError(Exception):
    pass

class IncorrectDefinitionVersionError(Exception):
    pass

class InvalidOverrideError(Exception):
    pass

MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-definitioncontainer",
        comment = "Uranium Definition Container",
        suffixes = ["def.json"]
    )
)

##  A container for SettingDefinition objects.
#
#
class DefinitionContainer(ContainerInterface.ContainerInterface, PluginObject):
    Version = 2

    ##  Constructor
    #
    #   \param container_id A unique, machine readable/writable ID for this container.
    def __init__(self, container_id, i18n_catalog = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = str(container_id)
        self._name = container_id
        self._metadata = {}
        self._definitions = []
        self._inherited_files = []
        self._i18n_catalog = i18n_catalog

        self._definition_cache = {}
        self._path = ""

    ##  Reimplement __setattr__ so we can make sure the definition remains unchanged after creation.
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        #raise NotImplementedError()

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self):
        return self._id

    id = property(getId)

    ##  \copydoc ContainerInterface::getName
    #
    #   Reimplemented from ContainerInterface
    def getName(self):
        return self._name

    name = property(getName)

    ##  \copydoc ContainerInterface::isReadOnly
    #
    #   Reimplemented from ContainerInterface
    def isReadOnly(self):
        return True

    def setReadOnly(self, read_only):
        pass

    ##  \copydoc ContainerInterface::getPath.
    #
    #   Reimplemented from ContainerInterface
    def getPath(self):
        return self._path

    ##  \copydoc ContainerInterface::setPath
    #
    #   Reimplemented from ContainerInterface
    def setPath(self, path):
        self._path = path

    ##  \copydoc ContainerInterface::getMetaData
    #
    #   Reimplemented from ContainerInterface
    def getMetaData(self):
        return self._metadata

    metaData = property(getMetaData)

    @property
    def definitions(self):
        return self._definitions

    ##  Gets all ancestors of this definition container.
    #
    #   This returns the definition in the "inherits" property of this
    #   container, and the definition in its "inherits" property, and so on. The
    #   ancestors are returned in order from parent to
    #   grand-grand-grand-...-grandparent, normally ending in a "root"
    #   container.
    #
    #   \return A list of ancestors, in order from near ancestor to the root.
    def getInheritedFiles(self):
        return self._inherited_files

    ##  Gets all keys of settings in this container.
    #
    #   \return A set of all keys of settings in this container.
    def getAllKeys(self):
        keys = set()
        for definition in self.definitions:
            keys |= definition.getAllKeys()
        return keys

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry, default = None):
        return self._metadata.get(entry, default)

    ##  \copydoc ContainerInterface::getProperty
    #
    #   Reimplemented from ContainerInterface.
    def getProperty(self, key, property_name):
        definition = self._getDefinition(key)
        if not definition:
            return None

        try:
            value = getattr(definition, property_name)
            if value is None and property_name == "value":
                value = getattr(definition, "default_value")
            return value
        except AttributeError:
            return None

    ##  \copydoc ContainerInterface::hasProperty
    #
    #   Reimplemented from ContainerInterface
    def hasProperty(self, key, property_name):
        definition = self._getDefinition(key)
        if not definition:
            return False
        return hasattr(definition, property_name)

    ##  This signal is unused since the definition container is immutable, but is provided for API consistency.
    propertyChanged = Signal()

    ##  \copydoc ContainerInterface::serialize
    #
    #   TODO: This implementation flattens the definition container, since the
    #   data about inheritance and overrides was lost when deserialising.
    #
    #   Reimplemented from ContainerInterface
    def serialize(self):
        data = { } # The data to write to a JSON file.
        data["name"] = self.getName()
        data["version"] = DefinitionContainer.Version
        data["metadata"] = self.getMetaData()

        data["settings"] = { }
        for definition in self.definitions:
            data["settings"][definition.key] = definition.serialize_to_dict()

        return json.dumps(data, separators = (", ", ": "), indent = 4) # Pretty print the JSON.

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    def deserialize(self, serialized):
        parsed = json.loads(serialized, object_pairs_hook=collections.OrderedDict)

        self._verifyJson(parsed)

        # Pre-process the JSON data to include inherited data and overrides
        if "inherits" in parsed:
            inherited = self._resolveInheritance(parsed["inherits"])
            parsed = self._mergeDicts(inherited, parsed)

        if "overrides" in parsed:
            for key, value in parsed["overrides"].items():
                setting = self._findInDict(parsed["settings"], key)
                if setting is None:
                    Logger.log("w","Unable to override setting %s", key)
                else:
                    setting.update(value)

        # If we do not have metadata or settings the file is invalid
        if not "metadata" in parsed:
            raise InvalidDefinitionError("Missing required metadata section")

        if not "settings" in parsed:
            raise InvalidDefinitionError("Missing required settings section")

        # Update properties with the data from the JSON
        self._name = parsed["name"]
        self._metadata = parsed["metadata"]

        for key, value in parsed["settings"].items():
            definition = SettingDefinition.SettingDefinition(key, self, None, self._i18n_catalog)
            definition.deserialize(value)
            self._definitions.append(definition)

        for definition in self._definitions:
            self._updateRelations(definition)

    ##  Find definitions matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing key-value pairs which should match properties of the definition.
    def findDefinitions(self, **kwargs):
        if len(kwargs) == 1 and "key" in kwargs:
            # If we are searching for a single definition by exact key, we can speed up things by retrieving from the cache.
            key = kwargs.get("key")
            if key in self._definition_cache:
                return [self._definition_cache[key]]

        definitions = []
        for definition in self._definitions:
            definitions.extend(definition.findDefinitions(**kwargs))

        return definitions

    # protected:

    # Load a file from disk, used to handle inheritance and includes
    def _loadFile(self, file_name):
        path = Resources.getPath(Resources.DefinitionContainers, file_name + ".def.json")
        contents = {}
        with open(path, encoding = "utf-8") as f:
            contents = json.load(f, object_pairs_hook=collections.OrderedDict)

        self._inherited_files.append(path)
        return contents

    # Recursively resolve loading inherited files
    def _resolveInheritance(self, file_name):
        result = {}

        json = self._loadFile(file_name)
        self._verifyJson(json)

        if "inherits" in json:
            inherited = self._resolveInheritance(json["inherits"])
            json = self._mergeDicts(inherited, json)

        return json

    # Verify that a loaded json matches our basic expectations.
    def _verifyJson(self, json):
        if not "version" in json:
            raise InvalidDefinitionError("Missing required property 'version'")

        if not "name" in json:
            raise InvalidDefinitionError("Missing required property 'name'")

        if json["version"] != self.Version:
            raise IncorrectDefinitionVersionError("Definition uses version {0} but expected version {1}".format(json["version"], self.Version))

    # Recursively find a key in a dictionary
    def _findInDict(self, dictionary, key):
        if key in dictionary: return dictionary[key]
        for k, v in dictionary.items():
            if isinstance(v, dict):
                item = self._findInDict(v, key)
                if item is not None:
                    return item

    # Recursively merge two dictionaries, returning a new dictionary
    def _mergeDicts(self, first, second):
        result = copy.deepcopy(first)
        for key, value in second.items():
            if key in result:
                if isinstance(value, dict):
                    result[key] = self._mergeDicts(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    # Recursively update relations of settings
    def _updateRelations(self, definition):
        for property in SettingDefinition.SettingDefinition.getPropertyNames(SettingDefinition.DefinitionPropertyType.Function):
            self._processFunction(definition, property)

        for child in definition.children:
            self._updateRelations(child)

    # Create relation objects for all settings used by a certain function
    def _processFunction(self, definition, property):
        try:
            function = getattr(definition, property)
        except AttributeError:
            return

        if not isinstance(function, SettingFunction.SettingFunction):
            return

        for setting in function.getUsedSettingKeys():
            # Do not create relation on self
            if setting == definition.key:
                continue

            other = self._getDefinition(setting)
            if not other:
                continue

            relation = SettingRelation.SettingRelation(definition, other, SettingRelation.RelationType.RequiresTarget, property)
            definition.relations.append(relation)

            relation = SettingRelation.SettingRelation(other, definition, SettingRelation.RelationType.RequiredByTarget, property)
            other.relations.append(relation)

    def _getDefinition(self, key):
        definition = None
        if key in self._definition_cache:
            definition = self._definition_cache[key]
        else:
            definitions = self.findDefinitions(key = key)
            if definitions:
                definition = definitions[0]
                self._definition_cache[key] = definition

        return definition
