from UM.PluginObject import PluginObject
import pytest


def test_getId_unhappy():
    plugin = PluginObject()
    with pytest.raises(ValueError):
        plugin.getPluginId()  # We didn't set an id yet.


def test_getVersion_unhappy():
    plugin = PluginObject()
    with pytest.raises(ValueError):
        plugin.getVersion()  # We didn't set a version yet.


def test_getVersion_happy():
    plugin = PluginObject()
    plugin.setVersion("12.0.0")
    assert plugin.getVersion() == "12.0.0"


def test_getId_happy():
    plugin = PluginObject()
    plugin.setPluginId("UltiBot")
    assert plugin.getPluginId() == "UltiBot"