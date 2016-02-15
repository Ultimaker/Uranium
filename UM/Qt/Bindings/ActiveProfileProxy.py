# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QVariant, QUrl

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry

from . import ContainerProxy

class ActiveProfileProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._setting_values = {}
        self._container_proxy = ContainerProxy.ContainerProxy(self._setting_values)
        self._active_profile = None
        Application.getInstance().getMachineManager().activeProfileChanged.connect(self._onActiveProfileChanged)
        self._onActiveProfileChanged()

    activeProfileChanged = pyqtSignal()

    @pyqtProperty(bool, notify = activeProfileChanged)
    def valid(self):
        return self._active_profile != None

    settingValuesChanges = pyqtSignal()
    
    @pyqtProperty(QObject, notify = settingValuesChanges)
    def settingValues(self):
        return self._container_proxy

    @pyqtSlot(str, "QVariant")
    def setSettingValue(self, key, value):
        self._active_profile.setSettingValue(key, value)

    ## Show any settings that have a value in the current profile but are not visible.
    @pyqtSlot(str)
    def showHiddenValues(self, category_id):
        category = Application.getInstance().getMachineManager().getActiveMachineInstance().getMachineDefinition().getSettingsCategory(category_id)
        for setting in category.getAllSettings():
            if not setting.isVisible() and self._active_profile.hasSettingValue(setting.getKey(), filter_defaults = False):
                setting.setVisible(True)
        category.visibleChanged.emit(category)

    def _onActiveProfileChanged(self):
        if self._active_profile:
            self._active_profile.settingValueChanged.disconnect(self._onSettingValuesChanged)

        self._active_profile = Application.getInstance().getMachineManager().getWorkingProfile()
        self.activeProfileChanged.emit()

        if self._active_profile:
            self._active_profile.settingValueChanged.connect(self._onSettingValuesChanged)
            self._onSettingValuesChanged()

    def _onSettingValuesChanged(self, setting = None):
        self._setting_values.update(self._active_profile.getAllSettingValues())
        self.settingValuesChanges.emit()

def createActiveProfileProxy(engine, script_engine):
    return ActiveProfileProxy()

