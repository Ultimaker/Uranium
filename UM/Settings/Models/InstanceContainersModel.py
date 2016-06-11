from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtWidgets import QMessageBox

from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message
from UM.Platform import Platform
from UM.PluginRegistry import PluginRegistry #For getting the possible profile writers to write with.
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Util import parseBool

import os

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

##  Model that holds instance containers. By setting the filter property the instances held by this model can be
#   changed.
class InstanceContainersModel(ListModel):
    NameRole = Qt.UserRole + 1  # Human readable name (string)
    IdRole = Qt.UserRole + 2    # Unique ID of Definition
    MetaDataRole = Qt.UserRole + 3
    ReadOnlyRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.MetaDataRole, "metadata")
        self.addRoleName(self.ReadOnlyRole, "readOnly")

        self._instance_containers = []

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)

        self._filter_dict = {}
        self._update()

    ##  Handler for container added / removed events from registry
    def _onContainerChanged(self, container):
        # We only need to update when the changed container is a instanceContainer
        if isinstance(container, InstanceContainer):
            self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        for container in self._instance_containers:
            container.nameChanged.disconnect(self._update)

        self.clear()
        self._instance_containers = ContainerRegistry.getInstance().findInstanceContainers(**self._filter_dict)
        self._instance_containers.sort(key = lambda k: (0 if k.isReadOnly() else 1, int(k.getMetaDataEntry("weight")) if k.getMetaDataEntry("weight") else 0, k.getName()))

        for container in self._instance_containers:
            container.nameChanged.connect(self._update)

            metadata = container.getMetaData().copy()
            metadata["has_settings"] = len(container.getAllKeys()) > 0

            self.appendItem({
                "name": container.getName(),
                "id": container.getId(),
                "metadata": metadata,
                "readOnly": container.isReadOnly()
            })

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._filter_dict = filter_dict
        self._update()

    filterChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", fset = setFilter, notify = filterChanged)
    def filter(self):
        return self._filter_dict

    @pyqtSlot(str, str)
    def rename(self, instance_id, new_name):
        containers = ContainerRegistry.getInstance().findInstanceContainers(id = instance_id)
        if containers:
            containers[0].setName(new_name)
            self._update()

    @pyqtSlot(str, QUrl, str)
    def exportProfile(self, instance_id, fileUrl, fileType):
        Logger.log('d', 'exportProfile instance_id: '+str(instance_id))
        if not fileUrl.isValid():
            return
        path = fileUrl.toLocalFile()
        if not path:
            return

        # Parse the fileType to deduce what plugin can save the file format.
        # fileType has the format "<description> (*.<extension>)"
        split = fileType.rfind(" (*.")  # Find where the description ends and the extension starts.
        if split < 0:  # Not found. Invalid format.
            Logger.log("e", "Invalid file format identifier %s", fileType)
            return
        description = fileType[:split]
        extension = fileType[split + 4:-1]  # Leave out the " (*." and ")".
        if not path.endswith("." + extension):  # Auto-fill the extension if the user did not provide any.
            path += "." + extension

        # On Windows, QML FileDialog properly asks for overwrite confirm, but not on other platforms, so handle those ourself.
        if not Platform.isWindows():
            if os.path.exists(path):
                result = QMessageBox.question(None, catalog.i18nc("@title:window", "File Already Exists"),
                                              catalog.i18nc("@label", "The file <filename>{0}</filename> already exists. Are you sure you want to overwrite it?").format(path))
                if result == QMessageBox.No:
                    return

        containers = ContainerRegistry.getInstance().findInstanceContainers(id=instance_id)
        if not containers:
            return
        container = containers[0]

        profile_writer = self._findProfileWriter(extension, description)

        try:
            success = profile_writer.write(path, container)
        except Exception as e:
            Logger.log("e", "Failed to export profile to %s: %s", path, str(e))
            m = Message(catalog.i18nc("@info:status", "Failed to export profile to <filename>{0}</filename>: <message>{1}</message>", path, str(e)), lifetime = 0)
            m.show()
            return
        if not success:
            Logger.log("w", "Failed to export profile to %s: Writer plugin reported failure.", path)
            m = Message(catalog.i18nc("@info:status", "Failed to export profile to <filename>{0}</filename>: Writer plugin reported failure.", path), lifetime = 0)
            m.show()
            return
        m = Message(catalog.i18nc("@info:status", "Exported profile to <filename>{0}</filename>", path))
        m.show()

    ##  Gets the plugin object matching the criteria
    #   \param extension
    #   \param description
    #   \return The plugin object matching the given extension and description.
    def _findProfileWriter(self, extension, description):
        pr = PluginRegistry.getInstance()
        for plugin_id, meta_data in self._getProfileIOPlugins("profile_writer"):
            for supported_type in meta_data["profile_writer"]:  # All file types this plugin can supposedly write.
                supported_extension = supported_type.get("extension", None)
                if supported_extension == extension:  # This plugin supports a file type with the same extension.
                    supported_description = supported_type.get("description", None)
                    if supported_description == description:  # The description is also identical. Assume it's the same file type.
                        return pr.getPluginObject(plugin_id)
        return None

    ##  Gets a list of the possible file filters that the plugins have
    #   registered they can write.
    #
    #   \return A list of strings indicating file name filters for a file
    #   dialog.
    @pyqtSlot(result="QVariantList")
    def getFileNameFiltersWrite(self):
        return self._getFileNameFilters("profile_writer")

    @pyqtSlot(result="QVariantList")
    def getFileNameFiltersRead(self):
        return self._getFileNameFilters("profile_reader")

    def _getFileNameFilters(self, profile_io_type):
        filters = []
        for plugin_id, meta_data in self._getProfileIOPlugins(profile_io_type):
            for writer in meta_data[profile_io_type]:
                filters.append(writer["description"] + " (*." + writer["extension"] + ")")

        filters.append(
            catalog.i18nc("@item:inlistbox", "All Files (*)"))  # Also allow arbitrary files, if the user so prefers.
        return filters

    @pyqtSlot(QUrl, result="QVariantMap")
    def importProfile(self, url):
        path = url.toLocalFile()
        if not path:
            return { "status": "error", "message": catalog.i18nc("@info:status", "Failed to import profile from <filename>{0}</filename>: <message>{1}</message>", path, "Invalid path") }

        pr = PluginRegistry.getInstance()
        for plugin_id, meta_data in self._getProfileIOPlugins("profile_reader"):
            profile_reader = pr.getPluginObject(plugin_id)
            try:
                profile = profile_reader.read(path) #Try to open the file with the profile reader.
            except Exception as e:
                #Note that this will fail quickly. That is, if any profile reader throws an exception, it will stop reading. It will only continue reading if the reader returned None.
                Logger.log("e", "Failed to import profile from %s: %s", path, str(e))
                return { "status": "error", "message": catalog.i18nc("@info:status", "Failed to import profile from <filename>{0}</filename>: <message>{1}</message>", path, str(e)) }
            if profile: #Success!
                profile.setReadOnly(False)

                if self._filterQualityByMachine():
                    profile.setDefinition(self._activeDefinition())
                    if self._hasMaterials():
                        profile.addMetaDataEntry("material", self._activeMaterialId())
                else:
                    profile.setDefinition(ContainerRegistry.getInstance().findDefinitionContainers(id="fdmprinter")[0])
                ContainerRegistry.getInstance().addContainer(profile)

                return { "status": "ok", "message": catalog.i18nc("@info:status", "Successfully imported profile {0}", profile.getName()) }

        #If it hasn't returned by now, none of the plugins loaded the profile successfully.
        return { "status": "error", "message": catalog.i18nc("@info:status", "Profile {0} has an unknown file type.", path) }

    @pyqtSlot(result=QUrl)
    def getDefaultPath(self):
        return QUrl.fromLocalFile(os.path.expanduser("~/"))

    ##  Gets a list of profile writer plugins
    #   \return List of tuples of (plugin_id, meta_data).
    def _getProfileIOPlugins(self, profile_io_type):
        pr = PluginRegistry.getInstance()
        active_plugin_ids = pr.getActivePlugins()

        result = []
        for plugin_id in active_plugin_ids:
            meta_data = pr.getMetaData(plugin_id)
            if profile_io_type in meta_data:
                result.append( (plugin_id, meta_data) )
        return result

    def _filterQualityByMachine(self):
        global_container_stack = Application.getInstance().getGlobalContainerStack()
        if global_container_stack:
            return bool(global_container_stack.getMetaDataEntry("has_machine_quality", False))
        return False

    def _activeDefinition(self):
        global_container_stack = Application.getInstance().getGlobalContainerStack()
        if global_container_stack:
            definition = global_container_stack.getBottom()
            if definition:
                return definition
        return None

    def _hasMaterials(self):
        global_container_stack = Application.getInstance().getGlobalContainerStack()
        if global_container_stack:
            return global_container_stack.getMetaDataEntry("has_materials", False)
        return False

    def _activeMaterialId(self):
        global_container_stack = Application.getInstance().getGlobalContainerStack()
        if global_container_stack:
            material = global_container_stack.findContainer({"type": "material"})
            if material:
                return material.getId()
        return ""
