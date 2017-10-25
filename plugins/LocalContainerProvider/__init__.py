# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import LocalContainerProvider

def getMetaData():
    return {
        "container_provider": {
            "priority": 0
        }
    }

def register(app):
    return { "container_provider": LocalContainerProvider.LocalContainerProvider() }
