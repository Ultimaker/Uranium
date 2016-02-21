# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from copy import deepcopy

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Settings.Setting import Setting
from UM.Resources import Resources
from UM.Application import Application
from UM.Signal import Signal, SignalEmitter
from copy import deepcopy

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
    FilteredRole = Qt.UserRole + 15
    GlobalOnlyRole = Qt.UserRole + 16
    ProhibitedRole = Qt.UserRole + 17 # This setting can never be enabled

    def __init__(self, category, parent = None, machine_manager = None):
        super().__init__(parent)
        self._category = category
        self._ignore_setting_value_update = None

        self._machine_manager = machine_manager
        if not self._machine_manager:
            self._machine_manager = Application.getInstance().getMachineManager()

        self._changed_setting = None

        self._profile = self._machine_manager.getWorkingProfile()
        self._machine_manager.activeProfileChanged.connect(self._onProfileChanged)
        if self._profile is not None: # A profile is already set but we did not recieve the event.
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
        self.addRoleName(self.FilteredRole, "filtered")
        self.addRoleName(self.GlobalOnlyRole, "global_only")
        self.addRoleName(self.ProhibitedRole, "prohibited")

    settingChanged = Signal()

    @pyqtSlot(str, "QVariant")
    ##  Notification that setting has changed.  
    def setSettingValue(self, key, value):
        index = self.find("key", key)
        if index == -1:
            return
        setting = self._category.getSetting(key)
        if setting:
            self._profile.setSettingValue(key, value)
            self.setProperty(index, "value", str(value))
            self.setProperty(index, "valid", setting.validate(setting.parseValue(value)))

    @pyqtSlot(str, bool)
    def setSettingVisible(self, key, visible):
        setting = self._category.getSetting(key)
        if setting:
            setting.setVisible(visible);

    @pyqtSlot(str)
    def resetSettingValue(self, key):
        setting = self._category.getSetting(key)
        if setting:
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
        model.sort(lambda t: t["name"])
        return model

    @pyqtSlot(str)
    def hideSetting(self, key):
        setting = self._category.getSetting(key)
        if setting:
            setting.setVisible(False);

    @pyqtSlot(str)
    def filter(self, filter):
        filter = filter.lower()
        for index in range(len(self.items)):
            if filter in self.items[index]["name"].lower():
                self.setProperty(index, "filtered", False)
            else:
                self.setProperty(index, "filtered", True)

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
                "overridden": (not self._profile.isReadOnly()) and self._profile.hasSettingValue(setting.getKey(), filter_defaults = True),
                "enabled": setting.isEnabled(),
                "filtered": False,
                "global_only": setting.getGlobalOnly(),
                "prohibited": setting.isProhibited()
            })
            setting.visibleChanged.connect(self._onSettingVisibleChanged)
            setting.enabledChanged.connect(self._onSettingEnabledChanged)
            setting.globalOnlyChanged.connect(self._onSettingGlobalOnlyChanged)

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

    ##  Updates the global only property if any of its dependencies have its
    #   value changed.
    #
    #   \param setting The setting whose value has changed.
    def _onSettingGlobalOnlyChanged(self, setting):
        if setting:
            index = self.find("key", setting.getKey())
            if index != -1:
                self.setProperty(index, "global_only", setting.getGlobalOnly())

    def _onProfileChanged(self):
        if self._profile:
            self._profile.settingValueChanged.disconnect(self._onSettingValueChanged)

        self._profile = self._machine_manager.getWorkingProfile()
        if self._profile:
            self._profile.settingValueChanged.connect(self._onSettingValueChanged)
            self.updateSettings()

            if self._changed_setting:
                self.setSettingValue(self._changed_setting[0], self._changed_setting[1])
                self._changed_setting = None

    def _onSettingValueChanged(self, key):
        index = self.find("key", key)
        if index != -1:
            setting = self._category.getSetting(key)
            value = self._profile.getSettingValue(key)

            self.setProperty(index, "value", str(value))
            self.setProperty(index, "overridden", self._profile.hasSettingValue(key, filter_defaults = True))
            self.setProperty(index, "valid", setting.validate(value))
