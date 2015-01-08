from . import Operation

from UM.Scene.SceneNode import SceneNode

##  An operation that removes an list of SceneNode from the scene.
class RemoveSceneNodesOperation(Operation.Operation):
    def __init__(self, nodes):
        super().__init__()
        self._nodes = [n for n in nodes] # Make a copy of the list of nodes
        self._parents = [n.getParent() for n in nodes]

    def undo(self):
        for i in range(len(self._nodes)):
            self._nodes[i].setParent(self._parents[i])

    def redo(self):
        for node in self._nodes:
            node.setParent(None)
