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
    IdRole = Qt.UserRole + 1
    FileRole = Qt.UserRole + 2
    NameRole = Qt.UserRole + 3
    ManufacturerRole = Qt.UserRole + 4
    AuthorRole = Qt.UserRole + 5
    PagesRole = Qt.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.FileRole, "file")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ManufacturerRole, "manufacturer")
        self.addRoleName(self.AuthorRole, "author")
        self.addRoleName(self.PagesRole, "pages")

        self._updateModel()


    @pyqtSlot(int,str)
    def createMachine(self, index, name):
        file = self.getItem(index)["file"]

        machine = MachineSettings()
        machine.loadSettingsFromFile(Resources.getPath(Resources.SettingsLocation, file))
        machine.setName(name)

        app = Application.getInstance()
        index = app.addMachine(machine)
        app.setActiveMachine(app.getMachines()[index])

    def _createPagesModel(self, steps):
        model = ListModel()
        model.addRoleName(self.NameRole,"page")
        model.addRoleName(self.NameRole,"title")
        for step in steps:
            _page = step.get("page")
            _title = step.get("title")
            model.appendItem({"title": str(_title), "page": str(_page)})
        return model

    def _updateModel(self):
        dirs = Resources.getLocation(Resources.SettingsLocation)
        _machines_by_ultimaker = []
        _machines_by_other = []

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

                _id = data.get("id")
                _file = file
                _name = data.get("name")
                _manufacturer = data.get("manufacturer")
                _author = data.get("author")
                _pages = data.get("add_pages")
                while _pages == None:
                    searchPath = os.path.join(dir, data.get("inherits"))
                    json_data = open(searchPath).read()
                    data = json.loads(json_data)
                    _pages = data.get("add_pages")
                _pages = self._createPagesModel(_pages)


                #makes sure that if Cura tries to load a faulty settings file, that it ignores the file and that Cura at least still loads
                if _id == None or _file == None or _name == None or _manufacturer == None:
                    continue

                #if the file is missing an author, it displays the author as "unspecified" instead of other
                if _author == None:
                    _author = "unspecified"

                if _manufacturer != "Ultimaker":
                    _machines_by_other.append([_manufacturer, _id, _file, _name, _author, _pages])

                if _manufacturer == "Ultimaker":
                     _machines_by_ultimaker.append([_id, _file, _name, _manufacturer, _author,_pages])

            for item in sorted(_machines_by_ultimaker, key = lambda item: item[2]):
                self.appendItem({ "id": item[0], "file": item[1], "name": item[2], "manufacturer": item[3], "author": item[4],"pages": item[5]})

            for item in sorted(_machines_by_other, key = lambda item: item[2]):
                self.appendItem({ "id": item[1], "file": item[2], "name": item[3], "manufacturer": item[0], "author": item[4],"pages": item[5]})
