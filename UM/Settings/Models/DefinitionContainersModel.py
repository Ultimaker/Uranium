from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtSlot, pyqtProperty

from UM.Settings.ContainerRegistry import ContainerRegistry

##  Model that holds definition containers. By setting the filter property the definitions held by this model can be
#   changed.
class DefinitionContainersModel(ListModel):
    NameRole = Qt.UserRole + 1

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self._definition_containers = ContainerRegistry.getInstance().findDefinitionContainers()
        self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        self.clear()
        for container in self._definition_containers:
            self.appendItem({"name": container.getName()})

    ##  Set the filter of this model based on a string.
    #   \param filter_string The string to be converted into a dict.
    #                           Key value pairs need to be separated by : and a , for each pair.
    #                           example: "key1:value1,key2:value2"
    #   \sa _stringToDict
    def setFilter(self, filter_string):
        filter = self._stringToDict(filter_string)
        self._update()

    @pyqtProperty(str, fset = setFilter)
    def filter(self, filter):
        pass

    #   Convert a string into a dict.
    #   \sa setFilter
    def _stringToDict(self, string):
        filter_list = string.split(",")
        filter_dict = {}
        for pair in filter_list:
            pair = pair.split(":")
            if len(pair) == 2:
                filter_dict[pair[0]] = pair[1]
        return filter_dict