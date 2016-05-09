from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtSlot, pyqtProperty, Qt

from UM.Settings.ContainerRegistry import ContainerRegistry

##  Model that holds instance containers. By setting the filter property the instances held by this model can be
#   changed.
class InstanceContainersModel(ListModel):
    NameRole = Qt.UserRole + 1

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self._instance_containers = ContainerRegistry.getInstance().findInstanceContainers()
        self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        self.clear()
        for container in self._instance_containers:
            self.appendItem({"name": container.getName()})

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._instance_containers = ContainerRegistry.getInstance().findInstanceContainers(**filter_dict)
        self._update()

    @pyqtProperty("QVariantMap", fset = setFilter)
    def filter(self, filter):
        pass
