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
from copy import deepcopy

##  Raised when an inheritance function tries to use a blacklisted method.
class IllegalMethodError(Exception):
    pass

##    A setting object contains a (single) configuration setting.
#     Settings have validators that check if the value is valid, but do not prevent invalid values!
#     Settings have conditions that enable/disable this setting depending on other settings. (Ex: Dual-extrusion)
class Setting(SignalEmitter):    
    def __init__(self, key, catalog, **kwargs):
        super().__init__()
        self._key = key
        self._i18n_catalog = catalog
        self._label = kwargs.get("label", key)
        self._description = kwargs.get("description", "")
        self._default_value = kwargs.get("default", None)
        self._value = kwargs.get("value", None)
        self._type = kwargs.get("type", "string")
        self._visible = kwargs.get("visible", True)
        self._validator = None
        self._parent = None
        self._hide_if_all_children_visible = True
        self._children = []
        self._category = kwargs.get("category", None)
        self._active = True
        self._machine_settings = self._category.getParent() if self._category else None
        self._active_if_setting = None
        self._active_if_value = None
        self._options = kwargs.get("options", [])
        self._unit = kwargs.get("unit", "")
        self._inherit = True
        self._inherit_function = None

    valueChanged = Signal()

    ##  Triggered when all settings are loaded and the setting has a conditional param
    def activeIfHandler(self):
        setting = self._machine_settings.getSettingByKey(self._active_if_setting)
        if setting is not None:
            setting.valueChanged.connect(self.conditionalActiveHandler)
            self.conditionalActiveHandler(setting)
        else:
            Logger.log("w", "Unknown active_if setting %s", self._active_if_setting)
            # Check current value and update active status. (It can happen that the default value is that it's not active)
            #self.setActive(str(self._machine_settings.getSettingValueByKey(self._active_if_setting)) == str(self._active_if_value))

    #   Triggered when the setting it's dependant on changes it's value
    def conditionalActiveHandler(self, setting):
        self.setActive(setting.getValue() == self._active_if_value)

    def isActive(self):
        return self._active
        #if self._parent != None:
        #   if self._parent.isActive() == True:
        #        return self._active
        #else:
        #    return self._active
        #return False    

    def setActive(self, active):
        if self._active != active: 
            self._active = active
            self.activeChanged.emit(self)

    activeChanged = Signal()

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
        if "default" in data:
            self._default_value = data["default"]

        if "type" in data:
            self._type = data["type"]

        self.bindValidator()

        if "label" in data:
            self._label = self._i18n_catalog.i18nc("{0} label".format(self._key), data["label"])

        if "description" in data:
            self._description = self._i18n_catalog.i18nc("{0} description".format(self._key), data["description"])

        if "warning_description" in data:
            self._warning_description = self._i18n_catalog.i18nc("{0} warning description".format(self._key), data["warning_description"])

        if "error_description" in data:
            self._error_description = self._i18n_catalog.i18nc("{0} error description".format(self._key), data["error_description"])
        if "visible" in data:
            self.setVisible(data["visible"])

        if "always_visible" in data:
            self._hide_if_all_children_visible = not data["always_visible"]

        if "unit" in data:
            self._unit = data["unit"]

        self._inherit = data.get("inherit", True)

        if "inherit_function" in data:
            try:
                tree = ast.parse(data["inherit_function"], "eval")
                names = _SettingExpressionVisitor().visit(tree)
                code = compile(data["inherit_function"], self._key, "eval")
            except (SyntaxError, TypeError) as e:
                Logger.log("e", "Parse error in inherit function for setting {0}: {1}".format(self._key, str(e)))
            except IllegalMethodError as e:
                Logger.log("e", "Use of illegal method {0} in inherit function for setting {1}".format(str(e), self._key))
            else:
                self._inherit_function = self._createInheritFunction(code, names)

        min_value = None
        max_value = None
        min_value_warning = None
        max_value_warning = None
        if "min_value" in data:
            min_value = data["min_value"]
        if "max_value" in data:
            max_value = data["max_value"]
        if "min_value_warning" in data:
            min_value_warning = data["min_value_warning"]
        if "max_value_warning" in data:
            max_value_warning = data["max_value_warning"]
        if  self.getValidator() is not None: #Strings don"t have validators as of yet
            self.getValidator().setRange(min_value,max_value,min_value_warning,max_value_warning)

        if "active_if" in data:
            if "setting" in data["active_if"] and "value" in data["active_if"]:
                self._active_if_setting = data["active_if"]["setting"]
                self._active_if_value = data["active_if"]["value"]
                self._machine_settings.settingsLoaded.connect(self.activeIfHandler)

        if "options" in data:
            self._options = data["options"]

        if "children" in data:
            for key, value in data["children"].items():
                setting = self.getSettingByKey(key)
                if not setting:
                    setting = Setting(key, self._i18n_catalog)
                    setting.setCategory(self._category)
                    setting.setParent(self)
                    setting.visibleChanged.connect(self._onChildVisibileChanged)
                    self._children.append(setting)

                setting.fillByDict(value)

    ##  Return the values this setting can have (needs to be set if this is setting is an enum!)
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

    ##  Set the parent of this setting. Parents can override the value of the setting if the child setting is not visible.
    #   mostly used for giving a 'global' setting (such as speed), with children being travel speed, infill speed, etc.
    #   \param setting Setting
    def setParent(self, setting):
        self._parent = setting

    ##  Get the parent.
    #   \returns Setting
    def getParent(self):
        return self._parent

    ##  Add a child to this setting. See setParent for more info.
    #   \param setting Setting
    def addChild(self, setting):
        setting.setParent(self)
        self._children.append(setting)

    ##  Recursively check it's children to see if the key matches.
    #   \returns Setting if key match is found, None otherwise.
    def getSettingByKey(self, key):
        if self._key == key:
            return self
        for s in self._children:
            ret = s.getSettingByKey(key)
            if ret is not None:
                return ret
        return None

    ##  Set the default value of the setting.
    #   \param value
    def setDefaultValue(self, value):
        self._default_value = value
        return self

    ##  get the default value of the setting.
    #   \returns default_value
    def getDefaultValue(self):
        return self._default_value

    ##  Set the visibility of this setting. See setParent for more info.
    #   \param visible Bool
    def setVisible(self, visible):
        if visible != self._visible:
            self._visible = visible
            self.visibleChanged.emit(self)

    ##  Check if the setting is visible. It can be that the setting visible is true, 
    #   but it still should be invisible as all it's children are visible (at this point this setting is overiden by its children 
    #   changing it does nothing, so it needs to be hidden!)
    #   The value is also hidden if it's not active (due to condition (some properties are active based on values of other settings)
    #   \returns bool
    def isVisible(self):
        if not self._visible:
            return False
        if self._hide_if_all_children_visible and self.checkAllChildrenVisible():
            return False
        return True

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

    ##  Set the range of the setting. The validator will give errors or warnings if these are met.
    #   See Validator for more info
    def setRange(self, min_value = None, max_value = None, min_value_warning = None, max_value_warning = None):
        if(self._validator is None):
            return
        self._validator.setRange(min_value, max_value, min_value_warning, max_value_warning)

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
        return self._i18n_catalog.i18n(self._description)

    ##  Get the identifier of the setting
    def getKey(self):
        return self._key

    ## Get the type of the setting
    # \returns type
    def getType(self):
        return self._type

    def getUnit(self):
        return self._unit

    ##  Get the effective value of the setting. This can be 'overriden' by a parent function if this function is invisible.
    #   \returns value
    def getValue(self):
        if not self._visible:
            if self._inherit and self._parent and type(self._parent) is Setting:
                if self._inherit_function:
                    try:
                        inherit_value = self._inherit_function(self._parent, self._machine_settings)
                    except Exception as e:
                        Logger.log("e", "An error occurred in inherit function for {0}: {1}".format(self._key, str(e)))
                    else:
                        self.setValue(inherit_value)
                else:
                    self.setValue(self._parent.getValue())

        retval = self._value
        if self._value is None:
            retval = self._default_value

        return retval

    ##  Set the value of this setting and emit valueChanged signal
    #   \param value Value to be set.
    def setValue(self, value):
        if self._value != value:
            # Strings and enums are stored as strings, do not try to parse them.
            # In addition, if we get a non-string type, also do not try to parse it.
            if type(value) is str and self._type != "string" and self._type != "enum":
                try:
                    self._value = ast.literal_eval(value)
                except SyntaxError:
                    self._value = value
            else:
                self._value = value
            self.valueChanged.emit(self)

    ##  Validate the value of this setting. 
    #   \returns ResultCodes.succes if there is no validator or if validation is succesfull. Returns warning or error code otherwise.
    def validate(self):
        if self._validator is not None:
            return self._validator.validate()
        else:
            return ResultCodes.succes

    def getAllChildren(self):
        all_children = []
        for s in self._children:
            all_children.append(s)
            all_children.extend(s.getAllChildren())
        return all_children

    def getChildren(self):
        return self._children

    def __repr__(self):
        return "<Setting: %s>" % (self._key)

    def __deepcopy__(self, memo):
        copy = Setting(
            self._key,
            self._i18n_catalog,
            label = self._label,
            description = self._description,
            default = self._default_value,
            value = self._value,
            type = self._type,
            visible = self._visible,
            category = self._category,
            unit = self._unit
        )

        copy._validator = self._validator
        copy._parent = self._parent
        copy._hide_if_all_children_visible = self._hide_if_all_children_visible
        copy._children = deepcopy(self._children, memo)
        copy._active = self._active
        copy._machine_settings = self._machine_settings
        copy._active_if_setting = self._active_if_setting
        copy._active_if_value = self._active_if_value
        copy._options = deepcopy(self._options, memo)
        copy._inherit = self._inherit
        copy._inherit_function = deepcopy(self._inherit_function, memo)

        copy._fixChildren()

        return copy

    ## private:

    # Fixes parent assignment after a deepcopy operation
    def _fixChildren(self):
        for child in self._children:
            child.setParent(self)
            child._fixChildren()

    def _onChildVisibileChanged(self, setting):
        self.visibleChanged.emit(setting)
        self.visibleChanged.emit(self)

    # Create a function that will run \param code, making the names in \param names available as local variables
    def _createInheritFunction(self, code, names):
        def inherit(parent, settings, c = code, n = names):
            locals = {
                "parent_value": parent.getValue(),
                "settings": settings
            }

            for name in names:
                locals[name] = settings.getSettingValueByKey(name)

            return eval(c, globals(), locals)

        return inherit

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
