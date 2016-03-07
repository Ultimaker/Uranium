# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.PluginRegistry import PluginRegistry

##  Regulates the upgrading of preferences from one application version to the
#   next.
#
#   The process of upgrading will take a look at all profiles, preferences and
#   machine instances and check their version numbers. If they are older than
#   the current version number of their respective type of file, an upgrade path
#   will be planned for it in order to upgrade the file to the current version
#   in as few conversions as possible.
#
#   To this end, the upgrade manager will maintain the shortest paths to the
#   current version for each of the types of profiles and each old version it
#   encounters. Once a shortest path is found, it is cached and can be re-used
#   for all nodes along this path. This minimises the extra start-up time
#   required for the conversions.
#
#   Old versions of the preferences are not deleted, but put in a folder next to
#   the current (upgraded) versions, where they are never loaded again unless
#   the user manually retrieves the files.
class VersionUpgradeManager:
    ##  Initialises the version upgrade manager.
    #
    #   This initialises the cache for shortest upgrade paths, and registers the
    #   version upgrade plug-ins.
    def __init__(self):
        #Initialise the caches for shortest upgrade paths.
        #These dictionaries are keyed by the version number for which it is the shortest path.
        #The value indicates the version upgrade plug-in to use to upgrade to the next version.
        self._machine_instance_upgrade_paths = {} #The shortest paths to upgrade machine instances to the current version.
        self._preferences_upgrade_paths = {} #The shortest paths to upgrade preferences to the current version.
        self._profile_upgrade_paths = {} #The shortest paths to upgrade profiles to the current version.

        self._versionUpgrades = [] #All upgrade plug-ins.
        PluginRegistry.addType("version_upgrade", self._addVersionUpgrade)

    ##  Performs the version upgrades of all preference files to the most recent
    #   version.
    #
    #   The upgrade plug-ins must all be loaded at this point, or no upgrades
    #   can be performed.
    def upgrade(self):
        pass

    ##  Adds a version upgrade plug-in.
    #
    #   \param version_upgrade_plugin The plug-in object of the version upgrade
    #   plug-in.
    def _addVersionUpgrade(self, version_upgrade_plugin):
        self._versionUpgrades.append(version_upgrade_plugin)