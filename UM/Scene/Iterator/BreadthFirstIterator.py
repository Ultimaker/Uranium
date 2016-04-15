# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Iterator


class BreadthFirstIterator(Iterator.Iterator):
    def __init__(self, scene_node):
        super(BreadthFirstIterator, self).__init__(scene_node) # Call super to make multiple inheritence work.
    
    def _fillStack(self):
        if self._scene_node is not None:
            self._node_stack.append(self._scene_node)
            for node in self._node_stack: # Loop through list, add children to back of list
                self._node_stack.extend(node.getChildren())

