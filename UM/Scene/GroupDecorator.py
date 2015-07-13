from UM.Scene.SceneNodeDecorator import SceneNodeDecorator

class GroupDecorator(SceneNodeDecorator):
    def __init__(self):
        super().__init__()
        
    def isGroup(self):
        return True