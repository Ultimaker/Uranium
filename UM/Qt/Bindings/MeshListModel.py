# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt, QUrl
from UM.FlameProfiler import pyqtSlot
from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Scene.Selection import Selection
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.SceneNode import SceneNode
from UM.Scene.PointCloudNode import PointCloudNode

class MeshListModel(ListModel):
    NameRole = Qt.UserRole + 1 #Label 
    VisibilityRole = Qt.UserRole + 2
    UniqueKeyRole = Qt.UserRole + 3
    SelectedRole = Qt.UserRole + 4
    CollapsedRole = Qt.UserRole + 5
    IsGroupRole = Qt.UserRole + 6
    IsDummyRole = Qt.UserRole + 7

    def __init__(self, parent = None):
        super().__init__(parent)
        self._collapsed_nodes = []
        self._scene = Application.getInstance().getController().getScene()
        self.updateList(self._scene.getRoot())
        self._scene.getRoot().childrenChanged.connect(self._onNodeAdded)
        self.addRoleName(self.NameRole,"name")
        self.addRoleName(self.VisibilityRole, "visibility")
        self.addRoleName(self.UniqueKeyRole, "key")
        self.addRoleName(self.SelectedRole, "selected")
        self.addRoleName(self.CollapsedRole,"collapsed")
        self.addRoleName(self.IsGroupRole,"is_group")
        self.addRoleName(self.IsDummyRole, "is_dummy")
        self._scene.rootChanged.connect(self._rootChanged)
        Selection.selectionChanged.connect(self._onSelectionChanged)

    def _onNodeAdded(self, node):
        self.updateList(node)

    def _onSelectionChanged(self):
        self.updateList(self._scene.getRoot())

    def _rootChanged(self):
        self._scene.getRoot().childrenChanged.connect(self.updateList)
        self.updateList(self._scene.getRoot()) # Manually trigger the update

    @pyqtSlot("long",int)
    def moveItem(self, key, new_index):
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if id(node) == key:
                # Found moved node.
                old_index = self.find("key",key)
                if old_index == new_index: # No change.
                    return

                old_model_entry = self.getItem(old_index) # Model data of moving node
                new_model_entry = self.getItem(new_index) # Model data of location node should move to.

                for parent_node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if id(parent_node) == new_model_entry["parent_key"]:
                        # Found group the object is moving to.
                        group_move = False
                        if id(node.getParent()) != id(parent_node):
                            group_move = True
                            # Move to different group.
                            node.setParent(parent_node)
                            self.removeItem(old_index) # Remove 'old' (now moved) item
                            if parent_node not in self._collapsed_nodes and node in self._collapsed_nodes:
                                self._collapsed_nodes.remove(node)
                            if parent_node in self._collapsed_nodes and node not in self._collapsed_nodes:
                                self._collapsed_nodes.append(node)
                        # Magical move
                        for node2 in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                            if id(node2) == new_model_entry["key"]:
                                # Ensure that items within a group are in the correct order.
                                children = parent_node.getChildren()

                                if node2 == parent_node:
                                    a , b = self.find("key",(id(children[0]))), self.find("key",(id(children[-1])))
                                    children.insert(0, children[-1])
                                    children.pop()

                                else:
                                    new_index = children.index(node2)
                                    if new_index > children.index(node) or (group_move and False):
                                        new_index += 1
                                    children.insert(new_index, node)
                                    old_index = [i for i, child in enumerate(children) if child == node and i != new_index][0]
                                    del children[old_index]
                                break

                        else:
                            # Switch happend to dummy?
                            pass
                        self.updateList(node)
                        break
                      #  break

                #self.removeItem(old_index)
                #self.insertItem(new_index,data)

    def updateList(self, trigger_node):
        self.clear()
        for root_child in self._scene.getRoot().getChildren():
            if root_child.callDecoration("isGroup"): # Check if its a group node
                parent_key = id(root_child)
                for node in DepthFirstIterator(root_child):
                    if root_child in self._collapsed_nodes:
                        self._collapsed_nodes.append(node)

                    data = {"name":node.getName(),
                            "visibility": node.isVisible(),
                            "key": (id(node)),
                            "selected": Selection.isSelected(node),
                            "collapsed": node in self._collapsed_nodes,
                            "parent_key": parent_key,
                            "is_group":bool(node.callDecoration("isGroup")),
                            "is_dummy" : False
                            }
                    self.appendItem(data)
                data = { "name":"Dummy",
                         "visibility": True,
                         "key": 0,
                         "selected": Selection.isSelected(node),
                         "collapsed": root_child in self._collapsed_nodes,
                         "parent_key": parent_key,
                         "is_group":False,
                         "is_dummy" : True
                        }
                self.appendItem(data)

            elif type(root_child) is SceneNode or type(root_child) is PointCloudNode: # Item is not a group node.
                data = {"name":root_child.getName(),
                        "visibility": root_child.isVisible(),
                        "key": (id(root_child)),
                        "selected": Selection.isSelected(root_child),
                        "collapsed": root_child in self._collapsed_nodes,
                        "parent_key": 0,
                        "is_group":bool(root_child.callDecoration("isGroup")),
                        "is_dummy" : False
                        }

                # Check if data exists, if yes, remove old and re-add.
                index = self.find("key",(id(root_child)))
                if index is not None and index >= 0:
                    self.removeItem(index)
                    self.insertItem(index,data)
                else:
                    self.appendItem(data)

    # set the visibility of a node (by key)
    @pyqtSlot("long",bool)
    def setVisibility(self, key, visibility):
        for node in self._scene.getRoot().getAllChildren():
            if id(node) == key:
                node.setVisible(visibility)

    @pyqtSlot("long",str)
    def setName(self, key, name):
        for index in range(0,len(self.items)):
            if self.items[index]["key"] == key:
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if id(node) == key:
                        node.setName(name)

    #Set a single item to be selected, by key
    @pyqtSlot("long")
    def setSelected(self, key):
        for index in range(0,len(self.items)):
            if self.items[index]["key"] == key:
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if id(node) == key:
                        if node not in Selection.getAllSelectedObjects(): #node already selected
                            Selection.add(node)
                            if node.callDecoration("isGroup"): #Its a group node
                                for child_node in node.getChildren():
                                    if child_node not in Selection.getAllSelectedObjects(): #Set all children to parent state (if they arent already)
                                        Selection.add(child_node)
                        else:
                            Selection.remove(node)
                            if node.callDecoration("isGroup"): #Its a group
                                for child_node in node.getChildren():
                                    if child_node in Selection.getAllSelectedObjects():
                                        Selection.remove(child_node)

        all_children_selected = True
        #Check all group nodes to see if all their children are selected (if so, they also need to be selected!)
        for index in range(0,len(self.items)):
            if self.items[index]["is_group"]:
                for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
                    if node.hasChildren():
                        if id(node) == self.items[index]["key"] and id(node) != key:
                            for index, child_node in enumerate(node.getChildren()):
                                if not Selection.isSelected(child_node):
                                    all_children_selected = False #At least one of its children is not selected, dont change state
                                    break
                            if all_children_selected:
                                Selection.add(node)
                            else:
                                Selection.remove(node)
        #Force update
        self.updateList(Application.getInstance().getController().getScene().getRoot())

    @pyqtSlot(str)
    def setCollapsed(self,key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if int(item["parent_key"]) == int(key) or int(item["key"]) == int(key):
                self.setProperty(index, "collapsed", not item["collapsed"])
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
                Application.getInstance().getMeshFileHandler().write(file_url.toLocalFile(),Application.getInstance().getStorageDevice("LocalFileStorage"),node.getMeshDataTransformed())


    #Remove mesh by key (triggered by context menu)
    @pyqtSlot("long")
    def removeMesh(self, key):
        for node in Application.getInstance().getController().getScene().getRoot().getAllChildren():
            if id(node) == key:
                op = RemoveSceneNodeOperation(node)
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



