# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import LocalFileOutputDevicePlugin

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

def getMetaData():
    return {
    }

def register(app):
    return { "output_device": LocalFileOutputDevicePlugin.LocalFileOutputDevicePlugin() }
