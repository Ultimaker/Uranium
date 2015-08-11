# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtSlot, QUrl

from UM.Application import Application
from UM.Qt.ListModel import ListModel
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode

class PerObjectSettingsModel(ListModel):
    IdRole = Qt.UserRole + 1
    XRole = Qt.UserRole + 2
    YRole = Qt.UserRole + 3
    MaterialRole = Qt.UserRole + 4
    ProfileRole = Qt.UserRole + 5
    SettingsRole = Qt.UserRole + 6

    def __init__(self, parent = None):
        super().__init__(parent)
        self._root = Application.getInstance().getController().getScene().getRoot()
        self._root.transformationChanged.connect(self._updatePositions)
        self._root.childrenChanged.connect(self._updateNodes)
        self._updateNodes(None)

        self.addRoleName(self.IdRole,"id")
        self.addRoleName(self.XRole,"x")
        self.addRoleName(self.YRole,"y")
        self.addRoleName(self.MaterialRole, "material")
        self.addRoleName(self.ProfileRole, "profile")
        self.addRoleName(self.SettingsRole, "settings")

    def _updatePositions(self, source):
        camera =  Application.getInstance().getController().getScene().getActiveCamera()
        for node in BreadthFirstIterator(self._root):
            if type(node) is not SceneNode or not node.getMeshData():
                continue

            projected_position = camera.project(node.getWorldPosition())
            #print(projected_position)

            index = self.find("id", id(node))
            print(index)
            self.setProperty(index, "x", float(projected_position[0]))
            self.setProperty(index, "y", float(projected_position[1]))

    def _updateNodes(self, source):
        self.clear()
        camera =  Application.getInstance().getController().getScene().getActiveCamera()
        for node in BreadthFirstIterator(self._root):
            if type(node) is not SceneNode or not node.getMeshData():
                continue

            projected_position = camera.project(node.getWorldPosition())
            #print(projected_position)

            self.appendItem({
                "id": id(node),
                "x": float(projected_position[0]),
                "y": float(projected_position[1]),
                "material": "",
                "profile": "",
                "settings": []
            })
