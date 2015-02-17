from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot,QUrl

from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Scene.Selection import Selection
from UM.Operations.RemoveSceneNodesOperation import RemoveSceneNodesOperation
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

import threading

class MeshListModel(ListModel):
    NameRole = Qt.UserRole + 1 #Label 
    VisibilityRole = Qt.UserRole + 2
    UniqueKeyRole = Qt.UserRole + 3
    SelectedRole = Qt.UserRole + 4
    DepthRole = Qt.UserRole + 5
    CollapsedRole = Qt.UserRole+6
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._scene = Application.getInstance().getController().getScene()
        self.updateList(self._scene.getRoot())
        self._scene.getRoot().childrenChanged.connect(self.updateList)
        self.addRoleName(self.NameRole,"name")
        self.addRoleName(self.VisibilityRole, "visibility")
        self.addRoleName(self.UniqueKeyRole, "key")
        self.addRoleName(self.SelectedRole, "selected")
        self.addRoleName(self.DepthRole, "depth")
        self.addRoleName(self.CollapsedRole,"collapsed")
        self._scene.rootChanged.connect(self._rootChanged)
        
    def _rootChanged(self):
        self._scene.getRoot().childrenChanged.connect(self.updateList)
        self.updateList(self._scene.getRoot()) #Manually trigger the update
    
    def updateList(self, trigger_node):
        self.clear()
        #scene_nodes = trigger_node.getAllChildren()
        #self.appendItem({"name": "test", "visibility": True,"key":id(self), "selected": False})
        
        for group_node in self._scene.getRoot().getChildren():
            for node in DepthFirstIterator(group_node):
                if node.getMeshData() is not None or node.hasChildren():
                    parent_key = 0
                    if group_node is not node:
                        parent_key =  (id(group_node))
                    self.appendItem({"name":node.getName(), "visibility": node.isVisible(), "key": (id(node)), "selected": Selection.isSelected(node),"depth": node.getDepth(),"collapsed": False,"parent_key": parent_key})
        
    #def roleNames(self):
    #    return {self.NameRole:'name', self.VisibilityRole:"visibility",self.UniqueKeyRole: "key", self.SelectedRole: "selected"}
    
    # set the visibility of a node (by key)
    @pyqtSlot("long",bool)
    def setVisibility(self, key, visibility):
        for node in self._scene.getRoot().getAllChildren():
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
    @pyqtSlot(str)
    def setCollapsed(self,key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if int(item["parent_key"]) == int(key):  
                self.setProperty(index, 'collapsed', not item['collapsed'])
    
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

    
    
    