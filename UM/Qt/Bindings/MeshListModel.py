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
    HasChildrenRole = Qt.UserRole+7
    
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
        self.addRoleName(self.HasChildrenRole,"has_children")
        self._scene.rootChanged.connect(self._rootChanged)
        self._collapsed_nodes = []
        
    def _rootChanged(self):
        self._scene.getRoot().childrenChanged.connect(self.updateList)
        self.updateList(self._scene.getRoot()) # Manually trigger the update
    
    def updateList(self, trigger_node):
        self.clear()

        for group_node in self._scene.getRoot().getChildren():
            for node in DepthFirstIterator(group_node):
                if node.getMeshData() is not None or node.hasChildren():
                    parent_key = 0
                    if group_node is not node:
                        parent_key =  (id(group_node))
                    self.appendItem({"name":node.getName(), "visibility": node.isVisible(), "key": (id(node)), "selected": Selection.isSelected(node),"depth": node.getDepth(),"collapsed": node in self._collapsed_nodes,"parent_key": parent_key, "has_children":node.hasChildren()})
        
    # set the visibility of a node (by key)
    @pyqtSlot("long",bool)
    def setVisibility(self, key, visibility):
        for node in self._scene.getRoot().getAllChildren():
            if id(node) == key:
                node.setVisibility(visibility)
    
    #Set a single item to selected, by key
    @pyqtSlot("long")
    def setSelected(self, key):
        for index in range(0,len(self.items)):
            if self.items[index]["key"] == key:
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if id(node) == key:
                        if node not in Selection.getAllSelectedObjects(): #Group node already selected
                            Selection.add(node)
                            self.setProperty(index,"selected", True)
                        else:
                            Selection.remove(node)
                            print("removing node")
                            self.setProperty(index,"selected", False)
        
        #Check all group nodes to see if all their children are selected (if so, they also need to be selected!)
        for index in range(0,len(self.items)):
            if self.items[index]["depth"] == 1:
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if node.hasChildren():
                        if id(node) == self.items[index]["key"] and id(node) != key: 
                            for child_node in node.getChildren():
                                print("Child node")
                                if not Selection.isSelected(child_node):
                                    break #At least one of its children is not selected, dont change state
                            #All children are selected (ergo it is also selected!)
                            self.setProperty(index,"selected", True)
                            Selection.add(node)
        #Force update                  
        self.updateList(Application.getInstance().getController().getScene().getRoot())
    
    @pyqtSlot(str)
    def setCollapsed(self,key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if int(item["parent_key"]) == int(key):  
                self.setProperty(index, 'collapsed', not item['collapsed'])
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if int(item["key"]) == id(node):
                        if node not in self._collapsed_nodes:
                            self._collapsed_nodes.append(node)
                        else:
                            self._collapsed_nodes.remove(node)
    
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

    @pyqtSlot()
    def removeSelected(self):
        keys_to_be_removed = []
        nodes_to_be_removed = []
        for item in self.items:
            if item["selected"]:
                keys_to_be_removed.append(item["key"])
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if id(node) in keys_to_be_removed:
                nodes_to_be_removed.append(node)
        
        if len(nodes_to_be_removed):
            op = RemoveSceneNodesOperation(nodes_to_be_removed)
            op.push()
    
    