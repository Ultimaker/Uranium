def getMetaData():
    return { "name": "TestPlugin", "type": "test" }

def register(app):
    app.registerTestPlugin("TestPlugin")