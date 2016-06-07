from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal, pyqtSlot

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.InstanceContainer import InstanceContainer


##  Model that holds instance containers. By setting the filter property the instances held by this model can be
#   changed.
class InstanceContainersModel(ListModel):
    NameRole = Qt.UserRole + 1  # Human readable name (string)
    IdRole = Qt.UserRole + 2    # Unique ID of Definition
    MetaDataRole = Qt.UserRole + 3
    SettingsRole = Qt.UserRole + 4

    LabelRole = Qt.UserRole + 5
    ValueRole = Qt.UserRole + 6
    UnitRole = Qt.UserRole + 7
    CategoryRole = Qt.UserRole + 8

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.MetaDataRole, "metadata")
        self.addRoleName(self.SettingsRole, "settings")

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
        self.clear()
        self._instance_containers = ContainerRegistry.getInstance().findInstanceContainers(**self._filter_dict)
        self._instance_containers.sort(key = lambda k: (0 if k.getMetaDataEntry("read_only") else 1, int(k.getMetaDataEntry("weight")) if k.getMetaDataEntry("weight") else 0, k.getName()))

        for container in self._instance_containers:
            settings = ListModel()
            settings.addRoleName(self.LabelRole, "label")
            settings.addRoleName(self.ValueRole, "value")
            settings.addRoleName(self.UnitRole, "unit")
            settings.addRoleName(self.CategoryRole, "category")

            container_keys = list(container.getAllKeys())
            container_keys.sort()

            for key in container_keys:
                category = container.getInstance(key).definition
                while category.type != "category":
                    category = category.parent

                settings.appendItem({
                    "key": key,
                    "value": container.getProperty(key, "value"),
                    "label": container.getInstance(key).definition.label,
                    "unit": container.getInstance(key).definition.unit,
                    "category": category.label
                })

            self.appendItem({
                "name": container.getName(),
                "id": container.getId(),
                "metadata": container.getMetaData(),
                "settings": settings
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
