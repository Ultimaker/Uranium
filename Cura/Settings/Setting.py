from Cura.Settings.Validators.IntValidator import IntValidator
from Cura.Settings.Validators.FloatValidator import FloatValidator
from Cura.Settings.Validators.ResultCodes import ResultCodes

##    A setting object contains a (single) configuration setting.
#     Settings have validators that check if the value is valid, but do not prevent invalid values!
#     Settings have conditions that enable/disable this setting depending on other settings. (Ex: Dual-extrusion)
class Setting(object):    
    def __init__(self, key = None, default = None, type = None, category = None, label = None):
        self._key = key
        if label is None:
            self._label = key
        self._tooltip = ''
        self._default_value = str(default)
        self._value = None
        self._type = type
        self._visible = True
        self._validator = None
        self._callbacks = [] #Callbacks trigged when the value is changed
        self._conditions = []
        self._parent = None
        self._hide_if_all_children_visible = True
        self._children = []
        self._category = category


    ##  Bind new validator to object based on it's current type
    def bindValidator(self):
        if self._type == 'float':
            FloatValidator(self) # Validator sets itself as validator to this setting
        elif self._type == 'int':
            IntValidator(self)
    
    ##  Get the depth of this setting (how many steps is it 'away' from its category)
    def getDepth(self):
        return self._parent.getDepth() + 1
    
    ##  Set values of the setting by providing it with a dict object (as decoded by JSON parser)
    #   \param data Decoded JSON dict
    def fillByDict(self, data):
        if "key" in data and "default" in data and "type" in data:
            self._key = data["key"]
            self._default_value = str(data["default"])
            self._type = data["type"]
            self.bindValidator()
            if "label" in data:
                self.setLabel(data["label"])
            if "visible" in data:
                self.setVisible(data["visible"])
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
            self.getValidator().setRange(min_value,max_value,min_value_warning,max_value_warning)
        
        if "children" in data:
            for setting in data["children"]:
                temp_setting = Setting()
                temp_setting.setParent(self)
                temp_setting.fillByDict(setting)
                self._children.append(temp_setting)
            
         
    
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
    
    ##  Set the visibility of this setting. See setParent for more info.
    #   \param visible Bool
    def setVisible(self, visible):
        self._visible = visible
    
    ##  Set the default value of the setting.
    #   \param value
    def setDefaultValue(self, value):
        self._default_value = value
        return self
   
    ##  get the default value of the setting.
    #   \returns default_value
    def getDefaultValue(self):
        return self._default_value

    ##  Check if the setting is visible. It can be that the setting visible is true, 
    #   but it still should be invisible as all it's children are visible (at this point this setting is overiden by its children 
    #   changing it does nothing, so it needs to be hidden!)
    #   \returns bool
    def isVisible(self):
        if not self._visible:
            return False
        if self._hide_if_all_children_visible and self.checkAllChildrenVisible():
            return False
        return True

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
        validator.setRange(min_value, max_value, min_value_warning, max_value_warning)

    ##  Get the display name of the setting
    def getLabel(self):
        if self._label is None:
            return self._key # Return key so it will always have some sort of display name
        return self._label
    
    ##  Set the label (display name) of setting.
    #   \param label 
    def setLabel(self, label):
        self._label = label

    ##  Get the tooltip (if any) from the setting
    def getTooltip(self):
        return self._tooltip
    
    ##  Set the tooltip of this setting
    #   \param tooltip
    def setTooltip(self, tooltip):
        self._tooltip = tooltip

    ##  Get the identifier of the setting
    def getKey(self):
        return self._key

    ## Get the type of the setting
    # \returns type
    def getType(self):
        return self._type
    
    ##  Get the effective value of the setting. This can be 'overriden' by a parent function if this function is invisible.
    #   \returns value
    def getValue(self):
        if not self._visible:
            if self._parent is not None:
                self._value = self._parent.getValue()
            else:
                return self._default_value
        if self._value is None:
            return self._default_value
        return self._value

    ##  Set the value of this setting and call the registered callbacks.
    #   \param value Value to be set.
    def setValue(self, value):
        if self._value != value:
            self._value = value
            for callback in self._callbacks:
                callback()
    
    ##   Add function to be called when value is changed.
    #   \param function to be added.
    def addValueChangedCallback(self, callback):
        self._callbacks.append(callback)
    
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
        return '<Setting: %s>' % (self._key)