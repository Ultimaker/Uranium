# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

class SettingsError(Exception):
    pass

class InvalidFileError(SettingsError):
    def __init__(self, path):
        super().__init__("File {0} is an invalid settings file".format(path))

class InvalidVersionError(SettingsError):
    def __init__(self, path):
        super().__init__("Invalid version for file {0}".format(path))

class DefinitionNotFoundError(SettingsError):
    def __init__(self, type_id):
        super().__init__("Could not find machine definition {0}".format(type_id))
