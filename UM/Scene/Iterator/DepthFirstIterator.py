# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import Iterator


class DepthFirstIterator(Iterator.Iterator):
    def __init__(self, scene_node):
        super(DepthFirstIterator, self).__init__(scene_node) # Call super to make multiple inheritence work.
    
    def _fillStack(self):
        self._node_stack.append(self._scene_node)
        self._node_stack.extend(self._scene_node.getAllChildren())
