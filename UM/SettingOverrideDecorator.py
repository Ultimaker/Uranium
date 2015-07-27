from UM.Scene.SceneNodeDecorator import SceneNodeDecorator

class SettingOverrideDecorator(SceneNodeDecorator):
    def __init__(self):
        self._settings = {}
       
    def setSetting(self, key, value):
        self._settings[key] = value
        
    def getSetting(self, key):
        if key not in self._settings:
            parent = self._node.getParent()
            # It could be that the parent does not have a decoration but it's parent parent does. 
            while parent is not None: 
                if self._node.hasDecoration("getSetting"):
                    return self._node.getParent().callDecoration("getSetting")
                else:
                    parent = parent.getParent()
        else:
            return self._settings[key]