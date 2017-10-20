# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import LocalInstanceProvider

def getMetaData():
    return {
        "container_provider": {
            "priority": 10
        }
    }

def register(app):
    return { "container_provider": LocalInstanceProvider.LocalInstanceProvider() }
