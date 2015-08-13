from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from UM.Signal import Signal, SignalEmitter

class SettingOverrideDecorator(SceneNodeDecorator, SignalEmitter):
    def __init__(self):
        super().__init__()
        self._settings = {}

    settingAdded = Signal()
    settingRemoved = Signal()
    settingValueChanged = Signal()

    def getAllSettings(self):
        return self._settings
       
    def setSetting(self, key, value):
        if key not in self._settings:
            self._settings[key] = value
            self.settingAdded.emit()
            return

        if self._settings[key] != value:
            self._settings[key] = value
            self.settingValueChanged.emit(key, value)
        
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

    def removeSetting(self, key):
        if key not in self._settings:
            return

        del self._settings[key]
        self.settingRemoved.emit()
