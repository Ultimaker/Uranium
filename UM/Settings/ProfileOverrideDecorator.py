# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from UM.Application import Application

class ProfileOverrideDecorator(SceneNodeDecorator):
    def __init__(self):
        super().__init__()

        self._profile = None

    def setProfile(self, profile):
        self._profile = profile
        Application.getInstance().getController().getScene().sceneChanged.emit(self._node)

    def getProfile(self):
        return self._profile
