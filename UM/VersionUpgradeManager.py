# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.PluginRegistry import PluginRegistry
from UM.Preferences import Preferences
from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.Profile import Profile

import collections #For deque, for breadth-first search.

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
        paths = self._findShortestUpgradePaths("machine_instance", MachineInstance.MachineInstanceVersion)
        #TODO: Find all machine instances.
        #TODO: Upgrade all machine instances to the most recent version.
        paths = self._findShortestUpgradePaths("preferences", Preferences.PreferencesVersion)
        #TODO: Find all preference files.
        #TODO: Upgrade all preference files to the most recent version.
        paths = self._findShortestUpgradePaths("profile", Profile.ProfileVersion)
        #TODO: Find all profiles.
        #TODO: Upgrade all profiles to the most recent version.

    # private:

    ##  Adds a version upgrade plug-in.
    #
    #   \param version_upgrade_plugin The plug-in object of the version upgrade
    #   plug-in.
    def _addVersionUpgrade(self, version_upgrade_plugin):
        self._versionUpgrades.append(version_upgrade_plugin)

    ##  For each version of a preference type, finds the next step to take to
    #   upgrade as quickly as possible to the most recent version.
    #
    #   The preference type should be either "machine_instance", "preferences"
    #   or "profile", matching the types listed in the metadata of a plug-in.
    #   This is abstracted to prevent having to maintain the same code in lots
    #   of different functions that do basically the same.
    #
    #   This function uses a breadth-first search to get the fewest number of
    #   steps required to upgrade to the destination version.
    #
    #   \param preference_type The type of preference to compute the shortest
    #   upgrade paths of.
    #   \param destination_version The version to compute the shortest paths to.
    #   \return A dictionary with an entry for each version number from which we
    #   can reach the destination version, naming the version upgrade plug-in
    #   with which to convert for the next step.
    def _findShortestUpgradePaths(self, preference_type, destination_version):
        by_destination_version = self._sortByDestinationVersion(preference_type)
        result = {}

        #Perform a breadth-first search.
        registry = PluginRegistry.getInstance()
        front = collections.deque() #Use as a queue for breadth-first iteration: Append right, pop left.
        done = {} #Flag explored upgrades as done.
        for neighbour in by_destination_version[destination_version]:
            front.append(neighbour)
            source_version = registry.getMetaData(neighbour.getPluginId())["version_upgrade"][preference_type]["from"]
            if source_version not in result: #First time we encounter this version. Due to breadth-first search, this must be part of the shortest path then.
                result[source_version] = neighbour
            done += neighbour
        while len(front) > 0:
            upgrade = front.popleft() #To make it a queue, pop on the opposite side of where you append!
            for neighbour in by_destination_version[registry.getMetaData(upgrade.getPluginId())["version_upgrade"][preference_type]["to"]]:
                if neighbour in done: #Already encountered elsewhere. No need to re-compute.
                    continue
                front.append(neighbour)
                source_version = registry.getMetaData(neighbour.getPluginId())["version_upgrade"][preference_type]["from"]
                if source_version not in result: #First time we encounter this version. Due to breadth-first search, this must be part of the shortest path then.
                    result[source_version] = neighbour
                done += neighbour

        return result

    ##  Creates a look-up table to get plug-ins by what version they upgrade
    #   to.
    #
    #   \param preference_type The type of preference file the version number
    #   applies to.
    #   \return A dictionary with an entry for every version that the upgrade
    #   plug-ins can convert to, and which plug-ins can convert to that version.
    def _sortByDestinationVersion(self, preference_type):
        result = {}
        registry = PluginRegistry.getInstance()
        for plugin in self._versionUpgrades:
            destination = registry.getMetaData(plugin.getPluginId())["version_upgrade"][preference_type]["to"]
            if not destination in result: #Entry doesn't exist yet.
                result[destination] = []
            result[destination].append(plugin) #Sort this plug-in under the correct entry.
        return result