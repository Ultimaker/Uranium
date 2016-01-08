# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

def getMetaData():
    return { "name": "OldTestPlugin" }

def register(app):
    app.registerTestPlugin("OldTestPlugin")