# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.DefinitionContainer import DefinitionContainer
from typing import Dict


class DefinitionContainersModel(ListModel):
    """Model that holds definition containers. By setting the filter property the definitions held by this model can be
    changed.
    """

    NameRole = Qt.UserRole + 1          # Human readable name (string)
    IdRole = Qt.UserRole + 2            # Unique ID of Definition
    SectionRole = Qt.UserRole + 3       # Section of definition / machine. (string)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.SectionRole, "section")

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)

        self._section_property = ""

        #Preference for which sections should be shown on top. Weights for each section.
        #Sections with the lowest value are shown on top. Sections not on this
        #list will get a value of 0.
        self._preferred_sections = {} #type: Dict[str, int]

        self._filter_dict = {}
        self._update()

    def _onContainerChanged(self, container):
        """Handler for container change events from registry"""

        # We only need to update when the changed container is a DefinitionContainer.
        if isinstance(container, DefinitionContainer):
            self._update()

    def _update(self) -> None:
        """Private convenience function to reset & repopulate the model."""

        items = []
        definition_containers = ContainerRegistry.getInstance().findDefinitionContainersMetadata(**self._filter_dict)
        definition_containers.sort(key = self._sortKey)

        for metadata in definition_containers:
            metadata = dict(metadata) # For fully loaded definitions, the metadata is an OrderedDict which does not pass to QML correctly

            items.append({
                "name": metadata["name"],
                "id": metadata["id"],
                "metadata": metadata,
                "section": metadata.get(self._section_property, ""),
            })
        self.setItems(items)

    def setSectionProperty(self, property_name):
        if self._section_property != property_name:
            self._section_property = property_name
            self.sectionPropertyChanged.emit()
            self._update()

    sectionPropertyChanged = pyqtSignal()
    @pyqtProperty(str, fset = setSectionProperty, notify = sectionPropertyChanged)
    def sectionProperty(self):
        return self._section_property

    def setPreferredSections(self, weights: Dict[str, int]):
        if self._preferred_sections != weights:
            self._preferred_sections = weights
            self.preferredSectionsChanged.emit()
            self._update()

    preferredSectionsChanged = pyqtSignal()

    @pyqtProperty("QVariantMap", fset = setPreferredSections, notify = preferredSectionsChanged)
    def preferredSections(self):
        return self._preferred_sections

    def setFilter(self, filter_dict):
        """Set the filter of this model based on a string.
        :param filter_dict: Dictionary to do the filtering by.
        """

        self._filter_dict = filter_dict
        self._update()

    filterChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", fset = setFilter, notify = filterChanged)
    def filter(self):
        return self._filter_dict

    def _sortKey(self, item):
        result = []

        if self._section_property:
            section_value = item.get(self._section_property, "")
            section_weight = self._preferred_sections.get(section_value, 0)
            result.append(section_weight)
            result.append(section_value.lower())

        result.append(int(item.get("weight", 0))) #Weight within a section.
        result.append(item["name"].lower())

        return result

    def _updateMetaData(self, container):
        index = self.find("id", container.id)

        if self._section_property:
            self.setProperty(index, "section", container.getMetaDataEntry(self._section_property, ""))

        self.setProperty(index, "metadata", container.getMetaData())