# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.Application import Application # To use the plug-in manager.
from UM.PluginObject import PluginObject # To create artificial plug-ins.
from UM.VersionUpgrade import VersionUpgrade
from UM.VersionUpgradeManager import VersionUpgradeManager

import pytest

##  Tests the version upgrade manager.
class TestVersionUpgradeManager():
    ##  Executed before the first test function is executed.
    def setup_method(self, method):
        self._upgrade_manager = VersionUpgradeManager()

    ##  Executed after the last test function was executed.
    def teardown_method(self, method):
        pass

    ##  The individual test cases for shortest upgrade paths.
    #
    #   Each entry contains a list of possible upgrades. Each upgrade has a
    #   from_version, a to_version and a preference_type field. Each entry also
    #   has a destination version to upgrade to and a preference type to filter
    #   on. Each entry has a list of possible answers, each of which is a
    #   mapping of version numbers to indices referring to upgrades in the input
    #   list. Lastly, each entry has a name for debugging.
    test_shortest_paths_data = [
        ({
            "name": "two-step",
            "upgrades": [
                { "from_version": 0, "to_version": 1, "preference_type": "a" },
                { "from_version": 1, "to_version": 2, "preference_type": "a" }
            ],
            "destination": 2,
            "preference_type": "a",
            "answers": [
                { 0: 0, 1: 1 }
            ]
        }),
        ({
            "name": "two-options",
            "upgrades": [
                { "from_version": 0, "to_version": 1, "preference_type": "a" },
                { "from_version": 0, "to_version": 1, "preference_type": "a" }
            ],
            "destination": 1,
            "preference_type": "a",
            "answers": [
                { 0: 0 },
                { 0: 1 }
            ]
        }),
        ({
            "name": "shortcut",
            "upgrades": [
                { "from_version": 0, "to_version": 1, "preference_type": "a" },
                { "from_version": 1, "to_version": 2, "preference_type": "a" },
                { "from_version": 0, "to_version": 2, "preference_type": "a" }
            ],
            "destination": 2,
            "preference_type": "a",
            "answers": [
                { 0: 2, 1: 1 }
            ]
        }),
        ({
            "name": "preference-type-filter",
            "upgrades": [
                { "from_version": 0, "to_version": 2, "preference_type": "b" },
                { "from_version": 1, "to_version": 2, "preference_type": "a" },
                { "from_version": 0, "to_version": 1, "preference_type": "a" }
            ],
            "destination": 2,
            "preference_type": "a",
            "answers": [
                { 0: 2, 1: 1 }
            ]
        })
    ]

    ##  Tests the algorithm to find shortest paths to update plug-ins.
    #
    #   This function is normally not "exposed" (though Python puts no
    #   limitations on that). However, since the accuracy of this function
    #   should only affect the execution speed, it is wise to test this function
    #   nonetheless.
    #
    #   \param data The data containing individual tests.
    @pytest.mark.parametrize("data", test_shortest_paths_data)
    def test_shortest_paths(self, data):
        registry = Application.getInstance().getPluginRegistry()
        self._loadUpgrades(data["upgrades"])
        shortest_paths = self._upgrade_manager._findShortestUpgradePaths(data["preference_type"], data["destination"]) # Find the shortest path.

        # Convert the upgrades in the path to indices in our original data.
        to_indices = {}
        for version, upgrade in shortest_paths.items():
            metadata = registry.getMetaData(upgrade.getPluginId())["version_upgrade"]
            for key, value in metadata.items(): # Get just the first element of the dict. There is always only one.
                preference_type = key
                from_version = metadata[preference_type]["from"]
                to_version = metadata[preference_type]["to"]
                break
            for i in range(0, len(data["upgrades"])): # Which index does it have?
                if data["upgrades"][i]["from_version"] == from_version and data["upgrades"][i]["to_version"] == to_version and data["upgrades"][i]["preference_type"] == preference_type:
                    to_indices[from_version] = i
                    break

        # Compare with the answers.
        for answer in data["answers"]:
            if len(answer) != len(to_indices): # Not the same amount of source versions.
                continue # Incorrect answer.
            for version, upgrade in answer.items():
                if version not in to_indices: # Key is missing!
                    break # Incorrect answer.
                if answer[version] != to_indices[version]: # Different plug-in for this version!
                    break # Incorrect answer.
            else: # No indices were different. Answer is correct.
                break
        else: # No answers were correct.
            assert False # Incorrect path.

    ##  Create a plug-in registry with the specified upgrade plug-ins in it.
    #
    #   \param upgrades Metadata of upgrades to fill the registry with, as
    #   obtained from test_shortest_paths_data.
    def _loadUpgrades(self, upgrades):
        registry = Application.getInstance().getPluginRegistry()
        for upgrade in upgrades: # Artificially fill the plug-in registry with my own metadata!
            plugin_object = PluginObject()
            metadata = { # Correctly fill the metadata for this plug-in.
                "plugin": {
                    "name": "Upgrade Test", # Note: Don't use internationalisation here, lest it be grabbed by gettext.
                    "author": "Ultimaker",
                    "version": "1.0",
                    "description": "Upgrade plug-in to test with.",
                    "api": 2
                },
                "version_upgrade": {}
            }
            metadata["version_upgrade"][upgrade["preference_type"]] = {}
            metadata["version_upgrade"][upgrade["preference_type"]]["from"] = upgrade["from_version"]
            metadata["version_upgrade"][upgrade["preference_type"]]["to"] = upgrade["to_version"]
            id = upgrade["preference_type"] + "-from-" + str(upgrade["from_version"]) + "-to-" + str(upgrade["to_version"]) # ID becomes "type-from-#-to-#".
            plugin_object.setPluginId(id)
            registry._plugins[id] = plugin_object
            registry._meta_data[id] = metadata
            self._upgrade_manager._addVersionUpgrade(plugin_object)