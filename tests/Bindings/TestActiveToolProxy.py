from unittest import TestCase

from PyQt5.QtCore import QUrl
from unittest.mock import MagicMock, patch

from UM.Application import Application
from UM.Qt.Bindings.ActiveToolProxy import ActiveToolProxy
from UM.Tool import Tool


class TestActiveToolProxy(TestCase):
    proxy = None

    def setUp(self):
        # These objects only need to be set / created once.
        if TestActiveToolProxy.proxy is None:
            TestActiveToolProxy.proxy = ActiveToolProxy()

        self.tool = Tool()
        self.tool.setPluginId("test_tool_1")

    def tearDown(self):
        Application.getInstance().getController().setActiveTool("")

    def test_isValid(self):
        assert not self.proxy.valid
        Application.getInstance().getController().setActiveTool(self.tool)
        assert self.proxy.valid  # It is valid now

    def test_activeToolPanel(self):
        # There is no active tool, so it should be empty
        assert self.proxy.activeToolPanel == QUrl()

        with patch.object(self.tool, "getMetaData", MagicMock(return_value={"tool_panel": "derp"})):
            with patch("UM.PluginRegistry.PluginRegistry.getPluginPath", MagicMock(return_value = "OMG")):
                Application.getInstance().getController().setActiveTool(self.tool)
                assert self.proxy.activeToolPanel == QUrl.fromLocalFile("OMG/derp")
        # Try again with empty metadata
        with patch("UM.PluginRegistry.PluginRegistry.getMetaData", MagicMock(return_value={"tool": {}})):
            Application.getInstance().getController().setActiveTool("")
            Application.getInstance().getController().setActiveTool(self.tool)
            assert self.proxy.activeToolPanel == QUrl.fromLocalFile("")

    def test_triggerAction(self):
        # There is no active tool, so this is just a check to see if nothing breaks.
        self.proxy.triggerAction("derp")

        Application.getInstance().getController().setActiveTool(self.tool)

        # It is active now, but it doesn't have a function called "derp". Again, nothing should break.
        self.proxy.triggerAction("derp")

        self.tool.derp = MagicMock()

        self.proxy.triggerAction("derp")
        assert self.tool.derp.call_count == 1

    def test_triggerActionWithData(self):
        # There is no active tool, so this is just a check to see if nothing breaks.
        self.proxy.triggerActionWithData("derp", "omgzomg")

        Application.getInstance().getController().setActiveTool(self.tool)

        # It is active now, but it doesn't have a function called "derp". Again, nothing should break.
        self.proxy.triggerActionWithData("derp", "omgzomg")

        self.tool.derp = MagicMock()

        self.proxy.triggerActionWithData("derp", "omgzomg")
        self.tool.derp.assert_called_once_with("omgzomg")

    def test_properties(self):
        # There is no active tool, so this is just a check to see if nothing breaks.
        self.proxy.setProperty("derp", "omgzomg")

        self.tool.setExposedProperties("Bla", "beep")
        self.tool.getBla = MagicMock(return_value ="BlaBla")
        self.tool.setBla = MagicMock()
        self.tool.beep = ""
        self.tool.getbeep = MagicMock()

        Application.getInstance().getController().setActiveTool(self.tool)
        assert self.proxy.properties.getValue("Bla") == "BlaBla"  # The default
        self.proxy.forceUpdate()
        self.proxy.setProperty("Bla", "OMGZOMG")
        self.proxy.setProperty("beep", "whoo")
        self.tool.setBla.assert_called_once_with("OMGZOMG")

        assert self.tool.beep == "whoo" # If no set is found, but the property itself it should still be changed.
