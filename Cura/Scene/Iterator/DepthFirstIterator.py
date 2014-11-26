from . import Iterator

class DepthFirstIterator(Iterator.Iterator):
    def __init__(self,scene_node):
        super(DepthFirstIterator, self).__init__(scene_node) # Call super to make multiple inheritence work.
    
    def _fillStack(self):
        print("nggh")
        self._node_stack.append(self._scene_node)
        print("num children all " + str(len(self._scene_node.getAllChildren())))
        print("num children direct " + str(len(self._scene_node.getChildren())))
        self._node_stack.extend(self._scene_node.getAllChildren())
