# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message
from UM.PluginRegistry import PluginRegistry #For getting the possible profile writers to write with.
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
    SettingsRole = Qt.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)

        self._add_use_global = False

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")
        self.addRoleName(self.ReadOnlyRole, "readOnly")
        self.addRoleName(self.ValueRole, "value")
        self.addRoleName(self.SettingsRole, "settings")

        self._manager = Application.getInstance().getMachineManager()

        self._manager.profilesChanged.connect(self._onProfilesChanged)
        self._manager.activeMachineInstanceChanged.connect(self._onMachineInstanceChanged)
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

        for profile_reader_id, profile_reader in self._manager.getProfileReaders():
            try:
                profile = profile_reader.read(path) #Try to open the file with the profile reader.
            except Exception as e:
                #Note that this will fail quickly. That is, if any profile reader throws an exception, it will stop reading. It will only continue reading if the reader returned None.
                Logger.log("e", "Failed to import profile from %s: %s", path, str(e))
                return { "status": "error", "message": catalog.i18nc("@info:status", "Failed to import profile from <filename>{0}</filename>: <message>{1}</message>", path, str(e)) }
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

    @pyqtSlot(str, QUrl, str)
    def exportProfile(self, name, url, fileType):
        #Input checking.
        path = url.toLocalFile()
        if not path:
            return

        profile = self._manager.findProfile(name)
        if not profile:
            return

        #Parse the fileType to deduce what plugin can save the file format.
        #TODO: This parsing can be made unnecessary by storing for each plugin what the fileType string is in complete (in addition to the {(description,extension)} dict).
        #fileType has the format "<description> (*.<extension>)"
        split = fileType.rfind(" (*.") #Find where the description ends and the extension starts.
        if split < 0: #Not found. Invalid format.
            Logger.log("e", "Invalid file format identifier %s", fileType)
            return
        description = fileType[:split]
        extension = fileType[split + 4:-1] #Leave out the " (*." and ")".
        if not path.endswith("." + extension): #Auto-fill the extension if the user did not provide any.
            path += "." + extension

        good_profile_writer = None
        for profile_writer_id, profile_writer in self._manager.getProfileWriters(): #Find which profile writer can write this file type.
            meta_data = PluginRegistry.getInstance().getMetaData(profile_writer_id)
            if "profile_writer" in meta_data:
                for supported_type in meta_data["profile_writer"]: #All file types this plugin can supposedly write.
                    supported_extension = supported_type.get("extension", None)
                    if supported_extension == extension: #This plugin supports a file type with the same extension.
                        supported_description = supported_type.get("description", None)
                        if supported_description == description: #The description is also identical. Assume it's the same file type.
                            good_profile_writer = profile_writer
                            break
            if good_profile_writer: #If we found a writer in this iteration, break the loop.
                break

        success = False
        try:
            success = good_profile_writer.write(path, profile)
        except Exception as e:
            Logger.log("e", "Failed to export profile to %s: %s", path, str(e))
            m = Message(catalog.i18nc("@info:status", "Failed to export profile to <filename>{0}</filename>: <message>{1}</message>", path, str(e)))
            m.show()
            return
        if not success:
            Logger.log("w", "Failed to export profile to %s: Writer plugin reported failure.", path)
            m = Message(catalog.i18nc("@info:status", "Failed to export profile to <filename>{0}</filename>: Writer plugin reported failure.", path))
            m.show()
            return
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
        all_supported = []
        for extension, description in self._manager.getSupportedProfileTypesRead().items(): #Format the file types that can be read correctly for the open file dialog.
            all_supported.append("*." + extension)
            filters.append(description + " (*." + extension + ")")
        filters.insert(0, catalog.i18nc("@item:inlistbox", "All supported files") + "(" + " ".join(all_supported) + ")") #An entry to show all file extensions that are supported.
        filters.append(catalog.i18nc("@item:inlistbox", "All Files (*)")) #Also allow arbitrary files, if the user so prefers.
        return filters
    
    ##  Gets a list of the possible file filters that the plugins have
    #   registered they can write.
    #
    #   \return A list of strings indicating file name filters for a file
    #   dialog.
    @pyqtSlot(result = "QVariantList")
    def getFileNameFiltersWrite(self):
        filters = []
        for extension, description in self._manager.getSupportedProfileTypesWrite().items(): #Format the file types that can be written correctly for the save file dialog.
            filters.append(description + " (*." + extension + ")")
        filters.append(catalog.i18nc("@item:inlistbox", "All Files (*)")) #Also allow arbitrary files, if the user so prefers.
        return filters

    def _onMachineInstanceChanged(self):
        self._onProfilesChanged()

        #Restore active profile for this machine_instance.
        active_profile = None
        active_instance_name = self._manager.getActiveMachineInstance().getActiveProfileName()
        #We can't use findProfile(active_instance_name) because there may be multiple profiles with the same name on different machine instances.
        profiles = self._manager.getProfiles()
        for profile in profiles:
            if profile.getName() == active_instance_name:
                active_profile = profile
                break

        self._manager.setActiveProfile(active_profile)

    def _onProfilesChanged(self):
        self.clear()

        if self._add_use_global:
            self.appendItem({
                "id": 1,
                "name": catalog.i18nc("@item:inlistbox", "- Use Global Profile -"),
                "active": False,
                "readOnly": True,
                "value": "global",
                "settings": None
            })

        profiles = self._manager.getProfiles()
        profiles.sort(key = lambda k: k.getName())
        for profile in profiles:
            settings_dict = profile.getChangedSettings()
            settings_list = []
            for key, value in settings_dict.items():
                setting = self._manager.getActiveMachineInstance().getMachineDefinition().getSetting(key)
                settings_list.append({"name": setting.getLabel(), "value": value})

            self.appendItem({
                "id": id(profile),
                "name": profile.getName(),
                "active": self._manager.getActiveProfile() == profile,
                "readOnly": profile.isReadOnly(),
                "value": profile.getName(),
                "settings": settings_list
            })

    def _onActiveProfileChanged(self):
        active_profile = self._manager.getActiveProfile()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(active_profile) == self.items[index]["id"])

    def _onProfileNameChanged(self, profile):
        index = self.find("id", id(profile))
        if index != -1:
            self.setProperty(index, "name", profile.getName())
