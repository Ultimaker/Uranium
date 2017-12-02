# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


##      The point of a SceneNodeDecorator is that it can be added to a SceneNode, where it then provides decorations
#       Decorations are functions of a SceneNodeDecorator that can be called (except for functions already defined
#       in SceneNodeDecorator).
#       \sa SceneNode
class SceneNodeDecorator:
    def __init__(self, node = None):
        super().__init__()
        self._node = node
        
    def setNode(self, node):
        self._node = node

    def getNode(self):
        return self._node

    ##  Clear all data associated with this decorator. This will be called before the decorator is removed
    def clear(self):
        pass

    def __deepcopy__(self, memo):
        raise NotImplementedError("Subclass {0} of SceneNodeDecorator should implement their own __deepcopy__() method.".format(str(self)))
