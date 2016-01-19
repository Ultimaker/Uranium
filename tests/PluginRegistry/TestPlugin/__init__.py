# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject

def getMetaData():
    return {
        "plugin": {
            "name": "TestPlugin",
            "api": 2
        }
    }

def register(app):
    return { "test": PluginObject() }