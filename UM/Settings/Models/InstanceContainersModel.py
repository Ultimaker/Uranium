from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtSlot, pyqtProperty, Qt

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.InstanceContainer import InstanceContainer

##  Model that holds instance containers. By setting the filter property the instances held by this model can be
#   changed.
class InstanceContainersModel(ListModel):
    NameRole = Qt.UserRole + 1

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self._instance_containers = ContainerRegistry.getInstance().findInstanceContainers()

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerAdded)
        self._filter_dict = {}
        self._update()

    ##  Handler for container added events from registry
    def _onContainerAdded(self, container):
        # We only need to update when the added container is a instanceContainer
        if isinstance(container, InstanceContainer):
            self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        self.clear()
        self._instance_containers = ContainerRegistry.getInstance().findInstanceContainers(**self._filter_dict)
        for container in self._instance_containers:
            self.appendItem({"name": container.getName()})

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._filter_dict = filter_dict
        self._update()

    @pyqtProperty("QVariantMap", fset = setFilter)
    def filter(self, filter):
        pass
