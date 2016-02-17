# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Application import Application

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class MachineManagerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._active_machine_instance = None
        self._active_profile = None

        self._manager = Application.getInstance().getMachineManager()

        self._changed_setting = None

        self._active_machine = None
        self._manager.activeMachineInstanceChanged.connect(self._onActiveMachineInstanceChanged)
        self._manager.activeProfileChanged.connect(self._onActiveProfileChanged)
        self._manager.machineInstanceNameChanged.connect(self._onInstanceNameChanged)
        self._manager.profileNameChanged.connect(self._onProfileNameChanged)
        self._onActiveMachineInstanceChanged()
        self._onActiveProfileChanged()

    activeMachineInstanceChanged = pyqtSignal()

    @pyqtProperty(str, notify = activeMachineInstanceChanged)
    def activeMachineInstance(self):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return ""

        return instance.getName()

    @pyqtSlot(str)
    def setActiveMachineInstance(self, name):
        instance = self._manager.findMachineInstance(name)
        if instance:
            self._manager.setActiveMachineInstance(instance)

    @pyqtProperty(bool, notify = activeMachineInstanceChanged)
    def hasVariants(self):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return False

        return instance.getMachineDefinition().hasVariants()

    @pyqtProperty(str, notify = activeMachineInstanceChanged)
    def activeMachineVariant(self):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return ""

        return instance.getMachineDefinition().getVariantName()

    @pyqtSlot(str)
    def setActiveMachineVariant(self, name):
        self._manager.setActiveMachineVariant(name)

    @pyqtProperty(bool, notify = activeMachineInstanceChanged)
    def hasMaterials(self):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return False

        return instance.hasMaterials()

    @pyqtProperty(str, notify = activeMachineInstanceChanged)
    def activeMaterial(self):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return ""

        return instance.getMaterialName()

    @pyqtSlot(str)
    def setActiveMaterial(self, name):
        self._manager.setActiveMaterial(name)

    activeProfileChanged = pyqtSignal()

    @pyqtProperty(str, notify = activeProfileChanged)
    def activeProfile(self):
        profile = self._manager.getActiveProfile()
        if not profile:
            return ""

        return profile.getName()

    @pyqtSlot(str)
    def setActiveProfile(self, name):
        profile = self._manager.findProfile(name)
        if profile:
            self._manager.setActiveProfile(profile)

    @pyqtSlot(str, result = bool)
    def checkInstanceExists(self, name):
        instance = self._manager.findMachineInstance(name)
        if instance:
            return True
        else:
            return False

    @pyqtSlot(str, result = int)
    def getSettingValue(self, setting):
        profile = self._manager.getWorkingProfile()
        if not profile:
            return None
        return profile.getSettingValue(setting)

    @pyqtSlot(str, "QVariant")
    def setSettingValue(self, key, value):
        profile = self._manager.getWorkingProfile()
        if not profile:
            return

        profile.setSettingValue(key, value)

    @pyqtSlot(str, "QVariant")
    def setMachineSettingValue(self, key, value):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return

        instance.setMachineSettingValue(key, value)

    @pyqtSlot(result = str)
    def createProfile(self):
        profile = self._manager.addProfileFromWorkingProfile()
        #Prevent "Replace profile?" dialog; working profile will get replaced by setActiveProfile()
        self._manager.getWorkingProfile().setChangedSettings({})
        self._manager.setActiveProfile(profile)
        return profile.getName()

    def _onActiveMachineInstanceChanged(self):
        self.activeMachineInstanceChanged.emit()

    def _onActiveProfileChanged(self):
        self.activeProfileChanged.emit()

        if self._changed_setting:
            self.setSettingValue(self._changed_setting[0], self._changed_setting[1])
            self._changed_setting = None

    def _onInstanceNameChanged(self, machine):
        self.activeMachineInstanceChanged.emit()

    def _onProfileNameChanged(self, profile):
        self.activeProfileChanged.emit()


def createMachineManagerProxy(engine, script_engine):
    return MachineManagerProxy()
