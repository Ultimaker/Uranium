# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

class SceneNodeDecorator():
    def __init__(self):
        super().__init__()
        self._node = None
        
    def setNode(self, node):
        self._node = node