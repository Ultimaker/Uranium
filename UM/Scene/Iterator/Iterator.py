# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


##    Abstract iterator class.
class Iterator(object):
    def __init__(self, scene_node):
        super(Iterator, self).__init__() # Call super to make multiple inheritence work.
        self._scene_node = scene_node
        self._node_stack = [] 
        self._fillStack()
    
    ##   Fills the list of nodes by a certain order. The strategy to do this is to be defined by the child.
    def _fillStack(self):
        raise NotImplementedError("Iterator is not correctly implemented. Requires a _fill_stack implementation.")
    
    def __iter__(self):
        return iter(self._node_stack)