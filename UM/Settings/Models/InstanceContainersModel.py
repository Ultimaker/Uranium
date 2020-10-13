# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
from typing import Any, cast, Dict, Generator, List, Tuple
from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal, pyqtSlot, QUrl, QTimer

from UM.Qt.ListModel import ListModel
from UM.PluginRegistry import PluginRegistry  # For getting the possible profile readers and writers.
from UM.Settings.Interfaces import ContainerInterface #For typing.
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.InstanceContainer import InstanceContainer
from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")


class InstanceContainersModel(ListModel):
    """Model that holds instance containers. By setting the filter property the instances held by this model can be
    changed.
    """

    NameRole = Qt.UserRole + 1  # Human readable name (string)
    IdRole = Qt.UserRole + 2    # Unique ID of the InstanceContainer
    MetaDataRole = Qt.UserRole + 3
    ReadOnlyRole = Qt.UserRole + 4
    SectionRole = Qt.UserRole + 5

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.MetaDataRole, "metadata")
        self.addRoleName(self.ReadOnlyRole, "readOnly")
        self.addRoleName(self.SectionRole, "section")

        #We keep track of two sets: One for normal containers that are already fully loaded, and one for containers of which only metadata is known.
        #Both of these are indexed by their container ID.
        self._instance_containers = {} #type: Dict[str, InstanceContainer]
        self._instance_containers_metadata = {} # type: Dict[str, Dict[str, Any]]

        self._section_property = ""

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)

        self._container_change_timer = QTimer()
        self._container_change_timer.setInterval(150)
        self._container_change_timer.setSingleShot(True)
        self._container_change_timer.timeout.connect(self._update)

        # List of filters for queries. The result is the union of the each list of results.
        self._filter_dicts = []  # type: List[Dict[str, str]]
        self._container_change_timer.start()

    def _onContainerChanged(self, container: ContainerInterface) -> None:
        """Handler for container added / removed events from registry"""

        # We only need to update when the changed container is a instanceContainer
        if isinstance(container, InstanceContainer):
            self._container_change_timer.start()

    def _update(self) -> None:
        """Private convenience function to reset & repopulate the model."""

        #You can only connect on the instance containers, not on the metadata.
        #However the metadata can't be edited, so it's not needed.
        for container in self._instance_containers.values():
            container.metaDataChanged.disconnect(self._updateMetaData)

        self._instance_containers, self._instance_containers_metadata = self._fetchInstanceContainers()

        for container in self._instance_containers.values():
            container.metaDataChanged.connect(self._updateMetaData)

        new_items = list(self._recomputeItems())
        if new_items != self._items:
            self.setItems(new_items)

    def _recomputeItems(self) -> Generator[Dict[str, Any], None, None]:
        """Computes the items that need to be in this list model.

        This does not set the items in the list itself. It is intended to be
        overwritten by subclasses that add their own roles to the model.
        """

        registry = ContainerRegistry.getInstance()
        result = []
        for container in self._instance_containers.values():
            result.append({
                "name": container.getName(),
                "id": container.getId(),
                "metadata": container.getMetaData().copy(),
                "readOnly": registry.isReadOnly(container.getId()),
                "section": container.getMetaDataEntry(self._section_property, ""),
                "weight": int(container.getMetaDataEntry("weight", 0))
            })
        for container_metadata in self._instance_containers_metadata.values():
            result.append({
                "name": container_metadata["name"],
                "id": container_metadata["id"],
                "metadata": container_metadata.copy(),
                "readOnly": registry.isReadOnly(container_metadata["id"]),
                "section": container_metadata.get(self._section_property, ""),
                "weight": int(container_metadata.get("weight", 0))
            })
        yield from sorted(result, key = self._sortKey)

    def _fetchInstanceContainers(self) -> Tuple[Dict[str, InstanceContainer], Dict[str, Dict[str, Any]]]:
        """Fetch the list of containers to display.

        This method is intended to be overridable by subclasses.

        :return: A tuple of an ID-to-instance mapping that includes all fully loaded containers, and
        an ID-to-metadata mapping that includes the containers of which only the metadata is known.
        """

        registry = ContainerRegistry.getInstance() #Cache this for speed.
        containers = {} #type: Dict[str, InstanceContainer] #Mapping from container ID to container.
        metadatas = {} #type: Dict[str, Dict[str, Any]] #Mapping from container ID to metadata.
        for filter_dict in self._filter_dicts:
            this_filter = registry.findInstanceContainersMetadata(**filter_dict)
            for metadata in this_filter:
                if metadata["id"] not in containers and metadata["id"] not in metadatas: #No duplicates please.
                    if registry.isLoaded(metadata["id"]): #Only add it to the full containers if it's already fully loaded.
                        containers[metadata["id"]] = cast(InstanceContainer, registry.findContainers(id = metadata["id"])[0])
                    else:
                        metadatas[metadata["id"]] = metadata
        return containers, metadatas

    def setSectionProperty(self, property_name: str) -> None:
        if self._section_property != property_name:
            self._section_property = property_name
            self.sectionPropertyChanged.emit()
            self._container_change_timer.start()

    sectionPropertyChanged = pyqtSignal()
    @pyqtProperty(str, fset = setSectionProperty, notify = sectionPropertyChanged)
    def sectionProperty(self) -> str:
        return self._section_property

    def setFilter(self, filter_dict: Dict[str, str]) -> None:
        """Set the filter of this model based on a string.

        :param filter_dict: :type{Dict} Dictionary to do the filtering by.
        """

        self.setFilterList([filter_dict])

    filterChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", fset = setFilter, notify = filterChanged)
    def filter(self) -> Dict[str, str]:
        return self._filter_dicts[0] if len(self._filter_dicts) != 0 else {}

    def setFilterList(self, filter_list: List[Dict[str, str]]) -> None:
        """Set a list of filters to use when fetching containers.

        :param filter_list: List of filter dicts to fetch multiple sets of
        containers. The final result is the union of these sets.
        """

        if filter_list != self._filter_dicts:
            self._filter_dicts = filter_list
            self.filterChanged.emit()
            self._container_change_timer.start()

    @pyqtProperty("QVariantList", fset=setFilterList, notify=filterChanged)
    def filterList(self) -> List[Dict[str, str]]:
        return self._filter_dicts

    @pyqtSlot(str, result="QVariantList")
    def getFileNameFilters(self, io_type: str) -> List[str]:
        """Gets a list of the possible file filters that the plugins have registered they can read or write.
        The convenience meta-filters "All Supported Types" and "All Files" are added when listing readers,
        but not when listing writers.

        :param io_type: Name of the needed IO type
        :return: A list of strings indicating file name filters for a file dialog.
        """

        #TODO: This function should be in UM.Resources!
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
    def getDefaultPath(self) -> QUrl:
        return QUrl.fromLocalFile(os.path.expanduser("~/"))

    def _getIOPlugins(self, io_type: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Gets a list of profile reader or writer plugins

        :return: List of tuples of (plugin_id, meta_data).
        """

        pr = PluginRegistry.getInstance()
        active_plugin_ids = pr.getActivePlugins()

        result = []
        for plugin_id in active_plugin_ids:
            meta_data = pr.getMetaData(plugin_id)
            if io_type in meta_data:
                result.append((plugin_id, meta_data))
        return result

    def _sortKey(self, item: Dict[str, Any]) -> List[Any]:
        result = []
        if self._section_property:
            result.append(item.get(self._section_property, ""))

        result.append(not ContainerRegistry.getInstance().isReadOnly(item["id"]))
        result.append(int(item.get("weight", 0)))
        result.append(item["name"])

        return result

    def _updateMetaData(self, container: InstanceContainer) -> None:
        index = self.find("id", container.id)

        if self._section_property:
            self.setProperty(index, "section", container.getMetaDataEntry(self._section_property, ""))

        self.setProperty(index, "metadata", container.getMetaData())
        self.setProperty(index, "name", container.getName())
        self.setProperty(index, "id", container.getId())

    def _onContainerLoadComplete(self, container_id: str) -> None:
        """If a container has loaded fully (rather than just metadata) we need to
        move it from the dict of metadata to the dict of full containers.
        """

        if container_id in self._instance_containers_metadata:
            del self._instance_containers_metadata[container_id]
            self._instance_containers[container_id] = ContainerRegistry.getInstance().findContainers(id = container_id)[0]
            self._instance_containers[container_id].metaDataChanged.connect(self._updateMetaData)
