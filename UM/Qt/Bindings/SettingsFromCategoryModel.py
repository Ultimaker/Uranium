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
    
    def __init__(self, category, parent = None):
        super().__init__(parent)
        self._category = category
        self.updateSettings()
        self._ignore_setting_value_update = None

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
    
    settingChanged = Signal()

    @pyqtSlot(int, str, "QVariant")
    ##  Notification that setting has changed.  
    def setSettingValue(self, index, key, value):
        setting = self._category.getSettingByKey(key)
        if setting:
            self._ignore_setting_value_update = setting
            setting.setValue(value)
            self._ignore_setting_value_update = None
            self.setProperty(index, "valid", setting.validate())

    @pyqtSlot(str)
    def hideSetting(self, key):
        setting = self._category.getSettingByKey(key)
        if setting:
            setting.setVisible(False);

    ##  Create model for combo box (used by enum type setting) 
    #   \param options List of strings
    #   \return ListModel with "text":value pairs
    def createOptionsModel(self, options):
        model = ListModel()
        model.addRoleName(self.NameRole,"name")
        for option in options:
            model.appendItem({"name": str(option)})
        return model

    def updateSettings(self):
        for setting in self._category.getAllSettings():
            self.appendItem({
                "name": setting.getLabel(),
                "description": setting.getDescription(),
                "type": setting.getType(),
                "value": setting.getValue(),
                "valid": setting.validate(),
                "key": setting.getKey(),
                "options": self.createOptionsModel(setting.getOptions()),
                "unit": setting.getUnit(),
                "visible": (setting.isVisible() and setting.isActive())
                "depth": setting.getDepth()
            })
            setting.visibleChanged.connect(self._onSettingChanged)
            setting.activeChanged.connect(self._onSettingChanged)
            setting.valueChanged.connect(self._onSettingChanged)

    def _onSettingChanged(self, setting):
        self.settingChanged.emit()
        if setting is not None:
            index = self.find("key", setting.getKey())
            if index != -1:
                self.setProperty(index, "visible", (setting.isVisible() and setting.isActive()))

                if setting is not self._ignore_setting_value_update:
                    self.setProperty(index, "value", setting.getValue())

                self.setProperty(index, "valid", setting.validate())
        self.settingChanged.emit()
