# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

# Workaround for a race condition on certain systems where there
# is a race condition between Arcus and PyQt. Importing Arcus
# first seems to prevent Sip from going into a state where it
# tries to create PyQt objects on a non-main thread.
import Arcus  # @UnusedImport
from . import CameraTool


def getMetaData():
    return {
        "tool": {
            "visible": False
        }
    }


def register(app):
    return {"tool": CameraTool.CameraTool()}
