# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Application import Application

class MachineManagerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._active_machine_instance = None
        self._active_profile = None

        self._manager = Application.getInstance().getMachineManager()

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
        instance = self._machine_manager.findMachineInstance(name)
        if instance:
            self._machine_manager.setActiveMachineInstance(instance)

    @pyqtProperty(bool, notify = activeMachineInstanceChanged)
    def hasVariants(self):
        instance = self._manager.getActiveMachineInstance()
        if not instance:
            return False

        return instance.getMachineDefinition().hasVariants()

    @pyqtSlot(str)
    def setActiveMachineVariant(self, name):
        pass

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

    def _onActiveMachineInstanceChanged(self):
        self.activeMachineInstanceChanged.emit()

    def _onActiveProfileChanged(self):
        self.activeProfileChanged.emit()

    def _onInstanceNameChanged(self, machine):
        self.activeMachineInstanceChanged.emit()

    def _onProfileNameChanged(self, profile):
        self.activeProfileChanged.emit()


def createMachineManagerProxy(engine, script_engine):
    return MachineManagerProxy()
