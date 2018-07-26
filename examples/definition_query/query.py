#!/usr/bin/env python

# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

#
# A simple example/tool to query a definition and get a list of settings matching those criteria.
# Call it with query.py <file path> <query in json>
# For example: query.py fdmprinter.def.json "{ \"key\": \"layer_height\" }"
#

import os
import sys
import json

from UM.Settings.SettingDefinition import SettingDefinition, DefinitionPropertyType
from UM.Settings.Validator import Validator
from UM.Settings.DefinitionContainer import DefinitionContainer

if len(sys.argv) < 3:
    print("Usage: query.py [file] [query]")
    exit(1)

file_path = sys.argv[1]

# These are defined by Cura but we would still like to be able to query them.
SettingDefinition.addSupportedProperty("settable_per_mesh", DefinitionPropertyType.Any, default = True, read_only = True)
SettingDefinition.addSupportedProperty("settable_per_extruder", DefinitionPropertyType.Any, default = True, read_only = True)
SettingDefinition.addSupportedProperty("settable_per_meshgroup", DefinitionPropertyType.Any, default = True, read_only = True)
SettingDefinition.addSupportedProperty("settable_globally", DefinitionPropertyType.Any, default = True, read_only = True)
SettingDefinition.addSupportedProperty("limit_to_extruder", DefinitionPropertyType.Function, default = "-1")
SettingDefinition.addSupportedProperty("resolve", DefinitionPropertyType.Function, default = None)
SettingDefinition.addSettingType("extruder", None, str, Validator)

definition = DefinitionContainer(os.path.basename(file_path))
with open(file_path, encoding = "utf-8") as f:
    definition.deserialize(f.read())

query = json.loads(sys.argv[2])

results = definition.findDefinitions(**query)

for result in results:
    print("Found setting:", result.key)
