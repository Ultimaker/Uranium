# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot

class ProfilesModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3

    def __init__(self):
        super().__init__()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")

        self._manager = Application.getInstance().getMachineManager()

        self._manager.profilesChanged.connect(self._onProfilesChanged)
        self._manager.activeProfileChanged.connect(self._onActiveProfileChanged)
        self._onProfilesChanged()

    def _onProfilesChanged(self):
        self.clear()
        profiles = self._manager.getProfiles()
        profiles.sort(key = lambda k: k.getName())
        for profile in profiles:
            self.appendItem({ "id": id(profile), "name": profile.getName(), "active": self._manager.getActiveProfile() == profile })

    def _onActiveMachineChanged(self):
        active_profile = self._manager.getActiveProfile()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(active_profile) == self.items[index]["id"])

