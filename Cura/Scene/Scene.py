from Cura.Scene.SceneObject import SceneObject

class Scene(object):
    def __init__(self):
        self._root = SceneObject()
        
        
    def getRoot(self):
        return self._root