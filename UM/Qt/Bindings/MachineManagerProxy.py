# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Application import Application

class MachineManagerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._active_machine_instance = None
        self._active_profile = None

        self._machine_manager = Application.getInstance().getMachineManager()

        self._machine_manager.activeMachineInstanceChanged.connect(self._onActiveMachineInstanceChanged)
        self._onActiveMachineInstanceChanged()
        self._machine_manager.activeProfileChanged.connect(self._onActiveProfileChanged)
        self._onActiveProfileChanged()

    activeMachineInstanceChanged = pyqtSignal()
    @pyqtProperty(str, notify = activeMachineInstanceChanged)
    def activeMachineInstance(self):
        instance = self._machine_manager.getActiveMachineInstance()
        if instance:
            return instance.getName()

        return ""

    @pyqtSlot(str)
    def setActiveMachineInstance(self, name):
        index = self._machine_manager.findMachineInstance(name)
        if index != -1:
            self._machine_manager.setActiveMachineInstance(self._machine_manager.getMachineInstance(index))

    @pyqtProperty(bool, notify = activeMachineInstanceChanged)
    def hasVariants(self):
        instance = self._machine_manager.getActiveMachineInstance()
        if not instance:
            return False

        variants = self._machine_manager.getALlMachineVariants(instance.getTypeID())
        return len(variants) > 1

    @pyqtSlot(str)
    def setActiveMachineVariant(self, name):
        pass

    activeProfileChanged = pyqtSignal()
    @pyqtProperty(str, notify = activeProfileChanged)
    def activeProfile(self):
        return self._machine_manager.getActiveProfile().getName()

    @pyqtSlot(str)
    def setActiveProfile(self, name):
        profile = self._machine_manager.findProfile(name)
        if profile:
            self._machine_manager.setActiveProfile(profile)

    def _onActiveMachineInstanceChanged(self):
        self.activeMachineInstanceChanged.emit()

    def _onActiveProfileChanged(self):
        self.activeProfileChanged.emit()


def createMachineManagerProxy(engine, script_engine):
    return MachineManagerProxy()
