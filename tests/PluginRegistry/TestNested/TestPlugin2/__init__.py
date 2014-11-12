def getMetaData():
    return { "name": "TestPlugin2", "type": "test" }

def register(app):
    app.registerTestPlugin("TestPlugin2")