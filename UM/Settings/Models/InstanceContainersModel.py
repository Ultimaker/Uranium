# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import os
from typing import Dict, List

from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal, pyqtSlot, QUrl, QTimer

from UM.Qt.ListModel import ListModel

from UM.PluginRegistry import PluginRegistry  # For getting the possible profile readers and writers.
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Logger import Logger
from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")


##  Model that holds instance containers. By setting the filter property the instances held by this model can be
#   changed.
class InstanceContainersModel(ListModel):
    NameRole = Qt.UserRole + 1  # Human readable name (string)
    IdRole = Qt.UserRole + 2    # Unique ID of the InstanceContainer
    MetaDataRole = Qt.UserRole + 3
    ReadOnlyRole = Qt.UserRole + 4
    SectionRole = Qt.UserRole + 5

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.MetaDataRole, "metadata")
        self.addRoleName(self.ReadOnlyRole, "readOnly")
        self.addRoleName(self.SectionRole, "section")

        self._instance_containers = []

        self._section_property = ""

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)

        self._container_change_timer = QTimer()
        self._container_change_timer.setInterval(150)
        self._container_change_timer.setSingleShot(True)
        self._container_change_timer.timeout.connect(self._update)


        # List of filters for queries. The result is the union of the each list of results.
        self._filter_dicts = [{}]  # type: List[Dict[str,str]]
        self._update()

    ##  Handler for container added / removed events from registry
    def _onContainerChanged(self, container):
        # We only need to update when the changed container is a instanceContainer
        if isinstance(container, InstanceContainer):
            self._container_change_timer.start()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        for container in self._instance_containers:
            container.nameChanged.disconnect(self._update)
            container.metaDataChanged.disconnect(self._updateMetaData)

        self._instance_containers = self._fetchInstanceContainers()

        for container in self._instance_containers:
            container.nameChanged.connect(self._update)
            container.metaDataChanged.connect(self._updateMetaData)
        try:
            self._instance_containers.sort(key=self._sortKey)
        except TypeError:
            Logger.logException("w", "Sorting the InstanceContainers model went wrong.")

        self.setItems(list(self._recomputeItems()))

    ##  Computes the items that need to be in this list model.
    #
    #   This does not set the items in the list itself. It is intended to be
    #   overwritten by subclasses that add their own roles to the model.
    def _recomputeItems(self):
        for container in self._instance_containers:
            metadata = container.getMetaData().copy()
            metadata["has_settings"] = len(container.getAllKeys()) > 0

            yield {
                "name": container.getName(),
                "id": container.getId(),
                "metadata": metadata,
                "readOnly": container.isReadOnly(),
                "section": container.getMetaDataEntry(self._section_property, "")
            }

    ##  Fetch the list of containers to display.
    #
    #   This method is intended to be overridable by subclasses.
    #
    #   \return \type{List[ContainerInstance]}
    def _fetchInstanceContainers(self):
        # Perform each query and assemble the union of all the results.
        results = set()
        for filter_dict in self._filter_dicts:
            results.update(ContainerRegistry.getInstance().findInstanceContainers(**filter_dict))
        return list(results)

    def setSectionProperty(self, property_name):
        if self._section_property != property_name:
            self._section_property = property_name
            self.sectionPropertyChanged.emit()
            self._update()

    sectionPropertyChanged = pyqtSignal()
    @pyqtProperty(str, fset = setSectionProperty, notify = sectionPropertyChanged)
    def sectionProperty(self):
        return self._section_property

    ##  Set the filter of this model based on a string.
    #   \param filter_dict \type{Dict} Dictionary to do the filtering by.
    def setFilter(self, filter_dict: Dict[str, str]) -> None:
        self.setFilterList([filter_dict])

    filterChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", fset = setFilter, notify = filterChanged)
    def filter(self) -> Dict[str, str]:
        return self._filter_dicts[0] if len(self._filter_dicts) !=0 else None

    ##  Set a list of filters to use when fetching containers.
    #
    #   \param filter_list \type{List[Dict]} List of filter dicts to fetch multiple
    #               sets of containers. The final result is the union of these sets.
    def setFilterList(self, filter_list):
        if filter_list != self._filter_dicts:
            self._filter_dicts = filter_list
            self.filterChanged.emit()
            self._update()

    @pyqtProperty("QVariantList", fset=setFilterList, notify=filterChanged)
    def filterList(self):
        return self._filter_dicts

    @pyqtSlot(str, str)
    def rename(self, instance_id, new_name):
        if new_name != self.getName():
            containers = ContainerRegistry.getInstance().findInstanceContainers(id = instance_id)
            if containers:
                containers[0].setName(new_name)
                self._update()

    ##  Gets a list of the possible file filters that the plugins have
    #   registered they can read or write. The convenience meta-filters
    #   "All Supported Types" and "All Files" are added when listing
    #   readers, but not when listing writers.
    #
    #   \param io_type \type{str} name of the needed IO type
    #   \return A list of strings indicating file name filters for a file
    #   dialog.
    @pyqtSlot(str, result="QVariantList")
    def getFileNameFilters(self, io_type):
        filters = []
        all_types = []
        for plugin_id, meta_data in self._getIOPlugins(io_type):
            for io_plugin in meta_data[io_type]:
                filters.append(io_plugin["description"] + " (*." + io_plugin["extension"] + ")")
                all_types.append("*.{0}".format(io_plugin["extension"]))

        if "_reader" in io_type:
            # if we're listing readers, add the option to show all supported files as the default option
            filters.insert(0,
                catalog.i18nc("@item:inlistbox", "All Supported Types ({0})", " ".join(all_types)))

            filters.append(
                catalog.i18nc("@item:inlistbox", "All Files (*)"))  # Also allow arbitrary files, if the user so prefers.
        return filters

    @pyqtSlot(result=QUrl)
    def getDefaultPath(self):
        return QUrl.fromLocalFile(os.path.expanduser("~/"))

    ##  Gets a list of profile reader or writer plugins
    #   \return List of tuples of (plugin_id, meta_data).
    def _getIOPlugins(self, io_type):
        pr = PluginRegistry.getInstance()
        active_plugin_ids = pr.getActivePlugins()

        result = []
        for plugin_id in active_plugin_ids:
            meta_data = pr.getMetaData(plugin_id)
            if io_type in meta_data:
                result.append( (plugin_id, meta_data) )
        return result

    @pyqtSlot("QVariantList", QUrl, str)
    def exportProfile(self, instance_id, file_url, file_type):
        if not file_url.isValid():
            return
        path = file_url.toLocalFile()
        if not path:
            return
        ContainerRegistry.getInstance().exportProfile(instance_id, path, file_type)

    @pyqtSlot(QUrl, result="QVariantMap")
    def importProfile(self, file_url):
        if not file_url.isValid():
            return
        path = file_url.toLocalFile()
        if not path:
            return
        return ContainerRegistry.getInstance().importProfile(path)

    def _sortKey(self, item):
        result = []
        if self._section_property:
            result.append(item.getMetaDataEntry(self._section_property, ""))

        result.append(not item.isReadOnly())
        result.append(int(item.getMetaDataEntry("weight", 0)))
        result.append(item.getName())

        return result

    def _updateMetaData(self, container):
        index = self.find("id", container.id)

        if self._section_property:
            self.setProperty(index, "section", container.getMetaDataEntry(self._section_property, ""))

        self.setProperty(index, "metadata", container.getMetaData())
