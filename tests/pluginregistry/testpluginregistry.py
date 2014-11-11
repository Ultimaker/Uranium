import unittest
import os

from Cura.Application import Application
from Cura.PluginRegistry import PluginRegistry

class TestApplication(Application):
    def registerTestPlugin(self, name):
        self._testPlugin = name
        
    def getTestPlugin(self):
        return self._testPlugin

class TestPluginRegistry(unittest.TestCase):
    # Called before the first testfunction is executed
    def setUp(self):
        self._registry = PluginRegistry()
        self._registry.addPluginLocation(".")
        self._app = TestApplication()
        self._registry.setApplication(self._app)

    # Called after the last testfunction was executed
    def tearDown(self):
        pass

    def test_MetaData(self):
        metaData = self._registry.getMetaData("TestPlugin")
        self.assertEqual("TestPlugin", metaData["name"])
        self.assertEqual("test", metaData["type"])

    def test_Load(self):
        self._registry.loadPlugin("TestPlugin")
        self.assertEqual("TestPlugin", self._app.getTestPlugin())

if __name__ == "__main__":
    unittest.main()
