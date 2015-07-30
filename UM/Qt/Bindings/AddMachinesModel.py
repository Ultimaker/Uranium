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

class AddMachinesModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    PagesRole = Qt.UserRole + 3
    FileRole = Qt.UserRole + 4


    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.PagesRole, "pages")
        self.addRoleName(self.PagesRole, "file")


        self._updateModel()

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

                if not data.get("id"):
                    #the base model (fdmprinter.json) has no id, but also doesn't represent a real printer profile, so we dump it
                    continue

                _file = file
                _id = data.get("id")
                _name = data.get("name")
                _pages = data.get("add_pages")
                while _pages == None:
                    searchPath = os.path.join(dir, data.get("inherits"))
                    json_data = open(searchPath).read()
                    data = json.loads(json_data)
                    _pages = data.get("add_pages")
                _pages = self._createPagesModel(_pages)

                self.appendItem({ "id": _id, "name": _name, "pages": _pages, "file": _file})