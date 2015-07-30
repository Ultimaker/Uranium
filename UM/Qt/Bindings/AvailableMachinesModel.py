# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Qt.ListModel import ListModel
from UM.Resources import Resources
from UM.Application import Application
from UM.Logger import Logger
from UM.Settings.MachineSettings import MachineSettings

import os
import os.path
import json

class AvailableMachinesModel(ListModel):
    NameRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    VariationsRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.TypeRole, "type")
        self.addRoleName(self.VariationsRole, "variations")
        
        # Groups all machines that have the same id
        self._machines_by_id = {}

        self._updateModel()

    @pyqtSlot(int, int,str)
    def createMachine(self, index, variation_index, name):
        type = self.getItem(index)["variations"].getItem(variation_index)["type"]

        machine = MachineSettings()
        machine.loadSettingsFromFile(Resources.getPath(Resources.SettingsLocation, type))
        machine.setName(name)

        app = Application.getInstance()
        index = app.addMachine(machine)
        app.setActiveMachine(app.getMachines()[index])

    def _createMachineVariationsModel(self, variations):
        model = ListModel()
        model.addRoleName(self.NameRole,"name")
        model.addRoleName(self.TypeRole, "type")
        for name, json_file in variations:
           # print(name, " " ,json_file)
            model.appendItem({"name": name, "type":json_file})
        return model

    def _updateModel(self):
        dirs = Resources.getLocation(Resources.SettingsLocation)

        for dir in dirs:
            if not os.path.isdir(dir):
                continue

            for file in os.listdir(dir):
                data = None
                path = os.path.join(dir, file)

                if os.path.isdir(path):
                    continue

                with open(path, "rt", -1, "utf-8") as f:
                    try:
                        data = json.load(f)
                    except ValueError as e:
                        Logger.log("e", "Error when loading file {0}: {1}".format(file, e))
                        continue

                # Ignore any file that is explicitly marked as non-visible
                if not data.get("visible", True):
                    continue

                # Ignore any file that is marked as non-visible for the current application.
                appname = Application.getInstance().getApplicationName()
                if appname in data:
                    if not data[appname].get("visible", True):
                        continue
                
                manufacturer = "other"
                if "manufacturer" in data:
                    manufacturer = data["manufacturer"]    
                if data["id"] in self._machines_by_id:
                    self._machines_by_id[data["id"]].append((data["name"],file))
                else:
                    self._machines_by_id[data["id"]] = [(data["name"],file)]
                #self.appendItem({ "name": data["name"], "type": file })

                #self.sort(lambda e: e["name"])
        for entry in self._machines_by_id:
            self.appendItem({"name": entry, "variations": self._createMachineVariationsModel(self._machines_by_id[entry])})
        #print(self.items)    
        #print(self._machines_by_id)
