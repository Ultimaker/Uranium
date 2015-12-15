# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Message import Message
from UM.Settings.Profile import Profile
from UM.Settings import SettingsError

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, pyqtProperty, QUrl

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class ProfilesModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3
    ReadOnlyRole = Qt.UserRole + 4
    ValueRole = Qt.UserRole + 5

    def __init__(self, parent = None):
        super().__init__(parent)

        self._add_use_global = False

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")
        self.addRoleName(self.ReadOnlyRole, "readOnly")
        self.addRoleName(self.ValueRole, "value")

        self._manager = Application.getInstance().getMachineManager()

        self._manager.profilesChanged.connect(self._onProfilesChanged)
        self._manager.activeProfileChanged.connect(self._onActiveProfileChanged)
        self._manager.profileNameChanged.connect(self._onProfileNameChanged)
        self._onProfilesChanged()

    addUseGlobalChanged = pyqtSignal()

    def setAddUseGlobal(self, add):
        if add != self._add_use_global:
            self._add_use_global = add
            self._onProfilesChanged()
            self.addUseGlobalChanged.emit()

    ##  Whether to add a "Use Global Profile" entry.
    @pyqtProperty(bool, fset = setAddUseGlobal, notify = addUseGlobalChanged)
    def addUseGlobal(self):
        return self._add_use_global

    @pyqtSlot(str)
    def removeProfile(self, name):
        profile = self._manager.findProfile(name)
        if not profile:
            return

        self._manager.removeProfile(profile)

    @pyqtSlot(str, str)
    def renameProfile(self, old_name, new_name):
        profile = self._manager.findProfile(old_name)
        if not profile:
            return

        profile.setName(new_name)

    @pyqtSlot(str, result = bool)
    def checkProfileExists(self, name):
        profile = self._manager.findProfile(name)
        if profile:
            return True

        return False

    @pyqtSlot(QUrl, result="QVariantMap")
    def importProfile(self, url):
        path = url.toLocalFile()
        if not path:
            return

        for profile_reader in self._manager.getProfileReaders():
            try:
                profile = profile_reader.read(path) #Try to open the file with the profile reader.
            except Exception as e:
                #Note that this will fail quickly. That is, if any profile reader throws an exception, it will stop reading. It will only continue reading if the reader returned None.
                return { "status": "error", "message": catalog.i18nc("@info:status", "Failed to import profile from file <filename>{0}</filename>: <message>{1}</message>", path, str(e)) }
            if profile: #Success!
                profile.setReadOnly(False)
                try:
                    self._manager.addProfile(profile) #Add the new profile to the list of profiles.
                except SettingsError.DuplicateProfileError as e:
                    count = 2
                    name = "{0} {1}".format(profile.getName(), count) #Try alternative profile names with a number appended to them.
                    while self._manager.findProfile(name) != None:
                        count += 1
                        name = "{0} {1}".format(profile.getName(), count)
                    profile.setName(name)
                    self._manager.addProfile(profile)
                    return { "status": "duplicate", "message": catalog.i18nc("@info:status", "Profile was imported as {0}", name) }
                else:
                    return { "status": "ok", "message": catalog.i18nc("@info:status", "Successfully imported profile {0}", profile.getName()) }

        #If it hasn't returned by now, none of the plugins loaded the profile successfully.
        return { "status": "error", "message": catalog.i18nc("@info:status", "Profile {0} has an unknown file type.", path) }

    @pyqtSlot(str, QUrl)
    def exportProfile(self, name, url):
        path = url.toLocalFile()
        if not path:
            return

        profile = self._manager.findProfile(name)
        if not profile:
            return

        error = ""
        try:
            error = profile.saveToFile(path)
        except Exception as e:
            error = str(e)

        if error:
            m = Message(catalog.i18nc("@info:status", "Failed to export profile to <filename>{0}</filename>: <message>{1}</message>", path, error))
            m.show()
        else:
            m = Message(catalog.i18nc("@info:status", "Exported profile to <filename>{0}</filename>", path))
            m.show()

    ##  Gets a list of the possible file filters that the plugins have
    #   registered they can open.
    #
    #   \return A list of strings indicating file name filters for a file
    #   dialog.
    @pyqtSlot(result = "QVariantList")
    def getFileNameFiltersRead(self):
        filters = []
        for extension,description in self._manager.getProfileSupportedFileTypesRead().items(): #Format the file types that can be read correctly for the open file dialog.
            filters.append(description + " (*." + extension + ")")
        filters.append(catalog.i18nc("@item:inlistbox", "All Files (*)")) #Also allow arbitrary files, if the user so prefers.
        return filters

    def _onProfilesChanged(self):
        self.clear()

        if self._add_use_global:
            self.appendItem({
                "id": 1,
                "name": catalog.i18nc("@item:inlistbox", "- Use Global Profile -"),
                "active": False,
                "readOnly": True,
                "value": "global"
            })

        profiles = self._manager.getProfiles()
        profiles.sort(key = lambda k: k.getName())
        for profile in profiles:
            self.appendItem({
                "id": id(profile),
                "name": profile.getName(),
                "active": self._manager.getActiveProfile() == profile,
                "readOnly": profile.isReadOnly(),
                "value": profile.getName()
            })

    def _onActiveProfileChanged(self):
        active_profile = self._manager.getActiveProfile()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(active_profile) == self.items[index]["id"])

    def _onProfileNameChanged(self, profile):
        index = self.find("id", id(profile))
        if index != -1:
            self.setProperty(index, "name", profile.getName())
