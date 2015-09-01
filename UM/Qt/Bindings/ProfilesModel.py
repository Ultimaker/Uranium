# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, pyqtProperty

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class ProfilesModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3
    ReadOnlyRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self._select_global = False

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")
        self.addRoleName(self.ReadOnlyRole, "readOnly")

        self._manager = Application.getInstance().getMachineManager()

        self._manager.profilesChanged.connect(self._onProfilesChanged)
        self._manager.activeProfileChanged.connect(self._onActiveProfileChanged)
        self._onProfilesChanged()

    selectGlobalChanged = pyqtSignal()

    def setSelectGlobal(self, select):
        if select != self._select_global:
            self._select_global = select
            self._onProfilesChanged()
            self.selectGlobalChanged.emit()

    @pyqtProperty(bool, fset = setSelectGlobal, notify = selectGlobalChanged)
    def selectGlobal(self):
        return self._select_global

    def _onProfilesChanged(self):
        self.clear()

        if self._select_global:
            self.appendItem({
                "id": 1,
                "name": catalog.i18nc("@item:inlistbox", "<Use Global Profile>"),
                "active": False,
                "readOnly": True
            })

        profiles = self._manager.getProfiles()
        profiles.sort(key = lambda k: k.getName())
        for profile in profiles:
            self.appendItem({
                "id": id(profile),
                "name": profile.getName(),
                "active": self._manager.getActiveProfile() == profile,
                "readOnly": profile.isReadOnly()
            })

    def _onActiveProfileChanged(self):
        active_profile = self._manager.getActiveProfile()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(active_profile) == self.items[index]["id"])

