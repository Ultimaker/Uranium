from unittest.mock import MagicMock, patch

from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.Models.SettingPropertyProvider import SettingPropertyProvider
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.SettingInstance import SettingInstance
from UM.Settings.Validator import ValidatorState


def test_setContainerStack(container_registry):
    setting_property_provider = SettingPropertyProvider()
    container_stack = ContainerStack("test!")

    setting_property_provider.containerStackChanged = MagicMock()
    setting_property_provider.setContainerStack(container_stack)
    assert setting_property_provider.containerStackChanged.emit.call_count == 1

    # Should not do anything (since its' the same stack)
    setting_property_provider.setContainerStack(container_stack)
    assert setting_property_provider.containerStackChanged.emit.call_count == 1
    assert setting_property_provider.containerStack == container_stack

    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value = container_registry)):
        setting_property_provider.setContainerStackId("test")
        # The registry doesn't have any containers, so this shouldn't have any effect.
        assert setting_property_provider.containerStackId == "test!"

        container_registry.addContainer(ContainerStack("test"))
        setting_property_provider.setContainerStackId("test")

        # Since it is added now, it should change.
        assert setting_property_provider.containerStackId == "test"


def test_valueChanges(container_registry):
    setting_property_provider = SettingPropertyProvider()

    # First create the basics; A container stack that will hold 2 instance containers and a single definition container
    container_stack = ContainerStack("test!")
    instance_container = InstanceContainer("data")
    second_instance_container = InstanceContainer("data2")
    definition_container = DefinitionContainer("foo")

    # Create a setting definition for our one and only setting!
    setting_definition = SettingDefinition("test_setting")
    setting_definition._deserialize_dict({"value": 10, "label": "blorp", "type": "float", "description": "nah", "maximum_value": 23, "maximum_value_warning": 21, "enabled": "test_setting != 20"})
    definition_container.addDefinition(setting_definition)

    # Make a single setting instance for our one and only setting.
    setting_instance = SettingInstance(setting_definition, instance_container)
    setting_instance.setProperty("value", 20)
    setting_instance.setProperty("enabled", False)
    instance_container.addInstance(setting_instance)

    # Make a setting instance that lives in our second instance_container
    setting_instance2 = SettingInstance(setting_definition, second_instance_container)
    second_instance_container.addInstance(setting_instance2)

    # Now that both containers are done, actually add them.
    container_stack.addContainer(definition_container)
    container_stack.addContainer(second_instance_container)
    container_stack.addContainer(instance_container)

    setting_property_provider.setContainerStack(container_stack)
    setting_property_provider.setKey("test_setting")
    assert setting_property_provider.key == "test_setting"

    assert setting_property_provider.getPropertyValue("value", 0) == 20

    setting_property_provider.setWatchedProperties(["enabled", "value", "validationState"])
    setting_property_provider._update()
    assert setting_property_provider.watchedProperties == ["enabled", "value", "validationState"]
    assert setting_property_provider.properties.value("enabled") == "False"
    assert setting_property_provider.properties.value("value") == "20"

    # Validator state is a special property that gets added based on the type and the value
    assert setting_property_provider.properties.value("validationState") == str(ValidatorState.Valid)

    # Set the property value to something that will trigger a warning
    setting_property_provider.setPropertyValue("value", 22)
    assert setting_property_provider.properties.value("validationState") == str(ValidatorState.MaximumWarning)
    assert setting_property_provider.getPropertyValue("value", 0) == 22
    # The setting doesn't exist in our second instance container, so this should be None
    assert setting_property_provider.getPropertyValue("value", 1) is None

    # Set the property value to something that will trigger an error
    setting_property_provider.setPropertyValue("value", 25)
    # The Qtimer that we use to prevent flooding doesn't work in tests, so tickle the change manually.
    setting_property_provider._update()

    assert setting_property_provider.properties.value("validationState") == str(ValidatorState.MaximumError)

    # We now ask for the second instance container to be targeted
    setting_property_provider.setStoreIndex(1)
    assert setting_property_provider.storeIndex == 1

    setting_property_provider.setPropertyValue("value", 2)
    setting_property_provider._update()
    # So now we should see a change in that instance container
    assert setting_property_provider.getPropertyValue("value", 1) == 2
    # But not if we ask the provider, because the container above it still has a 25 as value!
    assert setting_property_provider.getPropertyValue("value", 0) == 25

    assert setting_property_provider.stackLevels == [0, 1, 2]

    # We're asking for an index that doesn't exist.
    assert setting_property_provider.getPropertyValue("value", 2000) is None

    # The value is used, so the property must be true
    assert setting_property_provider.isValueUsed

    # Try to remove the setting from the container
    setting_property_provider.removeFromContainer(0)
    assert setting_property_provider.getPropertyValue("value", 0) is None

    # Ensure that a weird index doesn't break
    setting_property_provider.removeFromContainer(90001)


def test_stackLevelsNoStack():
    setting_property_provider = SettingPropertyProvider()
    assert setting_property_provider.stackLevels == [-1]


def test_isValueUsedNoStack():
    setting_property_provider = SettingPropertyProvider()
    assert setting_property_provider.isValueUsed == False


def test_containerStackIdNoStack():
    setting_property_provider = SettingPropertyProvider()
    assert setting_property_provider.containerStackId == ""


def test_getSetRemoveUnusedValue():
    setting_property_provider = SettingPropertyProvider()
    setting_property_provider.removeUnusedValueChanged = MagicMock()

    setting_property_provider.setRemoveUnusedValue(False)
    assert setting_property_provider.removeUnusedValue == False
    assert setting_property_provider.removeUnusedValueChanged.emit.call_count == 1

    setting_property_provider.setRemoveUnusedValue(False)
    assert setting_property_provider.removeUnusedValueChanged.emit.call_count == 1