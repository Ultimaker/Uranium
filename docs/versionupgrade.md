# Version Upgrade System
The version upgrade feature upgrades configuration from old versions to versions that are compatible with new versions of the application.

To provide support for upgrading from one version to another, the programmer defines a plug-in in the repository of the application with the following constraints:
* The plug-in SHOULD be located in the folder `./plugins/VersionUpgrade/VersionUpgradeXYtoZW` where `X` is the major version number of the old version, `Y` the minor version number of the old version, `Z` the major version number if the new version and `W` the minor version number of the new version.
* The plug-in MUST contain an `__init__.py` file with a `getMetaData()` function that returns a dictionary - let's call it `METADATA`. This is the same as all other plug-ins.
* The `METADATA` dictionary MUST have a `"version_upgrade"` field.
* The `"version_upgrade"` field SHOULD have one entry for each of the configuration types (see below).
* The `"version_upgrade"` field MAY NOT have more than one entry for any configuration type.
* Each entry in `"version_upgrade"` MUST have an entry `"from"` and an entry `"to"` to list the version number of that configuration type which it can upgrade. This version number MUST coincide with the version numbers in the classes corresponding to the configuration types at the appropriate application versions.
* The `__init__.py` file MUST define a class for the plug-in via the `register(app)` function (like all plug-ins).
* The plug-in class MUST implement the `upgrade<type>()` functions in `UM.VersionUpgrade` for the configuration types which it claims to be able to upgrade in `METADATA`.
* The `upgrade<type>()` functions MUST accept a string in the form of the old version's file and return a string in the form of the new version's file.

The configuration types currently supported are:
* Machine Instance
* Preferences
* Profile

For each new minor version of Cura in which any of these configuration types incremented their version number, we MUST include a new version upgrade plug-in to update the configuration of the user. With major version increments, we MAY include an additional plug-in that upgrades the configuration in larger increments, for faster processing.

The version upgrade system will:
* ...find the shortest path to upgrade each configuration file to the newest version, with the fewest upgrade steps possible.
* ...find all files it needs to upgrade.
* ...pass each file to the appropriate plug-in to upgrade it.
* ...move each file to an `./old` directory alongside the normal configuration files.
* ...write a new file in place of where the file used to be with the updated serialisation of the file.
* ...make the application load the new configuration files rather than the old ones.

Shortcomings of this system are:
* To be able to read the version numbers from each of the files, the files MUST remain config-files. It reads the version number by parsing it with `configparser` and reading the `general/version` key.
* The version upgrade system must be extended if the configuration types change. It is not required to extend this for old version upgrade plug-ins as long as the old configuration types are not removed from the system (backwards compatibility is ensured).
* The preferences configuration type (with global preferences) must be loaded before the plug-ins can load. The version upgrade system therefore can only re-apply the preferences after the loading of the plug-ins is completed. This means that the language cannot be updated. If the format for the language should change, this means that the user will have the language reset to his default at first launch of the new version. This will be corrected the next time he launches the application. The default language is the same as the system language (if that language is supported; otherwise it is English).
* Each upgrade plug-in has at most one upgrade for each configuration type. This is intended as it encourages the programmer to design these plug-ins for specific application versions.