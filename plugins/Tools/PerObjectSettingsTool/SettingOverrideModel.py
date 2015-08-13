# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, QUrl

from UM.Application import Application
from UM.Qt.ListModel import ListModel

class SettingOverrideModel(ListModel):
    KeyRole = Qt.UserRole + 1
    LabelRole = Qt.UserRole + 2
    DescriptionRole = Qt.UserRole + 3
    ValueRole = Qt.UserRole + 4
    TypeRole = Qt.UserRole + 5
    UnitRole = Qt.UserRole + 6
    ValidRole = Qt.UserRole + 7

    def __init__(self, decorator, parent = None):
        super().__init__(parent)

        self._decorator = decorator
        self._decorator.settingAdded.connect(self._onSettingsChanged)
        self._decorator.settingRemoved.connect(self._onSettingsChanged)
        self._decorator.settingValueChanged.connect(self._onSettingValueChanged)
        self._onSettingsChanged()

        self.addRoleName(self.KeyRole, "key")
        self.addRoleName(self.LabelRole, "label")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.ValueRole,"value")
        self.addRoleName(self.TypeRole, "type")
        self.addRoleName(self.UnitRole, "unit")
        self.addRoleName(self.ValidRole, "valid")


    def _onSettingsChanged(self):
        self.clear()

        active_instance = Application.getInstance().getMachineManager().getActiveMachineInstance()

        for key, value in self._decorator.getAllSettings().items():
            setting = active_instance.getSettingByKey(key)
            if not setting:
                continue

            self.appendItem({
                "key": key,
                "label": setting.getLabel(),
                "description": setting.getDescription(),
                "value": value,
                "type": setting.getType(),
                "unit": setting.getUnit(),
                "valid": setting.validate()
            })

    def _onSettingValueChanged(self, key, value):
        index = self.find("key", key)
        if index != -1:
            self.setProperty(index, "value", value)
