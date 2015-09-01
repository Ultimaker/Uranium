# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Settings.Setting import Setting
from UM.Resources import Resources
from UM.Application import Application
from UM.Signal import Signal, SignalEmitter

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

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
    OverriddenRole = Qt.UserRole + 13
    EnabledRole = Qt.UserRole + 14
    
    def __init__(self, category, parent = None):
        super().__init__(parent)
        self._category = category
        self._ignore_setting_value_update = None

        self._machine_manager = Application.getInstance().getMachineManager()

        self._changed_setting = None

        self._profile = None
        self._machine_manager.activeProfileChanged.connect(self._onProfileChanged)
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
        self.addRoleName(self.OverriddenRole, "overridden")
        self.addRoleName(self.EnabledRole, "enabled")
    
    settingChanged = Signal()

    @pyqtSlot(int, str, "QVariant")
    ##  Notification that setting has changed.  
    def setSettingValue(self, index, key, value):
        setting = self._category.getSettingByKey(key)
        if setting and value:
            if self._profile.isReadOnly():
                custom_profile_name = catalog.i18nc("@item appended to customised profiles ({0} is old profile name)", "{0} (Customised)", self._profile.getName())

                custom_profile = self._machine_manager.findProfile(custom_profile_name)
                if not custom_profile:
                    custom_profile = deepcopy(self._profile)
                    custom_profile.setName(custom_profile_name)
                    self._machine_manager.addProfile(custom_profile)

                self._changed_setting = (key, value)
                self._machine_manager.setActiveProfile(custom_profile)
                return

            self._profile.setSettingValue(key, value)
            self.setProperty(index, "valid", setting.validate(setting.parseValue(value)))

    @pyqtSlot(str, bool)
    def setSettingVisible(self, key, visible):
        setting = self._category.getSettingByKey(key)
        if setting:
            setting.setVisible(visible);

    @pyqtSlot(str)
    def resetSettingValue(self, key):
        self._profile.resetSettingValue(key)
        self.setProperty(self.find("key", key), "overridden", False)

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
        self.clear()
        for setting in self._category.getAllSettings():
            value = self._profile.getSettingValue(setting.getKey())

            self.appendItem({
                "name": setting.getLabel(),
                "description": setting.getDescription(),
                "type": setting.getType(),
                "value": str(value),
                "valid": setting.validate(value),
                "key": setting.getKey(),
                "options": self.createOptionsModel(setting.getOptions()),
                "unit": setting.getUnit(),
                "visible": setting.isVisible(),
                "depth": setting.getDepth(),
                "warning_description": setting.getWarningDescription(),
                "error_description": setting.getErrorDescription(),
                "overridden": (not self._profile.isReadOnly()) and self._profile.hasSettingValue(setting.getKey()),
                "enabled": setting.isEnabled()
            })
            setting.visibleChanged.connect(self._onSettingVisibleChanged)
            setting.enabledChanged.connect(self._onSettingEnabledChanged)

    def _onSettingVisibleChanged(self, setting):
        if setting:
            index = self.find("key", setting.getKey())
            if index != -1:
                self.setProperty(index, "visible", setting.isVisible())

    def _onSettingEnabledChanged(self, setting):
        if setting:
            index = self.find("key", setting.getKey())
            if index != -1:
                self.setProperty(index, "enabled", setting.isEnabled())

    def _onProfileChanged(self):
        if self._profile:
            self._profile.settingValueChanged.disconnect(self._onSettingValueChanged)

        self._profile = self._machine_manager.getActiveProfile()
        if self._profile:
            self._profile.settingValueChanged.connect(self._onSettingValueChanged)
            self.updateSettings()

            if self._changed_setting:
                index = self.find("key", self._changed_setting[0])
                self.setSettingValue(index, self._changed_setting[0], self._changed_setting[1])
                self._changed_setting = None

    def _onSettingValueChanged(self, key):
        index = self.find("key", key)
        if index != -1:
            setting = self._category.getSettingByKey(key)
            value = self._profile.getSettingValue(key)
            self.setProperty(index, "value", str(value))
            self.setProperty(index, "overridden", self._profile.hasSettingValue(key))
            self.setProperty(index, "valid", setting.validate(value))
