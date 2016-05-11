from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtSlot, pyqtProperty, Qt

from UM.Settings.ContainerRegistry import ContainerRegistry

##  Model that holds container stacks. By setting the filter property the stacks held by this model can be
#   changed.
class ContainerStacksModel(ListModel):
    NameRole = Qt.UserRole + 1
    IdRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self._container_stacks = ContainerRegistry.getInstance().findContainerStacks()
        self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        self.clear()
        for container in self._container_stacks:
            self.appendItem({"name": container.getName(),
                             "id": container.getId()})

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._container_stacks = ContainerRegistry.getInstance().findContainerStacks(**filter_dict)
        self._update()

    @pyqtProperty("QVariantMap", fset = setFilter)
    def filter(self, filter):
        pass