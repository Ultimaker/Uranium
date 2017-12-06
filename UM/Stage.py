# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.PluginObject import PluginObject

##  Stages handle combined views in an Uranium application.
#   The active stage decides which QML component to show where.
#   Uranium has no notion of specific view locations as that's application specific.
class Stage(PluginObject):

    def __init__(self):
        super().__init__()
        self._application = None
        self._views = {}

    ##  Inject the active application.
    def setApplication(self, application):
        self._application = application

    ##  Add a view to the stage
    def addView(self):
        return None
        # TODO

    ##  Get a view by name.
    def getView(self, name: str):
        if name in self._views:
            return self._views[name]
        return None
