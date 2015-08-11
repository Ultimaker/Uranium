# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Settings.MachineSettings import MachineSettings
from UM.Resources import Resources

class MachineDefinition():
    def __init__(self, machine_id, json_file):
        self._machine_id = machine_id
        self._json_file = json_file

        self._name = ""
        self._variant_name = None
        self._manufacturer = ""
        self._author = ""

    def getId(self):
        return self._machine_id

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getVariantName(self):
        return self._variant_name

    def setVariantName(self, name):
        self._variant_name = name

    def getManufacturer(self):
        return self._manufacturer

    def setManufacturer(self, manufacturer):
        self._manufacturer = manufacturer

    def getAuthor(self):
        return self._author

    def setAuthor(self, author):
        self._author = author

    def createInstance(self, name):
        instance = MachineSettings()
        instance.loadSettingsFromFile(Resources.getPath(Resources.MachineDefinitions, self._json_file))
        instance.setName(name)
        return instance
