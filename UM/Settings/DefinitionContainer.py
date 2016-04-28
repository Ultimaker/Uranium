# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import json
import collections
import copy

from UM.Resources import Resources
from UM.PluginObject import PluginObject

from . import ContainerInterface
from . import SettingDefinition

class InvalidDefinitionError(Exception):
    pass

class IncorrectDefinitionVersionError(Exception):
    pass

class InvalidOverrideError(Exception):
    pass

##  A container for SettingDefinition objects.
#
#
class DefinitionContainer(ContainerInterface.ContainerInterface, PluginObject):
    Version = 1

    ##  Constructor
    #
    #   \param container_id A unique, machine readable/writable ID for this container.
    def __init__(self, container_id, i18n_catalog = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = container_id
        self._name = container_id
        self._metadata = {}
        self._definitions = []
        self._i18n_catalog = i18n_catalog

    ##  Reimplement __setattr__ so we can make sure the definition remains unchanged after creation.
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        #raise NotImplementedError()

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
    #   Reimplemented from ContainerInterface
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
        parsed = json.loads(serialized, object_pairs_hook=collections.OrderedDict)

        self._verifyJson(parsed)

        # Pre-process the JSON data to include inherited data and overrides
        if "inherits" in parsed:
            inherited = self._resolveInheritance(parsed["inherits"])
            parsed = self._mergeDicts(inherited, parsed)

        if "overrides" in parsed:
            for key, value in parsed["overrides"].items():
                setting = self._findInDict(parsed["settings"], key)
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
            definition = SettingDefinition(key, self, None, self._i18n_catalog)
            definition.deserialize(value)
            self._definitions.append(definition)


    ##  Find definitions matching certain criteria.
    #
    #   \param criteria \type{dict} A dictionary containing key-value pairs which should match properties of the definition.
    def findDefinitions(self, criteria):
        definitions = []
        for definition in self._definitions:
            definitions.extend(definition.findDefinitions(criteria))

        return definitions

    # protected:

    # Load a file from disk, used to handle inheritance and includes
    def _loadFile(self, file_name):
        path = Resources.getPath(Resources.Definitions, file_name + ".json")
        contents = {}
        with open(path) as f:
            contents = json.load(f, object_pairs_hook=collections.OrderedDict)
        return contents

    # Recursively resolve loading inherited files
    def _resolveInheritance(self, file_name):
        result = {}

        json = self._loadFile(file_name)
        self._verifyJson(json)

        if "inherits" in json:
            inherited = self._resolveInheritance(json["inherits"])
            json = self._mergeDicts(inherited, json)
            print(json)

        return json

    # Verify that a loaded json matches our basic expectations.
    def _verifyJson(self, json):
        if not "version" in json:
            raise InvalidDefinitionError("Missing required property 'version'")

        if not "name" in json:
            raise InvalidDefinitionError("Missing required property 'name'")

        if json["version"] != self.Version:
            raise IncorrectDefinitionVersionError("Definition uses version {0} but expected version {1}".format(json["version"], self.Version))

    # Recursively find a key in a dicationary
    def _findInDict(self, dict, key):
        if key in dict:
            return dict

        result = None
        for dict_key, value in dict.items():
            self._findInDict(value, key)

        return result

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
