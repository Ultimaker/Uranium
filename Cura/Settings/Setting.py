from Cura.Settings.Validators.IntValidator import IntValidator
from Cura.Settings.Validators.FloatValidator import FloatValidator

## A setting object contains a (single) configuration setting.
# Settings have validators that check if the value is valid, but do not prevent invalid values!
# Settings have conditions that enable/disable this setting depending on other settings. (Ex: Dual-extrusion)

class Setting(object):    
    def __init__(self, key, default, type):
        self._key = key
        self._label = key
        self._tooltip = ''
        self._default = unicode(default)
        self._value = None
        self._machine = None
        self._type = type
        self._visible = True
        self._validator = None
        self._callbacks = []
        self._conditions = []
        self._parent_setting = None
        self._hide_if_all_children_visible = True
        self._copy_from_parent_function = lambda machine, value: value
        self._child_settings = []

        if type == 'float':
            FloatValidator(self) # Validator sets itself as validator to this setting
        elif type == 'int':
            IntValidator(self) 
    
    def setValidator(self, validator):
        self._validator = validator
        
    def getValidator(self):
        return self._validator
    
    def setParent(self, setting):
        self._parent_setting = setting
    
    def addSetting(self, setting):
        setting.setParent(self)
        self._child_settings.append(setting)

    ## Recursively check it's children to see if the key matches.
    # \returns Setting if key match is found, None otherwise.
    def getSettingByKey(self, key):
        if self._key == key:
            return self
        for s in self._child_settings:
            ret = s.getSettingByKey(key)
            if ret is not None:
                return ret
        return None

    def setMachine(self, machine):
        self._machine = machine

    def setVisible(self, visible):
        self._visible = visible
        return self

    def setDefault(self, value):
        self._default = value
        return self

    def getDefault(self):
        return self._default

    def getVisibleProperty(self):
        return self._visible

    def isVisible(self):
        if not self._visible:
            return False
        if self._hide_if_all_children_visible and self.checkAllChildrenVisible():
            return False
        return True

    ## Check if all children are visible.
    # \returns True if all children are visible. False otherwise
    def checkAllChildrenVisible(self):
        if len(self._child_settings) < 1:
            return False
        for c in self._child_settings:
            if not c._visible and not c.checkAllChildrenVisible():
                return False
        return True

    def setLabel(self, label):
        self._label = label
        
    def setTooltip(self, tooltip)
        self._tooltip = tooltip

    def setRange(self, min_value = None, max_value = None,min_value_warning = None, max_value_warning):
        if(self._validator = None):
            return
        
        validator.setRange(min_value, max_value 
        self._validators[0].maxValue = maxValue
        return self

    def setCopyFromParentFunction(self, function):
        self._copy_from_parent_function = function

    def getLabel(self):
        return self._label

    def getTooltip(self):
        return self._tooltip

    def getKey(self):
        return self._key

    def getType(self):
        return self._type

    def getValue(self):
        if not self._visible:
            if self._copy_from_parent_function is not None and self._parent_setting is not None:
                self._value = str(self._copy_from_parent_function(self._machine, self._parent_setting.getValue()))
            else:
                return self._default
        if self._value is None:
            return self._default
        return self._value

    def getDefault(self):
        return self._default

    def setValue(self, value):
        if self._value != value:
            self._value = value
            for callback in self._callbacks:
                callback()
            self._machine.onSettingUpdated()

    def validate(self):
        result = settingValidators.SUCCESS
        msgs = []
        for validator in self._validators:
            res, err = validator.validate()
            if res == settingValidators.ERROR:
                result = res
            elif res == settingValidators.WARNING and result != settingValidators.ERROR:
                result = res
            if res != settingValidators.SUCCESS:
                msgs.append(err)
        return result, '\n'.join(msgs)

    def addCondition(self, conditionFunction):
        self._conditions.append(conditionFunction)

    def checkConditions(self):
        for condition in self._conditions:
            if not condition():
                return False
        return True

    def addCallback(self, callback):
        self._callbacks.append(callback)

    def getSettings(self):
        settings = []
        for s in self._child_settings:
            settings.append(s)
            settings += s.getSettings()
        return settings

    def getChildren(self):
        return self._child_settings

    def __repr__(self):
        return '<Setting: %s>' % (self._key)