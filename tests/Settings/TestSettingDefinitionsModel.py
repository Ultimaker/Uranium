from unittest.mock import MagicMock

import os
import uuid

import pytest

from PyQt5.QtCore import QVariant, QModelIndex, Qt

from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.Models.SettingDefinitionsModel import SettingDefinitionsModel


def createModel(definition = "multiple_settings.def.json"):
    model = SettingDefinitionsModel()

    # Get a basic definition container
    uid = str(uuid.uuid4())
    definition_container = DefinitionContainer(uid)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", definition),
              encoding="utf-8") as data:
        json = data.read()

    definition_container.deserialize(json)

    stack = ContainerStack(str(uuid.uuid4()))
    stack.addContainer(definition_container)

    model._stack = stack
    model.setShowAll(True)
    model.forceUpdate()
    model._updateVisibleRows()

    return model


test_validate_data = [
    {"attribute": "showAncestors", "value": True},
    {"attribute": "showAll", "value": True},
    {"attribute": "visibilityHandler", "value": MagicMock()},
    {"attribute": "exclude", "value": ["yay"]},
    {"attribute": "expanded", "value": ["yay"]},
    {"attribute": "filter", "value": {}},
]


@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    model = SettingDefinitionsModel()
    model._container = MagicMock()
    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # Attempt to set the value
    getattr(model, "set" + attribute)(data["value"])

    # Ensure that the value got set
    assert getattr(model, data["attribute"]) == data["value"]

    # Check properties via function calls


def test_getCount():
    model = createModel()

    assert model.count == 5
    assert model.categoryCount == 0


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

def test_collapseExpand():
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


def test_setAllExpandedVisible():
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
