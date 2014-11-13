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
        self._validators = []
        self._callbacks = []
        self._conditions = []
        self._parent_setting = None
        self._hide_if_all_children_visible = True
        self._copy_from_parent_function = lambda machine, value: value
        self._child_settings = []

        if type == 'float':
            settingValidators.validFloat(self)
        elif type == 'int':
            settingValidators.validInt(self)

    def addSetting(self, setting):
        setting._parent_setting = self
        self._child_settings.append(setting)

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
        if self._hide_if_all_children_visible and self.allChildrenVisible():
            return False
        return True

    def allChildrenVisible(self):
        if len(self._child_settings) < 1:
            return False
        for c in self._child_settings:
            if not c._visible and not c.allChildrenVisible():
                return False
        return True

    def setAlwaysVisible(self):
        self._hide_if_all_children_visible = False
        return self

    def setLabel(self, label, tooltip=''):
        self._label = label
        self._tooltip = tooltip
        return self

    def setRange(self, minValue=None, maxValue=None):
        if len(self._validators) < 1:
            return
        self._validators[0].minValue = minValue
        self._validators[0].maxValue = maxValue
        return self

    def setCopyFromParentFunction(self, func):
        self._copy_from_parent_function = func

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