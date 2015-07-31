# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import LocalFileOutputDevicePlugin

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": catalog.i18nc("Local File Output Device plugin name", "Local File Output Device"),
            "description": catalog.i18nc("Local File Output Device plugin description", "Enables saving to local files"),
            "author": "Ultimaker B.V.",
            "version": "1.0",
            "api": 2,
        }
    }

def register(app):
    return { "output_device": LocalFileOutputDevicePlugin.LocalFileOutputDevicePlugin() }
