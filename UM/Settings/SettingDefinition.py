# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import json
import enum
import collections

from UM.Logger import Logger

from . import SettingFunction

class SettingType(enum.IntEnum):
    Unknown = 1
    Boolean = 2
    Integer = 3
    Float = 4
    Enum = 5
    String = 6
    List = 7
    Dictionary = 8
    Polygon = 9
    Other = 10

class SettingPropertyType(enum.IntEnum):
    Any = 1
    String = 2
    TranslatedString = 3
    Function = 4

##  Defines a single Setting with its properties.
#
#   This class defines a single Setting with all its properties. This class is considered invariant,
#   the only way to change it is using deserialize().
class SettingDefinition:
    ##  Construcutor
    #
    #   \param key \type{string} The unique, machine readable/writable key to use for this setting.
    #   \param container \type{DefinitionContainer} The container of this setting. Defaults to None.
    #   \param parent \type{SettingDefinition} The parent of this setting. Defaults to None.
    #   \param i18n_catalog \type{i18nCatalog} The translation catalog to use for this setting. Defaults to None.
    def __init__(self, key, container = None, parent = None, i18n_catalog = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._key = key
        self._container = container
        self._parent = parent

        self._i18n_catalog = i18n_catalog

        self._children = {}
        self._relations = {}

        self._type = SettingType.Unknown

        self.__property_values = {}

    ##  Override __getattr__ to provide access to definition properties.
    def __getattr__(self, name):
        if name in self.__property_definitions:
            return self.__property_values[name]

        raise AttributeError("'SettingDefinition' object has no attribute '{0}'".format(name))

    ##  Override __setattr__ to enforce invariant status of definition properties.
    def __setattr__(self, name, value):
        if name in self.__property_definitions:
            raise NotImplementedError("Setting of property {0} not supported".format(name))

        super().__setattr__(name, value)

    ##  The key of this setting.
    @property
    def key(self):
        return self._key

    ##  The container of this setting.
    @property
    def container(self):
        return self._container

    ##  The parent of this setting.
    @property
    def parent(self):
        return self._parent

    ##  The type of this setting.
    @property
    def type(self):
        return self._type

    ##  A list of children of this setting.
    @property
    def children(self):
        return self._children

    ##  A list of SettingRelation objects of this setting.
    @property
    def relations(self):
        return self._relations

    ##  Serialize this setting to a string.
    #
    #   \return \type{string} A serialized representation of this setting.
    def serialize(self):
        pass

    ##  Deserialize this setting from a string or dict.
    #
    #   \param serialized \type{string or dict} A serialized representation of this setting.
    def deserialize(self, serialized):
        if isinstance(serialized, dict):
            self._deserialize_dict(serialized)
        else:
            parsed = json.loads(serialized, object_pairs_hook=collections.OrderedDict)
            self._deserialize_dict(parsed)

    ##  Get a child by key
    #
    #   \param key \type{string} The key of the child to get.
    #
    #   \return \type{SettingDefinition} The child with the specified key or None if not found.
    def getChild(self, key):
        for child in self._children:
            if child.key == key:
                return child

        return None

    ##  Find all definitions matching certain criteria.
    #
    #   This will search this definition and its children for definitions matching the search criteria.
    #
    #   \param criteria \type{dict} A dictionary with key-value pairs that need to match properties of the children.
    #
    #   \return \type{list} A list of children matching the search criteria. The list will be empty if no children were found.
    def findDefinitions(self, criteria):
        definitions = []

        has_properties = True
        for key, value in criteria.items():
            try:
                if getattr(self, key) != value:
                    has_properties = False
            except AttributeError:
                continue

        if has_properties:
            definitions.append(self)

        for child in self._children:
            definitions.extend(child.findDefinitions(criteria))

        return definitions
    @classmethod
    def addPropertyDefinition(cls, name, type, required = False):
        cls.__property_definitions[name] = { "type": type, "required": required }

    ## protected:

    def _deserialize_dict(self, serialized):
        self._children = {}
        self._relations = {}
        self._type = SettingType.Unknown

        for key, value in serialized.items():
            if key == "children":
                for child_key, child_dict in value.items():
                    child = SettingDefinition(child_key, self._container, self, self._i18n_catalog)
                    child.deserialize(child_dict)
                    self._children[child_key] = child

            if key == "type":
                if value in self.__setting_type_map:
                    self._type = self.__setting_type_map[value]
                else:
                    Logger.log("w", "Unrecognised type %s for setting %s", value, self._key)
                    self._type = SettingType.Unknown
                continue

            if key not in self.__property_definitions:
                Logger.log("w", "Unrecognised property %s in setting %s", key, self._key)
                continue

            if self.__property_definitions[key]["type"] == SettingPropertyType.Any:
                self.__property_values[key] = value
            elif self.__property_definitions[key]["type"] == SettingPropertyType.String:
                self.__property_values[key] = str(value)
            elif self.__property_definitions[key]["type"] == SettingPropertyType.TranslatedString:
                self.__property_values[key] = self._i18n_catalog.i18n(value) if self._i18n_catalog is not None else value
            elif self.__property_definitions[key]["type"] == SettingPropertyType.Function:
                self.__property_values[key] = SettingFunction.SettingFunction(value)

        for key in filter(lambda i: self.__property_definitions[i]["required"], self.__property_definitions):
            if not key in self.__property_values:
                raise AttributeError("Setting {0} is missing required property {1}".format(self._key, key))

    __property_definitions = {
        "label": { "type": SettingPropertyType.TranslatedString, "required": True },
        "icon": { "type": SettingPropertyType.String, "required": False },
        "unit": { "type": SettingPropertyType.String, "required": False },
        "description": { "type": SettingPropertyType.TranslatedString, "required": True },
        "warning_description": { "type": SettingPropertyType.TranslatedString, "required": False },
        "error_description": { "type": SettingPropertyType.TranslatedString, "required": False },
        "default_value": { "type": SettingPropertyType.Any, "required": True },
        "value": { "type": SettingPropertyType.Function, "required": False },
        "enabled": { "type": SettingPropertyType.Function, "required": False },
        "minimum": { "type": SettingPropertyType.Function, "required": False },
        "maximum": { "type": SettingPropertyType.Function, "required": False },
        "minimum_warning": { "type": SettingPropertyType.Function, "required": False },
        "maximum_warning": { "type": SettingPropertyType.Function, "required": False },
        "options": { "type": SettingPropertyType.Any, "required": False },
    }

    __setting_type_map = {
        "bool": SettingType.Boolean,
        "int": SettingType.Integer,
        "float": SettingType.Float,
        "enum": SettingType.Enum,
        "string": SettingType.String,
        "list": SettingType.List,
        "dict": SettingType.Dictionary,
        "polygon": SettingType.Polygon,
        "other": SettingType.Other,
    }
