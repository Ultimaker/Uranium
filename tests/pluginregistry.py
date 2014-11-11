#!/usr/bin/env python2

import Cura.PluginRegistry

p = Cura.PluginRegistry.PluginRegistry()
p.addPluginLocation("plugins")

p._populateMetaData()
p.loadPlugin("ExamplePlugin")

print(p.getMetaData("ExamplePlugin"))

