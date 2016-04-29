# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject

def getMetaData():
    return {
        "plugin": {
            "name": "TestPlugin2",
            "api": 3
        }
    }

def register(app):
    return { "test": PluginObject() }
