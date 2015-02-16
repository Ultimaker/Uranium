from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot,QUrl

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Scene.Selection import Selection
from UM.Operations.RemoveSceneNodesOperation import RemoveSceneNodesOperation

import threading

class MeshListModel(ListModel):
    NameRole = Qt.UserRole + 1 #Label 
    VisibilityRole = Qt.UserRole + 2
    UniqueKeyRole = Qt.UserRole + 3
    SelectedRole = Qt.UserRole + 4
    DepthRole = Qt.UserRole + 5
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.updateList(Application.getInstance().getController().getScene().getRoot())
        Application.getInstance().getController().getScene().getRoot().childrenChanged.connect(self.updateList)
        self.addRoleName(self.NameRole,"name")
        self.addRoleName(self.VisibilityRole, "visibility")
        self.addRoleName(self.UniqueKeyRole, "key")
        self.addRoleName(self.SelectedRole, "selected")
        self.addRoleName(self.DepthRole, "depth")
        Application.getInstance().getController().getScene().rootChanged.connect(self._rootChanged)
        
    def _rootChanged(self):
        Application.getInstance().getController().getScene().getRoot().childrenChanged.connect(self.updateList)
        self.updateList(Application.getInstance().getController().getScene().getRoot()) #Manually trigger the update
    
    def updateList(self, trigger_node):
        self.clear()
        scene_nodes = trigger_node.getAllChildren()
        #self.appendItem({"name": "test", "visibility": True,"key":id(self), "selected": False})
        for node in scene_nodes:
            if node.getMeshData() is not None or node.hasChildren():
                self.appendItem({"name":node.getName(), "visibility": node.isVisible(), "key": (id(node)), "selected": Selection.isSelected(node),"depth": node.getDepth()})
    
    #def roleNames(self):
    #    return {self.NameRole:'name', self.VisibilityRole:"visibility",self.UniqueKeyRole: "key", self.SelectedRole: "selected"}
    
    # set the visibility of a node (by key)
    @pyqtSlot("long",bool)
    def setVisibility(self, key, visibility):
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if node.getMeshData() is not None:
                if id(node) == key:
                    node.setVisibility(visibility)
    
    #Set a single item to selected, by key
    @pyqtSlot("long")
    def setSelected(self, key):
        Selection.clear()
        for index in range(0,len(self.items)):
            if self.items[index]["key"] == key:
                self.setProperty(index,"selected", True)
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if id(node) == key:
                        Selection.add(node)
            else:
                self.setProperty(index,"selected", False)
    
    @pyqtSlot("long",QUrl)
    def saveMesh(self,key,file_url):
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if id(node) == key:
                Application.getInstance().getMeshFileHandler().write(file_url.toLocalFile(),Application.getInstance().getStorageDevice('local'),node.getMeshData())
        print("saving ",key)

    #Remove mesh by key (triggered by context menu)
    @pyqtSlot("long")
    def removeMesh(self, key):
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if id(node) == key:
                op = RemoveSceneNodesOperation([node])
                op.push()
                break

    
    
    