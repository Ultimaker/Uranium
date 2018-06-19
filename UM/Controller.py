# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import TYPE_CHECKING

from UM.Scene.Scene import Scene

if TYPE_CHECKING:
    from UM.Application import Application


class Controller:
    def __init__(self, application: "Application") -> None:
        super().__init__()
        self._application = application

        self._scene = Scene()

    def getScene(self) -> Scene:
        return self._scene
