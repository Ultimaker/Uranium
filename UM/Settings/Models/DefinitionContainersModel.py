from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtSlot, pyqtProperty, Qt

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.ContainerStack import ContainerStack
from UM.Application import Application

##  Model that holds definition containers. By setting the filter property the definitions held by this model can be
#   changed.
class DefinitionContainersModel(ListModel):
    NameRole = Qt.UserRole + 1
    ManufacturerRole = Qt.UserRole + 2
    IdRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ManufacturerRole, "manufacturer")
        self.addRoleName(self.IdRole, "id")
        self._definition_containers = ContainerRegistry.getInstance().findDefinitionContainers()
        self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        self.clear()
        for container in self._definition_containers:
            self.appendItem({"name": container.getName(),
                             "manufacturer": container.getMetaDataEntry("manufacturer", ""),
                             "id": container.getId()})

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._definition_containers = ContainerRegistry.getInstance().findDefinitionContainers(**filter_dict)
        self._update()

    @pyqtProperty("QVariantMap", fset = setFilter)
    def filter(self, filter):
        pass

    ##  Convenience function. Creates a new stack with definition and sets it as global.
    @pyqtSlot(str, str)
    def setNewGlobalStackFromDefinition(self, name, definition_id):
        definitions = ContainerRegistry.getInstance().findDefinitionContainers(id = definition_id)
        if definitions:
            new_global_stack = ContainerStack(name)
            ContainerRegistry.getInstance().addContainer(new_global_stack)
            # If a definition is found, its a list. Should only have one item.
            new_global_stack.addContainer(definitions[0])
            Application.getInstance().setGlobalContainerStack(new_global_stack)
        pass