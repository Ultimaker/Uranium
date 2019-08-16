from unittest.mock import MagicMock, patch

import pytest
import os
import uuid

from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.Models.SettingDefinitionsModel import SettingDefinitionsModel
from PyQt5.QtCore import QVariant, QModelIndex, Qt


def createModel(definition = "multiple_settings.def.json"):
    model = SettingDefinitionsModel()

    # Get a basic definition container
    uid = str(uuid.uuid4())
    definition_container = DefinitionContainer(uid)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", definition),
              encoding="utf-8") as data:
        json = data.read()
    definition_container._updateSerialized = MagicMock(return_value = json)
    definition_container.deserialize(json)
    model._container = definition_container
    with patch("UM.Application.Application.getInstance"):
        model.setShowAll(True)
    model.forceUpdate()
    model._updateVisibleRows()

    return model


test_validate_data = [
    {"attribute": "showAncestors", "value": True},
    {"attribute": "containerId", "value": "omg"},
    {"attribute": "showAll", "value": True},
    {"attribute": "visibilityHandler", "value": MagicMock()},
    {"attribute": "exclude", "value": ["yay"]},
    {"attribute": "expanded", "value": ["yay"]},
    {"attribute": "filter", "value": {"zomg": "zomg"}},
    {"attribute": "rootKey", "value": "Whatevah"}
]

@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    model = SettingDefinitionsModel()
    model._scheduleUpdateVisibleRows = MagicMock()
    model._container = MagicMock()
    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # Attempt to set the value
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance"):
        getattr(model, "set" + attribute)(data["value"])

    # Ensure that the value got set
    assert getattr(model, data["attribute"]) == data["value"]


def test_setRootKeyUnknownDefinition():
    model = SettingDefinitionsModel()
    model._container = MagicMock()
    model._container.findDefinitions = MagicMock(return_value = [])
    model.rootKeyChanged = MagicMock()
    model.setRootKey("Blorp")
    assert model.rootKeyChanged.emit.call_count == 0


def test_getCount():
    model = createModel()

    assert model.count == 6
    assert model.categoryCount == 1


def test_setVisible():
    model = createModel()
    assert model.visibleCount == 0

    model.show("test_setting_0")
    assert model.visibleCount == 1
    assert model.getVisible("test_setting_0")

    model.hide("test_setting_0")
    assert model.visibleCount == 0

    mocked_visibility_handler = MagicMock()
    model.setVisibilityHandler(mocked_visibility_handler)
    model.setAllVisible(True)
    # Ensure that the visibility handler got notified that things were changed.

    assert mocked_visibility_handler.setVisible.call_count == 1


def test_disconnectVisibilityHandler():
    model = SettingDefinitionsModel()
    visibility_handler = MagicMock()
    visibility_handler_2 = MagicMock()
    model.setVisibilityHandler(visibility_handler)
    assert visibility_handler.visibilityChanged.disconnect.call_count == 0

    model.setVisibilityHandler(visibility_handler_2)

    assert visibility_handler.visibilityChanged.disconnect.call_count > 0


def test_getIndex():
    model = createModel()
    # This setting doesn't exist
    assert model.getIndex("set_setting_0") == -1
    assert model.getIndex("test_setting_0") == 0


def test_getRequires():
    model = createModel("functions.def.json")

    requires = model.getRequires("test_setting_1", "value")
    assert requires[0]["key"] == "test_setting_0"


def test_getRequiredBy():
    model = createModel("functions.def.json")

    requires = model.getRequiredBy("test_setting_0", "value")
    assert requires[0]["key"] == "test_setting_1"


@patch("UM.Application.Application.getInstance")
def test_collapseExpand(application):
    model = createModel("children.def.json")

    model.expand("test_setting")
    assert "test_setting" in model.expanded
    assert "test_child_0" not in model.expanded
    assert "test_child_1" not in model.expanded

    model.expandRecursive("test_setting")
    assert "test_setting" in model.expanded
    assert "test_child_0" in model.expanded
    assert "test_child_1" in model.expanded

    model.collapse("test_child_0")
    assert "test_setting" in model.expanded
    assert "test_child_0" not in model.expanded
    assert "test_child_1" in model.expanded

    model.collapse("test_setting")
    assert "test_setting" not in model.expanded
    assert "test_child_0" not in model.expanded
    assert "test_child_1" not in model.expanded


@patch("UM.Application.Application.getInstance")
def test_setAllExpandedVisible(application):
    model = createModel("children.def.json")
    mocked_visibility_handler = MagicMock()
    model.setVisibilityHandler(mocked_visibility_handler)
    model.expand("test_setting")

    model.setAllExpandedVisible(True)
    assert mocked_visibility_handler.setVisible.call_count == 1


def test_dataHappy():
    model = createModel("single_setting.def.json")

    assert model.data(model.index(0, 0), model.KeyRole) == "test_setting"
    assert model.data(model.index(0, 0), model.DepthRole) == 0
    assert model.data(model.index(0, 0), model.ExpandedRole) == False
    assert model.data(model.index(0, 0), model.VisibleRole) == False


def test_dataUnhappy():
    model = createModel("single_setting.def.json")
    # Out of bounds
    assert model.data(model.index(250, 0), model.KeyRole) == QVariant()

    # Invalid index
    assert model.data(QModelIndex(), model.KeyRole) == QVariant()

    # Unknown role
    assert model.data(model.index(0, 0), Qt.UserRole + 100) == QVariant()

    empty_model = SettingDefinitionsModel()
    assert empty_model.data(model.index(0, 0), model.KeyRole) == QVariant()

