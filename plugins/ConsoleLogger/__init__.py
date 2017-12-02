# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

#Shoopdawoop
from . import ConsoleLogger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")


def getMetaData():
    return {}


def register(app):
    return { "logger": ConsoleLogger.ConsoleLogger() }
