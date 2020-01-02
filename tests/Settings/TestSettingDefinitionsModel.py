from unittest.mock import MagicMock, patch

import pytest
import os
import uuid
from UM.Settings.SettingRelation import RelationType

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


def test_getCountNoContainer():
    model = SettingDefinitionsModel()
    assert model.count == 0


def test_setVisible():
    model = createModel()
    assert model.visibleCount == 0

    model.show("test_setting_0")
    assert model.visibleCount == 1
    assert model.getVisible("test_setting_0")

    model.hide("test_setting_0")
    assert model.visibleCount == 0

    mocked_visibility_handler = MagicMock(name = "mocked_visibility_handler")
    mocked_visibility_handler.getVisible = MagicMock(return_value = set())
    model.setVisibilityHandler(mocked_visibility_handler)
    model.setAllVisible(True)

    # Ensure that the visibility handler got notified that things were changed.
    assert mocked_visibility_handler.setVisible.call_count == 1
    mocked_visibility_handler.setVisible.assert_called_with({'test_setting_2', 'test_setting_4', 'test_setting_3', 'test_setting_0', 'test_setting_1'})

    model.setAllVisible(False)
    assert mocked_visibility_handler.setVisible.call_count == 2
    mocked_visibility_handler.setVisible.assert_called_with(set())


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


def test_getRequires_noContainer():
    model = SettingDefinitionsModel()
    assert model.getRequires("blorp", "whatever") == []


def test_getRequires_noDefinition():
    model = SettingDefinitionsModel()
    model._container = MagicMock()
    model._container.findDefinitions = MagicMock(return_value=[])

    assert model.getRequires("blorp", "whatever") == []


def test_getRequires_withRelationsSet():
    model = SettingDefinitionsModel()
    model._container = MagicMock()

    relation_1 = MagicMock()
    relation_1.type = RelationType.RequiredByTarget
    relation_2 = MagicMock()
    relation_2.type = RelationType.RequiresTarget
    relation_2.role = "HERPDERP"
    relation_3 = MagicMock()
    relation_3.type = RelationType.RequiresTarget
    relation_3.role = "yay"
    relation_3.target.key = "key_3"
    relation_3.target.label = "label_3"

    mocked_definition_1 = MagicMock()
    mocked_definition_1.relations = [relation_1, relation_2, relation_3]

    model._container.findDefinitions = MagicMock(return_value=[mocked_definition_1])
    assert model.getRequires("blorp", "yay") == [{"key": "key_3", "label": "label_3"}]


def test_getRequiredBy_withRelationsSet():
    model = SettingDefinitionsModel()
    model._container = MagicMock()

    relation_1 = MagicMock()
    relation_1.type = RelationType.RequiredByTarget
    relation_2 = MagicMock()
    relation_2.type = RelationType.RequiresTarget
    relation_2.role = "HERPDERP"
    relation_3 = MagicMock()
    relation_3.type = RelationType.RequiredByTarget
    relation_3.role = "yay"
    relation_3.target.key = "key_3"
    relation_3.target.label = "label_3"

    mocked_definition_1 = MagicMock()
    mocked_definition_1.relations = [relation_1, relation_2, relation_3]

    model._container.findDefinitions = MagicMock(return_value=[mocked_definition_1])
    assert model.getRequiredBy("blorp", "yay") == [{"key": "key_3", "label": "label_3"}]


def test_getRequiredBy():
    model = createModel("functions.def.json")

    requires = model.getRequiredBy("test_setting_0", "value")
    assert requires[0]["key"] == "test_setting_1"


def test_getRequiredBy_unknownSetting():
    model = createModel("functions.def.json")
    model._getDefinitionsByKey = MagicMock(return_value = [])

    assert model.getRequiredBy("test_setting_0", "value") == []



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

    model.collapseRecursive("test_child_0")
    assert "test_setting" in model.expanded
    assert "test_child_0" not in model.expanded
    assert "test_child_1" in model.expanded

    model.collapseRecursive("test_setting")
    assert "test_setting" not in model.expanded
    assert "test_child_0" not in model.expanded
    assert "test_child_1" not in model.expanded


def test_expandRecursive_noContainer():
    model = SettingDefinitionsModel()
    model.expand = MagicMock()
    model.expandRecursive("whatever")

    assert model.expanded == []
    assert model.expand.call_count == 0


def test_expandRecursive_noDefinition():
    model = SettingDefinitionsModel()
    model._container = MagicMock()
    model._container.findDefinitions = MagicMock(return_value = False)
    model.expand = MagicMock()

    model.expandRecursive("whatever")

    assert model.expanded == []
    assert model.expand.call_count == 0


def test_collapse_no_container():
    model = SettingDefinitionsModel()
    model.collapseRecursive("whatever")

    assert model.expanded == []


@patch("UM.Application.Application.getInstance")
def test_setAllExpandedVisible(application):
    model = createModel("children.def.json")
    mocked_visibility_handler = MagicMock()
    mocked_visibility_handler.getVisible = MagicMock(return_value=set())
    model.setVisibilityHandler(mocked_visibility_handler)
    model.expand("test_setting")

    model.setAllExpandedVisible(True)
    assert mocked_visibility_handler.setVisible.call_count == 1
    mocked_visibility_handler.setVisible.assert_called_with({"test_setting"})

    model.setAllExpandedVisible(False)
    assert mocked_visibility_handler.setVisible.call_count == 2
    mocked_visibility_handler.setVisible.assert_called_with(set())


def test_setAlreadyVisbleSettingVisible():
    model = createModel("children.def.json")
    mocked_visibility_handler = MagicMock()
    mocked_visibility_handler.getVisible = MagicMock(return_value={"test_setting"})
    model.setVisibilityHandler(mocked_visibility_handler)
    model.setVisible("test_setting", True) # This setting is already visible (the visibility handler says so after all!)

    assert mocked_visibility_handler.setVisible.call_count == 0


def test_hideAlreadyHiddenSetting():
    model = createModel("children.def.json")
    mocked_visibility_handler = MagicMock()
    mocked_visibility_handler.getVisible = MagicMock(return_value=set())
    model.setVisibilityHandler(mocked_visibility_handler)
    model.setVisible("test_setting", False)  # This setting is already hidden (the visibility handler says so after all!)

    assert mocked_visibility_handler.setVisible.call_count == 0


def test_showUnknownSetting():
    model = createModel("children.def.json")
    mocked_visibility_handler = MagicMock()
    model.setVisibilityHandler(mocked_visibility_handler)
    model.setVisible("HERPDERP", True)
    assert mocked_visibility_handler.setVisible.call_count == 0


def test_showKnownHiddenSetting():
    model = createModel("children.def.json")
    mocked_visibility_handler = MagicMock()
    mocked_visibility_handler.getVisible = MagicMock(return_value=set())
    model.setVisibilityHandler(mocked_visibility_handler)
    model.setVisible("test_setting", True)

    assert mocked_visibility_handler.setVisible.call_count == 1
    mocked_visibility_handler.setVisible.assert_called_with({"test_setting"})


@patch("UM.Application.Application.getInstance")
def test_setExpanded(application):
    model = createModel("children.def.json")
    model.setExpanded(["*"])
    assert "test_setting" in model.expanded
    assert "test_child_0" not in model.expanded
    assert "test_child_1" not in model.expanded


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


def test_getIndexNoContainer():
    model = SettingDefinitionsModel()
    assert model.getIndex("blarg") == -1


def test_isDefinitionVisible_excluded():
    definition = MagicMock()
    definition.key = "blorp"
    model = createModel("single_setting.def.json")
    with patch("UM.Application.Application.getInstance"):
        model.setExclude(["blorp"])
    assert model._isDefinitionVisible(definition) == False


def test_isDefinitionVisible_excludedAncestors():
    definition = MagicMock()
    definition.key = "blorp"
    definition.getAncestors = MagicMock(return_value = {"zomg"})

    model = createModel("single_setting.def.json")
    with patch("UM.Application.Application.getInstance"):
        model.setExclude(["zomg"])

    assert model._isDefinitionVisible(definition) == False


def test_isDefinitionVisible_notExpanded():
    definition = MagicMock()
    definition.key = "blorp"

    model = createModel("single_setting.def.json")

    assert model._isDefinitionVisible(definition) == False


def test_isDefinitionVisible_settingNotVisible():
    definition = MagicMock()
    definition.key = "test_setting"
    definition.getAncestors = MagicMock(return_value=set())
    definition.parent = None
    model = createModel("single_setting.def.json")
    with patch("UM.Application.Application.getInstance"):
        model.expand("test_setting")
        model.setShowAll(False)

    assert model._isDefinitionVisible(definition) == False