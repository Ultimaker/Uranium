# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import ast
import json
import enum
import collections
import re

from UM.Logger import Logger

from . import SettingFunction
from . import Validator


##  Type of definition property.
#
#   This enum describes the possible types for a supported definition property.
#   For more information about supported definition properties see SettingDefinition
#   and SettingDefinition::addSupportedProperty().
class DefinitionPropertyType(enum.IntEnum):
    Any = 1  ## Any value.
    String = 2  ## Value is always converted to string.
    TranslatedString = 3  ## Value is converted to string then passed through an i18nCatalog object to get a translated version of that string.
    Function = 4  ## Value is a python function. It is passed to SettingFunction's constructor which will parse and analyze it.


##  Defines a single Setting with its properties.
#
#   This class defines a single Setting with all its properties. This class is considered immutable,
#   the only way to change it is using deserialize(). Should any state need to be stored for a definition,
#   create a SettingInstance pointing to the definition, then store the value in that instance.
#
#   == Supported Properties
#
#   The SettingDefinition class contains a concept of "supported properties". These are properties that
#   are supported when serializing or deserializing a setting. These properties are defined through the
#   addSupportedProperty() method. Each property needs a name and a type. In addition, there are two
#   optional boolean value to indicate whether the property is "required" and whether it is "read only".
#   Currently, four types of supported properties are defined. Please DefinitionPropertyType for a description
#   of these types.
#
#   Required properties are properties that should be present when deserializing a setting. If the property
#   is not present, an error will be raised. Read-only properties are properties that should never change
#   after creating a SettingDefinition. This means they cannot be stored in a SettingInstance object.
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

        self._children = []
        self._relations = []

        self.__ancestors = set() # Cached set of keys of ancestors. Used for fast lookups of ancestors.
        self.__descendants = {} # Cached set of key - definition pairs of descendants. Used for fast lookup of descendants by key.

        self.__property_values = {}

    ##  Override __getattr__ to provide access to definition properties.
    def __getattr__(self, name):
        if name in self.__property_definitions:
            if name in self.__property_values:
                return self.__property_values[name]
            else:
                return self.__property_definitions[name]["default"]

        raise AttributeError("'SettingDefinition' object has no attribute '{0}'".format(name))

    ##  Override __setattr__ to enforce invariant status of definition properties.
    def __setattr__(self, name, value):
        if name in self.__property_definitions:
            raise NotImplementedError("Setting of property {0} not supported".format(name))

        super().__setattr__(name, value)

    ##  The key of this setting.
    #
    #   \return \type{string}
    @property
    def key(self):
        return self._key

    ##  The container of this setting.
    #
    #   \return \type{DefinitionContainer}
    @property
    def container(self):
        return self._container

    ##  The parent of this setting.
    #
    #   \return \type{SettingDefinition}
    @property
    def parent(self):
        return self._parent

    ##  A list of children of this setting.
    #
    #   \return \type{list<SettingDefinition>}
    @property
    def children(self):
        return self._children

    ##  A list of SettingRelation objects of this setting.
    #
    #   \return \type{list<SettingRelation>}
    @property
    def relations(self):
        return self._relations

    ##  Serialize this setting to a string.
    #
    #   \return \type{string} A serialized representation of this setting.
    def serialize(self):
        pass

    ##  Gets the key of this setting definition and of all its descendants.
    #
    #   \return A set of the key in this definition and all its descendants.
    def getAllKeys(self):
        keys = set()
        keys.add(self.key)
        for child in self.children:
            keys |= child.getAllKeys() #Recursively get all keys of all descendants.
        return keys

    ##  Serialize this setting to a dict.
    #
    #   \return \type{dict} A representation of this setting definition.
    def serialize_to_dict(self):
        result = {}
        result["label"] = self.key

        result["children"] = {}
        for child in self.children:
            result["children"][child.key] = child.serialize_to_dict()

        for key, value in self.__property_values.items():
            result[key] = str(value)

        return result

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
        if not self.__descendants:
            self.__descendants = self._updateDescendants()

        if key in self.__descendants:
            child = self.__descendants[key]
            if child not in self._children:
                # Descendants includes children-of-children etc. so we need to make sure we only return direct children.
                return None

            return child

        return None

    ## Check if this setting definition matches the provided criteria.
    #   \param kwargs \type{dict} A dictionary of keyword arguments that need to match its attributes.
    def matchesFilter(self, **kwargs):

        # First check for translated labels.
        keywords = kwargs.copy()
        if "i18n_label" in keywords:
            try:
                property_value = getattr(self, "label")
            except AttributeError:
                # If we do not have the attribute, we do not match
                return False

            if "i18n_catalog" in keywords:
                catalog = keywords["i18n_catalog"]
                if catalog:
                    property_value = catalog.i18nc(self._key + " label", property_value)

            value = keywords["i18n_label"]
            del keywords["i18n_label"]
            if not isinstance(value, str):
                return False
            if value != property_value:
                if "*" not in value:
                    return False

                value = value.strip("* ").lower()
                if value not in property_value.lower():
                    return False

        if "i18n_catalog" in keywords:
            del keywords["i18n_catalog"]

        # Normal attribute matching
        for key in keywords:
            try:
                property_value = getattr(self, key)
            except AttributeError:
                # If we do not have the attribute, we do not match
                return False

            value = kwargs[key]
            if property_value == value:
                # If the value matches with the expected value, we match for this property and should
                # continue with the other properties.
                # We do this check first so we can avoid the costly wildcard matching for situations where
                # we do not need to perform wildcard matching anyway.
                continue

            if isinstance(value, str):
                if not isinstance(property_value, str):
                    # If value is a string but the actual property value is not there is no situation where we
                    # will match.
                    return False

                if "*" not in value:
                    # If both are strings but there is no wildcard we do not match since we already checked if
                    # both are equal.
                    return False

                value = value.strip("* ").lower()
                if value not in property_value.lower():
                    return False
            else:
                return False

        return True

    ##  Find all definitions matching certain criteria.
    #
    #   This will search this definition and its children for definitions matching the search criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments that need to match properties of the children.
    #
    #   \return \type{list} A list of children matching the search criteria. The list will be empty if no children were found.
    def findDefinitions(self, **kwargs):
        definitions = []

        if not self.__descendants:
            self.__descendants = self._updateDescendants()

        key = kwargs.get("key")
        if key and not "*" in key:
            # Optimization for the most common situation: finding a setting by key
            if self._key != key and key not in self.__descendants:
                # If the mentioned key is not ourself and not in children, we will never match.
                return []

            if len(kwargs) == 1:
                # If all we are searching for is a key, return either ourself or a value from the descendants.
                if self._key == key:
                    return [self]

                return [self.__descendants[key]]

        if self.matchesFilter(**kwargs):
            definitions.append(self)

        for child in self._children:
            definitions.extend(child.findDefinitions(**kwargs))

        return definitions

    ##  Check whether a certain setting is an ancestor of this definition.
    #
    #   \param key \type{str} The key of the setting to check.
    #
    #   \return True if the specified setting is an ancestor of this definition, False if not.
    def isAncestor(self, key):
        if not self.__ancestors:
            self.__ancestors = self._updateAncestors()

        return key in self.__ancestors

    ##  Check whether a certain setting is a descendant of this definition.
    #
    #   \param key \type{str} The key of the setting to check.
    #
    #   \return True if the specified setting is a descendant of this definition, False if not.
    def isDescendant(self, key):
        if not self.__descendants:
            self.__descendants = self._updateDescendants()

        return key in self.__descendants

    ##  Get a set of keys representing the setting's ancestors.
    def getAncestors(self):
        if not self.__ancestors:
            self.__ancestors = self._updateAncestors()

        return self.__ancestors

    def __repr__(self):
        return "<SettingDefinition (0x{0:x}) key={1} container={2}>".format(id(self), self._key, self._container)

    def __eq__(self, other):
        if other is None:
            return False

        try:
            if isinstance(other, SettingDefinition):
                return self._key == other.key
            else:
                Logger.log("w", "Trying to compare equality of SettingDefinition and something that is no SettingDefinition.")
        except:  # Has no key. Not the same type of object.
            Logger.log("w", "Trying to compare equality of SettingDefinition and something that is no SettingDefinition.")
            return False

    ##  Define a new supported property for SettingDefinitions.
    #
    #   Since applications may want custom properties in their definitions, most properties are handled
    #   dynamically. This allows the application to define what extra properties it wants to support.
    #   Additionally, it can indicate whether a properties should be considered "required". When a
    #   required property is not missing during deserialization, an AttributeError will be raised.
    #
    #   \param name \type{string} The name of the property to define.
    #   \param property_type \type{DefinitionPropertyType} The type of property.
    #   \param kwargs Keyword arguments. Possible values:
    #                 required  \type{bool} True if missing the property indicates an error should be raised. Defaults to False.
    #                 read_only \type{bool} True if the property should never be set on a SettingInstance. Defaults to False. Note that for Function properties this indicates whether the result of the function should be stored.
    #                 default               The default value for this property. This will be returned when the specified property is not defined for this definition.
    #                 depends_on            Key to another property that this property depends on; eg; if that value changes, this value should be re-evaluated.
    @classmethod
    def addSupportedProperty(cls, name, property_type, **kwargs):
        cls.__property_definitions[name] = {"type": property_type, "required": kwargs.get("required", False), "read_only": kwargs.get("read_only", False), "default": kwargs.get("default", None), "depends_on": kwargs.get("depends_on", None)}

    ##  Get the names of all supported properties.
    #
    #   \param type \type{DefinitionPropertyType} The type of property to get the name of. Defaults to None which means all properties.
    #
    #   \return A list of all the names of supported properties.
    @classmethod
    def getPropertyNames(cls, type = None):
        result = []
        for key, value in cls.__property_definitions.items():
            if not type or value["type"] == type:
                result.append(key)
        return result

    ##  Check if a property with the specified name is defined as a supported property.
    #
    #   \param name \type{string} The name of the property to check if it is supported.
    #
    #   \return True if the property is supported, False if not.
    @classmethod
    def hasProperty(cls, name):
        return name in cls.__property_definitions

    ##  Get the type of a specified property.
    #
    #   \param name \type{str} The name of the property to find the type of.
    #
    #   \return DefinitionPropertyType corresponding to the type of the property or None if not found.
    @classmethod
    def getPropertyType(cls, name):
        if name in cls.__property_definitions:
            return cls.__property_definitions[name]["type"]

        return None

    ##  Check if the specified property is considered a required property.
    #
    #   Required properties are checked when deserializing a SettingDefinition and if not present an error
    #   will be reported.
    #
    #   \param name \type{string} The name of the property to check if it is required or not.
    #
    #   \return True if the property is supported and is required, False if it is not required or is not part of the list of supported properties.
    @classmethod
    def isRequiredProperty(cls, name):
        if name in cls.__property_definitions:
            return cls.__property_definitions[name]["required"]
        return False

    ##  Check if the specified property is considered a read-only property.
    #
    #   Read-only properties are properties that cannot have their value set in SettingInstance objects.
    #
    #   \param name \type{string} The name of the property to check if it is read-only or not.
    #
    #   \return True if the property is supported and is read-only, False if it is not required or is not part of the list of supported properties.
    @classmethod
    def isReadOnlyProperty(cls, name):
        if name in cls.__property_definitions:
            return cls.__property_definitions[name]["read_only"]
        return False

    ##  Check if the specified property depends on another property
    #
    #   The value of certain properties can change if the value of another property changes. This is used to signify that relation.
    #
    #   \param name \type{string} The name of the property to check if it depends on another setting.
    #
    #   \return \type{string} The property it depends on or None if it does not depend on another property.
    @classmethod
    def dependsOnProperty(cls, name):
        if name in cls.__property_definitions:
            return cls.__property_definitions[name]["depends_on"]
        return None

    ##  Add a new setting type to the list of accepted setting types.
    #
    #   \param type_name The name of the new setting type.
    #   \param from_string A function to call that converts to a proper value of this type from a string.
    #   \param to_string A function that converts a value of this type to a string.
    #
    @classmethod
    def addSettingType(cls, type_name, from_string, to_string, validator = None):
        cls.__type_definitions[type_name] = { "from": from_string, "to": to_string, "validator": validator }

    ##  Convert a string to a value according to a setting type.
    #
    #   \param type_name \type{string} The name of the type to convert to.
    #   \param string_value \type{string} The string to convert.
    #
    #   \return The string converted to a proper value.
    #
    #   \exception ValueError Raised when the specified type does not exist.
    @classmethod
    def settingValueFromString(cls, type_name, string_value):
        if type_name not in cls.__type_definitions:
            raise ValueError("Unknown setting type {0}".format(type_name))

        convert_function = cls.__type_definitions[type_name]["to"]
        if convert_function:
            return convert_function(string_value)

        return string_value

    ##  Convert a setting value to a string according to a setting type.
    #
    #   \param type_name \type{string} The name of the type to convert from.
    #   \param value The value to convert.
    #
    #   \return \type{string} The specified value converted to a string.
    #
    #   \exception ValueError Raised when the specified type does not exist.
    @classmethod
    def settingValueToString(cls, type_name, value):
        if type_name not in cls.__type_definitions:
            raise ValueError("Unknown setting type {0}".format(type_name))

        convert_function = cls.__type_definitions[type_name]["from"]
        if convert_function:
            return convert_function(value)

        return value

    ##  Get the validator type for a certain setting type.
    @classmethod
    def getValidatorForType(cls, type_name):
        if type_name not in cls.__type_definitions:
            raise ValueError("Unknown setting type {0}".format(type_name))

        return cls.__type_definitions[type_name]["validator"]

    ## protected:

    # Deserialize from a dictionary
    def _deserialize_dict(self, serialized):
        self._children = []
        self._relations = []

        for key, value in serialized.items():
            if key == "children":
                for child_key, child_dict in value.items():
                    child = SettingDefinition(child_key, self._container, self, self._i18n_catalog)
                    child.deserialize(child_dict)
                    self._children.append(child)
                continue

            if key not in self.__property_definitions:
                Logger.log("w", "Unrecognised property %s in setting %s", key, self._key)
                continue

            if key == "type":
                if value not in self.__type_definitions:
                    raise ValueError("Type {0} is not a correct setting type".format(value))

            if self.__property_definitions[key]["type"] == DefinitionPropertyType.Any:
                self.__property_values[key] = value
            elif self.__property_definitions[key]["type"] == DefinitionPropertyType.String:
                self.__property_values[key] = str(value)
            elif self.__property_definitions[key]["type"] == DefinitionPropertyType.TranslatedString:
                self.__property_values[key] = self._i18n_catalog.i18n(str(value)) if self._i18n_catalog is not None else value
            elif self.__property_definitions[key]["type"] == DefinitionPropertyType.Function:
                self.__property_values[key] = SettingFunction.SettingFunction(str(value))
            else:
                Logger.log("w", "Unknown DefinitionPropertyType (%s) for key %s", key, self.__property_definitions[key]["type"])

        for key in filter(lambda i: self.__property_definitions[i]["required"], self.__property_definitions):
            if key not in self.__property_values:
                raise AttributeError("Setting {0} is missing required property {1}".format(self._key, key))

        self.__ancestors = self._updateAncestors()
        self.__descendants = self._updateDescendants()

    def _updateAncestors(self):
        result = set()

        parent = self._parent
        while parent:
            result.add(parent.key)
            parent = parent.parent

        return result

    def _updateDescendants(self, definition = None):
        result = {}

        if not definition:
            definition = self

        for child in definition.children:
            result[child.key] = child
            result.update(self._updateDescendants(child))

        return result

    __property_definitions = {
        # The name of the setting. Only used for display purposes.
        "label": {"type": DefinitionPropertyType.TranslatedString, "required": True, "read_only": True, "default": "", "depends_on" : None},
        # The type of setting. Can be any one of the types defined.
        "type": {"type": DefinitionPropertyType.String, "required": True, "read_only": True, "default": "", "depends_on" : None},
        # An optional icon that can be displayed for the setting.
        "icon": {"type": DefinitionPropertyType.String, "required": False, "read_only": True, "default": "", "depends_on" : None},
        # A string describing the unit used for the setting. This is only used for display purposes at the moment.
        "unit": {"type": DefinitionPropertyType.String, "required": False, "read_only": True, "default": "", "depends_on" : None},
        # A description of what the setting does. Used for display purposes.
        "description": {"type": DefinitionPropertyType.TranslatedString, "required": True, "read_only": True, "default": "", "depends_on" : None},
        # A description of what is wrong when the setting has a warning validation state. Used for display purposes.
        "warning_description": {"type": DefinitionPropertyType.TranslatedString, "required": False, "read_only": True, "default": "", "depends_on" : None},
        # A description of what is wrong when the setting has an error validation state. Used for display purposes.
        "error_description": {"type": DefinitionPropertyType.TranslatedString, "required": False, "read_only": True, "default": "", "depends_on" : None},
        # The default value of the setting. Used when no value function is defined.
        "default_value": {"type": DefinitionPropertyType.Any, "required": False, "read_only": True,  "default": 0, "depends_on" : None},
        # A function used to calculate the value of the setting.
        "value": {"type": DefinitionPropertyType.Function, "required": False, "read_only": False,  "default": None, "depends_on" : None},
        # A function that should evaluate to a boolean to indicate whether or not the setting is enabled.
        "enabled": {"type": DefinitionPropertyType.Function, "required": False, "read_only": False, "default": True, "depends_on": None},
        # A function that calculates the minimum value for this setting. If the value is less than this, validation will indicate an error.
        "minimum_value": {"type": DefinitionPropertyType.Function, "required": False, "read_only": False, "default": None, "depends_on" : None},
        # A function that calculates the maximum value for this setting. If the value is more than this, validation will indicate an error.
        "maximum_value": {"type": DefinitionPropertyType.Function, "required": False, "read_only": False, "default": None, "depends_on" : None},
        # A function that calculates the minimum warning value for this setting. If the value is less than this, validation will indicate a warning.
        "minimum_value_warning": {"type": DefinitionPropertyType.Function, "required": False, "read_only": False, "default": None, "depends_on" : None},
        # A function that calculates the maximum warning value for this setting. If the value is more than this, validation will indicate a warning.
        "maximum_value_warning": {"type": DefinitionPropertyType.Function, "required": False, "read_only": False, "default": None, "depends_on" : None},
        # A dictionary of key-value pairs that provide the options for an enum type setting. The key is the actual value, the value is a translated display string.
        "options": {"type": DefinitionPropertyType.Any, "required": False, "read_only": True, "default": {}, "depends_on" : None},
        # Optional comments that apply to the setting. Will be ignored.
        "comments": {"type": DefinitionPropertyType.String, "required": False, "read_only": True, "default": "", "depends_on" : None}
    }

    ##  Conversion from string to integer.
    #
    #   \param value The string representation of an integer.
    def _toIntConversion(value):
        try:
            return ast.literal_eval(value)
        except SyntaxError:
            return 0

    ## Conversion of string to float.
    def _toFloatConversion(value):
        ## Ensure that all , are replaced with . (so they are seen as floats)
        value = value.replace(",", ".")

        def stripLeading0(matchobj):
            return matchobj.group(0).lstrip("0")

        ## Literal eval does not like "02" as a value, but users see this as "2".
        ## We therefore look numbers with leading "0", provided they are not used in variable names
        ## example: "test02 * 20" should not be changed, but "test * 02 * 20" should be changed (into "test * 2 * 20")
        regex_pattern = '(?<!\.|\w|\d)0+(\d+)'
        value = re.sub(regex_pattern, stripLeading0 ,value)

        try:
            return ast.literal_eval(value)
        except:
            return 0

    __type_definitions = {
        # An integer value
        "int": {"from": lambda v: str(v) if v is not None else "", "to": _toIntConversion, "validator": Validator.Validator},
        # A boolean value
        "bool": {"from": str, "to": ast.literal_eval, "validator": None},
        # Special case setting; Doesn't have a value. Display purposes only.
        "category": {"from": None, "to": None, "validator": None},
        # A string value
        "str": {"from": None, "to": None, "validator": None},
        # An enumeration
        "enum": {"from": None, "to": None, "validator": None},
        # A floating point value
        "float": {"from": lambda v: str(round(v, 4)) if v is not None else "", "to": _toFloatConversion, "validator": Validator.Validator},
        # A list of 2D points
        "polygon": {"from": str, "to": ast.literal_eval, "validator": None},
        # A list of polygons
        "polygons": {"from": str, "to": ast.literal_eval, "validator": None},
        # A 3D point
        "vec3": {"from": None, "to": None, "validator": None},
    }


