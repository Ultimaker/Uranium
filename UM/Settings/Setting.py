# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Settings.Validators.IntValidator import IntValidator
from UM.Settings.Validators.FloatValidator import FloatValidator
from UM.Settings.Validators.ResultCodes import ResultCodes
from PyQt5.QtCore import QCoreApplication
from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger

import math
import ast
import collections
from copy import deepcopy

##  Raised when an inheritance function tries to use a blacklisted method.
class IllegalMethodError(Exception):
    pass

##  A setting object contains the definition of a (single) configuration setting.
#
#   The Setting object provides the definition of a setting, like the user-visible label,
#   description and other properties. It does not contain any values, for that you should
#   use the Profile class.
#
#   \note Currently there is still too much state embedded in a setting. All value functions
#         and things like visibility should really be separated into a different class.
#
class Setting(SignalEmitter):
    def __init__(self, machine_manager, key, catalog, **kwargs):
        super().__init__()
        self._machine_manager = machine_manager
        self._machine_manager.activeProfileChanged.connect(self._onActiveProfileChanged)

        self._key = key
        self._i18n_catalog = catalog

        self._label = kwargs.get("label", key)
        self._type = kwargs.get("type", "string")
        self._category = kwargs.get("category", None)
        self._profile = kwargs.get("profile", None)

        self._description = ""
        self._warning_description = ""
        self._error_description = ""
        self._global_only = False
        self._default_value = None
        self._visible = True
        self._validator = None
        self._parent = None
        self._hide_if_all_children_visible = True
        self._children = []
        self._enabled_function = None
        self._options = collections.OrderedDict()
        self._unit = ""
        self._inherit = True
        self._inherit_function = None
        self._prohibited = False

        # Keys of the settings that this setting requires to set certain values (As defined by inherit & enabled function)
        self._required_setting_keys = set()

        # Keys of the settings that require this setting to set certain vailes (As defined by inherit & enabled function)
        self._required_by_setting_keys = set()

    def addRequiredBySettingKey(self, key):
        self._required_by_setting_keys.add(key)

    def getRequiredBySettingKeys(self):
        return self._required_by_setting_keys

    def getRequiredSettingKeys(self):
        return self._required_setting_keys

    ##  Bind new validator to object based on it's current type
    def bindValidator(self):
        if self._type == "float":
            FloatValidator(self) # Validator sets itself as validator to this setting
        elif self._type == "int":
            IntValidator(self)

    ##  Get the depth of this setting (how many steps is it 'away' from its category)
    def getDepth(self):
        return self._parent.getDepth() + 1

    ##  Set values of the setting by providing it with a dict object (as decoded by JSON parser)
    #   \param data Decoded JSON dict
    def fillByDict(self, data):
        if "type" in data:
            self._type = data["type"]
            if self._type not in ["int", "float", "string", "enum", "boolean", "polygon", "polygons"]:
                Logger.log("e", "Invalid type %s for Setting %s, ignoring", self._type, self._key)
                return

        if "default" in data:
            self._default_value = data["default"]

        if not self._validator:
            self.bindValidator()

        if "label" in data:
            self._label = self._i18n_catalog.i18nc("{0} label".format(self._key), data["label"])

        if "description" in data:
            self._description = self._i18n_catalog.i18nc("{0} description".format(self._key), data["description"])

        if "warning_description" in data:
            self._warning_description = self._i18n_catalog.i18nc("{0} warning description".format(self._key), data["warning_description"])

        if "error_description" in data:
            self._error_description = self._i18n_catalog.i18nc("{0} error description".format(self._key), data["error_description"])

        if "unit" in data:
            self._unit = self._i18n_catalog.i18nc("{0} unit".format(self._key), data["unit"])

        if "visible" in data:
            self.setVisible(data["visible"])

        if "global_only" in data:
            #if the data contains global_only; it can contain a boolean value or a function that returns a boolean value
            if isinstance(data["global_only"], bool):
                self._global_only = data["global_only"]
            else:
                 self._global_only = self._createFunction(data["global_only"])

        if "always_visible" in data:
            self._hide_if_all_children_visible = not data["always_visible"]

        self._inherit = data.get("inherit", True)

        if "inherit_function" in data:
            self._inherit_function = self._createFunction(data["inherit_function"])

        if not self._inherit_function and self._inherit and self._parent and isinstance(self._parent, Setting):
            self._inherit_function = self._createFunction("parent_value")

        min_value = None
        max_value = None
        min_value_warning = None
        max_value_warning = None

        if "min_value" in data:
            min_value = self._createFunction(data["min_value"])
        if "max_value" in data:
            max_value = self._createFunction(data["max_value"])
        if "min_value_warning" in data:
            min_value_warning = self._createFunction(data["min_value_warning"])
        if "max_value_warning" in data:
            max_value_warning = self._createFunction(data["max_value_warning"])

        if  self.getValidator() is not None: #Strings don"t have validators as of yet
            if min_value:
                self.getValidator().setMinValue(min_value)
            if max_value:
                self.getValidator().setMaxValue(max_value)
            if max_value_warning:
                self.getValidator().setMaxValueWarning(max_value_warning)
            if min_value_warning:
                self.getValidator().setMinValueWarning(min_value_warning)
        if "enabled" in data:
            self._enabled_function = self._createFunction(data["enabled"])
            self._prohibited = data["enabled"] == "False" # Enabled can never be true, so this setting is prohibited.

        if "options" in data:
            self._options = {}
            for key, value in data["options"].items():
                self._options[key] = self._i18n_catalog.i18nc("{0} option {1}".format(self._key, key), value)

        if "children" in data:
            for key, value in data["children"].items():
                setting = self.getSetting(key)
                if not setting:
                    setting = Setting(self._machine_manager, key, self._i18n_catalog)
                    setting.setCategory(self._category)
                    setting.setParent(self)
                    setting.defaultValueChanged.connect(self.defaultValueChanged)
                    # Pass visibility to parent, as the category needs to be notified when it changes.
                    setting.visibleChanged.connect(self.visibleChanged)
                    self._children.append(setting)

                setting.fillByDict(value)

    ##  Return a dict with the values this setting can have.
    #
    #   The dict contains a value as key and a user-visible label that can be used to display the value to the user.
    def getOptions(self):
        return self._options

    ##  Set the validator of the Setting
    #   \param validator Validator
    def setValidator(self, validator):
        self._validator = validator

    ##  Get the validator
    #   \returns Validator
    def getValidator(self):
        return self._validator

    ##  Get the category of this setting.
    #   \returns SettingCategory
    def getCategory(self):
        return self._category

    ##  Set the category
    #   \params category SettingCategory
    def setCategory(self, category):
        self._category = category
        self._machine_settings = category.getParent() if category else None
        for child in self._children:
            child.setCategory(category)

    ##  Set the parent of this setting.
    #
    #   Parents can be used to determine the value of the setting if the setting is not visible.
    #   mostly used for giving a 'global' setting (such as speed), with children being travel speed, infill speed, etc.
    #   \param setting Setting
    def setParent(self, setting):
        self._parent = setting

        if not self._inherit_function and self._inherit and self._parent and isinstance(self._parent, Setting):
            self._inherit_function = self._createFunction("parent_value")

    ##  Get the parent.
    #   \returns Setting
    def getParent(self):
        return self._parent

    ##  Add a child to this setting. See setParent for more info.
    #   \param setting Setting
    def addChild(self, setting):
        setting.setParent(self)
        self._children.append(setting)

    ##  Retrieve a setting or child setting by key.
    #
    #   \param key The key to search for.
    #   \returns Setting if key match is found, None otherwise.
    def getSetting(self, key):
        if self._key == key:
            return self
        for s in self._children:
            ret = s.getSetting(key)
            if ret is not None:
                return ret
        return None

    ##  Set the default value of the setting.
    #
    #   Note that the default value may be overridden when the setting is not visible.
    #   \param value
    def setDefaultValue(self, value):
        self._default_value = value
        return self

    ##  get the default value of the setting.
    #   \param values The object to use to get setting values from. Used by the inherit function, if set.
    #   \returns default_value
    def getDefaultValue(self, values = None):
        if self._inherit and self._inherit_function:
            try:
                inherit_value = self._inherit_function(values)
            except Exception as e:
                Logger.log("e", "An error occurred in inherit function for {0}: {1}".format(self._key, str(e)))
            else:
                if inherit_value is not None:
                    return inherit_value

        return self._default_value

    defaultValueChanged = Signal()

    ##  Set the visibility of this setting.
    #   \param visible Bool
    def setVisible(self, visible):
        if visible != self._visible:
            self._visible = visible
            self.visibleChanged.emit(self)

    ##  Check if the setting is visible.
    #
    #   It can be that the setting visible is true,
    #   but it still should be invisible as all it's children are visible (at this point this setting is overridden by its children
    #   changing it does nothing, so it needs to be hidden!)
    #   \returns bool
    #   \sa isEnabled
    def isVisible(self):
        return self._visible

    ##  Emitted when visible is changed either due to explicitly setting it or due to children visibility changing.
    visibleChanged = Signal()

    ##  Check if all children are visible.
    #   \returns bool True if all children are visible. False otherwise
    def checkAllChildrenVisible(self):
        if len(self._children) < 1:
            return False
        for child in self._children:
            if not child.isVisible() and not child.checkAllChildrenVisible():
                return False
        return True

    ##  Get the display name of the setting
    def getLabel(self):
        if self._label is None:
            return self._key # Return key so it will always have some sort of display name

        return self._label

    ##  Set the label (display name) of setting.
    #   \param label 
    def setLabel(self, label):
        self._label = label

    ##  Get the description of this setting.
    #
    #   This will return a string with a description of this setting, if provided by the setting file.
    def getDescription(self):
        return self._description

    ##  Get the warning description of the setting.
    #
    #   This provides a descriptive text about why the setting is in a warning state.
    def getWarningDescription(self):
        return self._warning_description

    ##  Get the error description of the setting.
    #
    #   This provides a descriptive text about why the setting is in an error state.
    def getErrorDescription(self):
        return self._error_description

    ##  Emitted whenever this setting's global-only state changes.
    globalOnlyChanged = Signal()

    ##  Get whether the setting is global only or not.
    #
    #   Global only means that this setting cannot be used as a per object setting.
    def getGlobalOnly(self):
        if not isinstance(self._global_only, bool):
            return self._global_only()
        return self._global_only

    ##  Get the identifier of the setting
    def getKey(self):
        return self._key

    ## Get the type of the setting
    # \returns type
    def getType(self):
        return self._type

    ##  Get the unit of the setting.
    #
    #   This is primarily a user-visible string that can be displayed to provide information about the unit.
    def getUnit(self):
        return self._unit

    ##  Emitted whenever this setting's enabled state changes.
    enabledChanged = Signal()

    ##  Check whether this setting is enabled.
    #
    #   Enabled settings can be displayed and used. Disabled settings should be ignored.
    def isEnabled(self):
        if self._enabled_function:
            return self._enabled_function() == True #Force check. 

        return True

    ##  Check whether this setting is prohibited.
    #   This value is true if in all cases of the enabled function the result is false.
    def isProhibited(self):
        return self._prohibited

    ##  Validate a value using this Setting
    #   \param value The value to validate
    #   \returns ResultCodes.succes if there is no validator or if validation is succesfull. Returns warning or error code otherwise.
    def validate(self, value):
        if self._validator is not None:
            return self._validator.validate(value)
        else:
            return ResultCodes.succes

    ##  Get a list of all children of this setting, including children of children.
    def getAllChildren(self):
        all_children = []
        for s in self._children:
            all_children.append(s)
            all_children.extend(s.getAllChildren())
        return all_children

    ##  Get a list of the direct children of this setting (so no children of children).
    def getChildren(self):
        return self._children

    ##  Parse a value so it is a proper value for this setting.
    #
    #   \param value The value to parse.
    #
    #   \return A value that is valid for this setting.
    def parseValue(self, value):
        if self._type == "string" or self._type == "enum":
            return str(value)

        if isinstance(value, str):
            try:
                value = ast.literal_eval(value.replace(",", "."))
            except Exception:
                value = None

        if self._type == "boolean":
            return bool(value) if value else False
        elif self._type == "int":
            return int(value) if value else 0
        elif self._type == "float":
            return float(value) if value else 0.0
        else:
            return value

    def __repr__(self):
        return "<Setting: %s>" % (self._key)

    def __deepcopy__(self, memo):
        copy = Setting(
            machine_manager = self._machine_manager,
            key = self._key,
            catalog = self._i18n_catalog,
            label = self._label,
            type = self._type
        )

        copy._description = self._description
        copy._default_value = self._default_value
        copy._visible = self._visible
        copy._category = self._category
        copy._unit = self._unit
        copy._validator = deepcopy(self._validator, memo)
        copy._parent = self._parent
        copy._hide_if_all_children_visible = self._hide_if_all_children_visible
        copy._children = deepcopy(self._children, memo)
        copy._options = deepcopy(self._options, memo)
        copy._inherit = self._inherit
        copy._inherit_function = deepcopy(self._inherit_function, memo)

        copy._warning_description = self._warning_description
        copy._error_description = self._error_description
        copy._global_only = deepcopy(self._global_only, memo)
        copy._enabled_function = deepcopy(self._enabled_function, memo)

        copy._fixChildren()

        return copy

    ## private:

    # Fixes parent assignment after a deepcopy operation
    def _fixChildren(self):
        for child in self._children:
            child.setParent(self)
            child._fixChildren()

    def _createFunction(self, code):
        try:
            tree = ast.parse(code, "eval")
            names = _SettingExpressionVisitor().visit(tree)
            compiled = compile(code, self._key, "eval")
        except (SyntaxError, TypeError) as e:
            Logger.log("e", "Parse error in function ({2}) for setting {0}: {1}".format(self._key, str(e), code))
        except IllegalMethodError as e:
            Logger.log("e", "Use of illegal method {0} in function ({2}) for setting {1}".format(str(e), self._key, code))
        except Exception as e:
            Logger.log("e", "Exception in function ({2}) for setting {0}: {1}".format(self._key, str(e), code))

        def local_function(profile = None):
            if not profile:
                profile = self._machine_manager.getWorkingProfile()

            if not profile:
                return None

            locals = {
                "profile": profile
            }

            if self.getParent() and isinstance(self.getParent(), Setting):
                locals["parent_value"] = profile.getSettingValue(self.getParent().getKey())
                self._required_setting_keys.add(self.getParent().getKey())
                self.getParent().addRequiredBySettingKey(self._key)

            for name in names:
                locals[name] = profile.getSettingValue(name)
                self._required_setting_keys.add(name)
            return eval(compiled, globals(), locals)

        return local_function

    def _onSettingValueChanged(self, key):
        if key in self._required_setting_keys:
            self.enabledChanged.emit(self)
            self.defaultValueChanged.emit(self)
            self.globalOnlyChanged.emit(self)

    def _onActiveProfileChanged(self):
        if self._profile:
            self._profile.settingValueChanged.disconnect(self._onSettingValueChanged)

        self._profile = self._machine_manager.getWorkingProfile()
        if self._profile:
            self._profile.settingValueChanged.connect(self._onSettingValueChanged)

# Private AST visitor class used to look up names in the inheritance functions.
class _SettingExpressionVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.names = []

    def visit(self, node):
        super().visit(node)
        return self.names

    def visit_Name(self, node): # [CodeStyle: ast.NodeVisitor requires this function name]
        if node.id in self._blacklist:
            raise IllegalMethodError(node.id)

        if node.id not in self._knownNames and node.id not in __builtins__:
            self.names.append(node.id)

    _knownNames = [
        "parent_value",
        "math"
    ]

    _blacklist = [
        "sys",
        "os",
        "import",
        "__import__"
    ]
