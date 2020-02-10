# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.ContainerStack import ContainerStack

class ContainerStacksModel(ListModel):
    """Model that holds container stacks. By setting the filter property the stacks held by this model can be
    changed.
    """

    NameRole = Qt.UserRole + 1
    IdRole = Qt.UserRole + 2
    MetaDataRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.MetaDataRole, "metadata")
        self._container_stacks = []

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerMetaDataChanged.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)
        self._filter_dict = {}
        self._update()

    def _onContainerChanged(self, container):
        """Handler for container added/removed events from registry"""

        # We only need to update when the added / removed container is a stack.
        if isinstance(container, ContainerStack):
            self._update()

    def _onContainerNameChanged(self):
        """Handler for container name change events."""

        self._update()

    def _update(self):
        """Private convenience function to reset & repopulate the model."""

        items = []
        # Remove all connections
        for container in self._container_stacks:
            container.nameChanged.disconnect(self._onContainerNameChanged)

        self._container_stacks = ContainerRegistry.getInstance().findContainerStacks(**self._filter_dict)
        self._container_stacks.sort(key = lambda i: i.getName())

        for container in self._container_stacks:
            metadata = container.getMetaData().copy()
            if container.getBottom():
                metadata["definition_name"] = container.getBottom().getName()

            container.nameChanged.connect(self._onContainerNameChanged)
            items.append({"name": container.getName(),
                             "id": container.getId(),
                             "metadata": metadata})
        self.setItems(items)

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
