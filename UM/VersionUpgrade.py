# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginObject import PluginObject

##  A type of plug-in that upgrades the configuration from an old file format to
#   a newer one.
#
#   Each version upgrade plug-in can convert machine instances, preferences and
#   profiles from one version to one other version. Which versions that are is
#   specified in the metadata of the plug-in.
class VersionUpgrade(PluginObject):
    ##  Initialises a version upgrade plugin instance.
    def __init__(self):
        super().__init__()

    ##  Upgrades a machine instance file from one file format to another.
    #
    #   This parses the serialised data of a machine instance and converts it to
    #   a serialised form of the new file format.
    #
    #   \param serialised A machine instance, serialised in an old file format.
    #   \return A machine instance, serialised in a newer file format.
    def upgradeMachineInstance(self, serialised):
        Logger.log("w", "This version upgrade plug-in defines no way to upgrade machine instances.") # A subclass should implement this.
        raise Exception("Machine instance upgrade is not implemented in this plug-in.")

    ##  Upgrades a preferences file from one file format to another.
    #
    #   This parses the serialised data of a preferences file and converts it to
    #   a serialised form of the new file format.
    #
    #   \param serialised A preferences file, serialised in an old file format.
    #   \return A preferences file, serialised in a newer file format.
    def upgradePreferences(self, serialised):
        Logger.log("w", "This version upgrade plug-in defines no way to upgrade preferences.") # A subclass should implement this.
        raise Exception("Preferences upgrade is not implemented in this plug-in.")

    ##  Upgrades a profile from one file format to another.
    #
    #   This parses the serialised data of a profile and converts it to a
    #   serialised form of the new file format.
    #
    #   \param serialised A profile, serialised in an old file format.
    #   \return A profile, serialised in a newer file format.
    def upgradeProfile(self, serialised):
        Logger.log("w", "This version upgrade plug-in defines no way to upgrade profiles.") # A subclass should implement this.
        raise Exception("Profile upgrade is not implemented in this plug-in.")