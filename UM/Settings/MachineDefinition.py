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
    # Because Python sort is stupid and does not allow for specifying a comparison method
    def __lt__(self, other):
        # This makes sure we place Ultimaker machines at the top of the list and "Other" at the bottom
        if self._manufacturer == self.UltimakerManufacturerString and other.getManufacturer() != self.UltimakerManufacturerString:
            return True

        if self._manufacturer != self.UltimakerManufacturerString and other.getManufacturer() == self.UltimakerManufacturerString:
            return False

        if self._manufacturer == self.OtherManufacturerString and other.getManufacturer() != self.OtherManufacturerString:
            return False

        if self._manufacturer != self.OtherManufacturerString and other.getManufacturer() == self.OtherManufacturerString:
            return True

        # Otherwise, just sort by manufacturer and name
        if self._manufacturer < other.getManufacturer():
            return True
        elif self._manufacturer == other.getManufacturer():
            return self._name < other.getName()
        else:
            return False
