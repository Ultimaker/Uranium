from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.DefinitionContainer import DefinitionContainer


##  Model that holds definition containers. By setting the filter property the definitions held by this model can be
#   changed.
class DefinitionContainersModel(ListModel):
    NameRole = Qt.UserRole + 1          # Human readable name (string)
    IdRole = Qt.UserRole + 2            # Unique ID of Definition
    SectionRole = Qt.UserRole + 3       # Section of definition / machine. (string)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.SectionRole, "section")

        self._definition_containers = []

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)

        self._section_property = ""
        self._preferred_section_value = ""

        self._filter_dict = {}
        self._update()

    ##  Handler for container change events from registry
    def _onContainerChanged(self, container):
        # We only need to update when the changed container is a DefinitionContainer.
        if isinstance(container, DefinitionContainer):
            self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        items = []
        self._definition_containers = ContainerRegistry.getInstance().findDefinitionContainers(**self._filter_dict)
        self._definition_containers.sort(key = self._sortKey)

        for container in self._definition_containers:
            metadata = container.getMetaData().copy()

            items.append({
                "name": container.getName(),
                "id": container.getId(),
                "metadata": metadata,
                "section": container.getMetaDataEntry(self._section_property, ""),
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

    def setPreferredSectionValue(self, value):
        if self._preferred_section_value != value:
            self._preferred_section_value = value
            self.preferredSectionValueChanged.emit()
            self._update()

    preferredSectionValueChanged = pyqtSignal()
    @pyqtProperty(str, fset = setPreferredSectionValue, notify = preferredSectionValueChanged)
    def preferredSectionValue(self):
        return self._preferred_section_value

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._filter_dict = filter_dict
        self._update()

    filterChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", fset = setFilter, notify = filterChanged)
    def filter(self):
        return self._filter_dict

    def _sortKey(self, item):
        result = []

        if self._section_property:
            section_value = item.getMetaDataEntry(self._section_property, "")
            if self._preferred_section_value:
                result.append(section_value != self._preferred_section_value)
            result.append(section_value)

        result.append(int(item.getMetaDataEntry("weight", 0)))
        result.append(item.getName())

        return result

    def _updateMetaData(self, container):
        index = self.find("id", container.id)

        if self._section_property:
            self.setProperty(index, "section", container.getMetaDataEntry(self._section_property, ""))

        self.setProperty(index, "metadata", container.getMetaData())