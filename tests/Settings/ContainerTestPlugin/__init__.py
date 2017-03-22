# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from .ContainerTestPlugin import ContainerTestPlugin
from UM.Settings.ContainerRegistry import ContainerRegistry

def getMetaData():
    return {
        "plugin": {
            "name": "TestContainerPlugin",
            "api": 3
        },
        "settings_container": {
            "mimetype": "application/x-uranium-test"
        }
    }

def register(app):
    return { "settings_container": ContainerTestPlugin() }
