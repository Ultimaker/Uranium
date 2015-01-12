from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Scene.Selection import Selection

import threading

class MeshListModel(ListModel):
    NameRole = Qt.UserRole + 1 #Label 
    VisibilityRole = Qt.UserRole + 2
    UniqueKeyRole = Qt.UserRole + 3
    SelectedRole = Qt.UserRole + 4
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.updateList(Application.getInstance().getController().getScene().getRoot())
        Application.getInstance().getController().getScene().getRoot().childrenChanged.connect(self.updateList)
    
    def updateList(self, trigger_node):
        self.clear()
        scene_nodes = trigger_node.getAllChildren()
        for node in scene_nodes:
            if node.getMeshData() is not None:
                self.appendItem({"name":node.getMeshData().getName(), "visibility": node.isVisible(), "key": (id(node)), "selected": Selection.isSelected(node)})
    
    def roleNames(self):
        return {self.NameRole:'name', self.VisibilityRole:"visibility",self.UniqueKeyRole: "key", self.SelectedRole: "selected"}
    
    @pyqtSlot("long",bool)
    def setVisibility(self, key, visibility):
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if node.getMeshData() is not None:
                if id(node) == key:
                    node.setVisibility(visibility)
    
    
    