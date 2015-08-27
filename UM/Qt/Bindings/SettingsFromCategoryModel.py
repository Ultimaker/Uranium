# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Settings.Setting import Setting
from UM.Resources import Resources
from UM.Application import Application
from UM.Signal import Signal, SignalEmitter

class SettingsFromCategoryModel(ListModel, SignalEmitter):
    NameRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    ValueRole = Qt.UserRole + 3
    ValidRole = Qt.UserRole + 4
    KeyRole = Qt.UserRole + 5
    OptionsRole = Qt.UserRole + 6
    UnitRole = Qt.UserRole + 7
    DescriptionRole = Qt.UserRole + 8
    VisibleRole = Qt.UserRole + 9
    DepthRole = Qt.UserRole + 10
    WarningDescriptionRole = Qt.UserRole + 11
    ErrorDescriptionRole = Qt.UserRole + 12
    
    def __init__(self, category, parent = None):
        super().__init__(parent)
        self._category = category
        self._ignore_setting_value_update = None

        self._profile = None
        Application.getInstance().getMachineManager().activeProfileChanged.connect(self._onProfileChanged)
        self._onProfileChanged()

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.TypeRole,"type")
        self.addRoleName(self.ValueRole,"value")
        self.addRoleName(self.ValidRole,"valid")
        self.addRoleName(self.KeyRole,"key")
        self.addRoleName(self.OptionsRole,"options")
        self.addRoleName(self.UnitRole,"unit")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.VisibleRole, "visible")
        self.addRoleName(self.DepthRole, "depth")
        self.addRoleName(self.WarningDescriptionRole, "warning_description")
        self.addRoleName(self.ErrorDescriptionRole, "error_description")
    
    settingChanged = Signal()

    @pyqtSlot(int, str, "QVariant")
    ##  Notification that setting has changed.  
    def setSettingValue(self, index, key, value):
        self._profile.setSettingValue(key, value)

        #setting = self._category.getSettingByKey(key)
        #if setting:
            #self._ignore_setting_value_update = setting
            #setting.setValue(value)
            #self._ignore_setting_value_update = None
            #self.setProperty(index, "valid", setting.validate())

    @pyqtSlot(str, bool)
    def setSettingVisible(self, key, visible):
        setting = self._category.getSettingByKey(key)
        if setting:
            setting.setVisible(visible);

    ##  Create model for combo box (used by enum type setting) 
    #   \param options List of strings
    #   \return ListModel with "text":value pairs
    def createOptionsModel(self, options):
        if not options:
            return None

        model = ListModel()
        model.addRoleName(Qt.UserRole + 1, "value")
        model.addRoleName(Qt.UserRole + 2, "name")
        for value, name in options.items():
            model.appendItem({"value": str(value), "name": str(name)})
        return model

    def updateSettings(self):
        for setting in self._category.getAllSettings():
            self.appendItem({
                "name": setting.getLabel(),
                "description": setting.getDescription(),
                "type": setting.getType(),
                "value": setting.getDefaultValue(),
                "valid": setting.validate(self._profile.getSettingValue(setting.getKey())),
                "key": setting.getKey(),
                "options": self.createOptionsModel(setting.getOptions()),
                "unit": setting.getUnit(),
                #"visible": (setting.isVisible() and setting.isActive()),
                "visible": setting.isVisible(),
                "depth": setting.getDepth(),
                "warning_description": setting.getWarningDescription(),
                "error_description": setting.getErrorDescription(),
                "overridden": self._profile.hasSettingValue(setting.getKey())
            })
            setting.visibleChanged.connect(self._onSettingChanged)
            #setting.activeChanged.connect(self._onSettingChanged)
            #setting.valueChanged.connect(self._onSettingChanged)

    def _onSettingChanged(self, setting):
        self.settingChanged.emit()
        if setting is not None:
            index = self.find("key", setting.getKey())
            if index != -1:
                self.setProperty(index, "visible", setting.isVisible())

                value = self._profile.getSettingValue(setting.getKey())

                if setting is not self._ignore_setting_value_update:
                    #self.setProperty(index, "value", setting.getValue())
                    self.setProperty(index, "value", value)

                self.setProperty(index, "valid", setting.validate(value))
        self.settingChanged.emit()

    def _onProfileChanged(self):
        if self._profile:
            self._profile.settingValueChanged.disconnect(self._onSettingValueChanged)

        self._profile = Application.getInstance().getMachineManager().getActiveProfile()
        self._profile.settingValueChanged.connect(self._onSettingValueChanged)
        self.updateSettings()

    def _onSettingValueChanged(self, key):
        index = self.find("key", key)
        if index != -1:
            self.setProperty(index, "value", self._profile.getSettingValue(key))
