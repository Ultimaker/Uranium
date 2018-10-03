# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import CameraTool


def getMetaData():
    return {
        "tool": {
            "visible": False
        }
    }

def register(app):
    return { "tool": CameraTool.CameraTool() }
