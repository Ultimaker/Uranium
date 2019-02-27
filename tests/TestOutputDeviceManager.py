from unittest.mock import MagicMock

from UM.OutputDevice.OutputDevice import OutputDevice
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin


def test_addRemoveOutputDevice():
    manager = OutputDeviceManager()

    manager.outputDevicesChanged.emit = MagicMock()
    manager.activeDeviceChanged.emit = MagicMock()

    output_device = OutputDevice("test_device_one")
    output_device.setPriority(2)
    output_device_2 = OutputDevice("test_device_two")
    output_device_2.setPriority(9001)

    manager.addOutputDevice(output_device)
    assert manager.outputDevicesChanged.emit.call_count == 1
    assert manager.getOutputDevice("test_device_one") == output_device

    # Our new device is also the one with the highest priority (as it's the only one). So it should be active.
    assert manager.getActiveDevice() == output_device

    manager.addOutputDevice(output_device)
    assert manager.outputDevicesChanged.emit.call_count == 1

    manager.addOutputDevice(output_device_2)
    assert manager.outputDevicesChanged.emit.call_count == 2
    # We added a new device with a higher priority, so that one should be the active one
    assert manager.getActiveDevice() == output_device_2

    assert set([output_device, output_device_2]) == set(manager.getOutputDevices())
    assert set(["test_device_one", "test_device_two"]) == set(manager.getOutputDeviceIds())

    # Try to manually change the active device a few times
    manager.setActiveDevice("test_device_one")
    assert manager.activeDeviceChanged.emit.call_count == 3
    assert manager.getActiveDevice() == output_device
    manager.setActiveDevice("test_device_two")
    assert manager.activeDeviceChanged.emit.call_count == 4
    assert manager.getActiveDevice() == output_device_2

    # As usual, doing it twice shouldn't cause more updates
    manager.setActiveDevice("test_device_two")
    assert manager.activeDeviceChanged.emit.call_count == 4
    manager.setActiveDevice("Whatever")  # Simply shouldn't cause issues.

    # Time to remove the device again
    assert manager.removeOutputDevice("test_device_two")
    assert manager.getActiveDevice() == output_device
    assert manager.outputDevicesChanged.emit.call_count == 3
    # Trying to remove it again should return false
    assert not manager.removeOutputDevice("test_device_two")
    assert manager.outputDevicesChanged.emit.call_count == 3


def test_addRemoveOutputDevicePlugin():
    manager = OutputDeviceManager()
    plugin_1 = OutputDevicePlugin()
    plugin_1.setPluginId("plugin_one")

    plugin_1.start = MagicMock()
    plugin_1.stop = MagicMock()

    manager.addOutputDevicePlugin(plugin_1)
    assert manager.getOutputDevicePlugin("plugin_one") == plugin_1
    # Outputdevice manager wasn't started, so the start of the plugin should not be called
    assert plugin_1.start.call_count == 0

    # So once we do, it should be called.
    manager.start()
    assert plugin_1.start.call_count == 1

    # Adding it again shouldn't cause the start to be called again!
    manager.addOutputDevicePlugin(plugin_1)
    assert plugin_1.start.call_count == 1

    manager.removeOutputDevicePlugin("plugin_one")
    assert manager.getOutputDevicePlugin("plugin_one") is None
    assert plugin_1.start.call_count == 1

    # And removing it again shouldn't cause issues.
    manager.removeOutputDevicePlugin("plugin_two")
    assert plugin_1.start.call_count == 1

    # As the default output device plugin is an interface, the start and stop will raise exceptions.
    # but the outputdevice manager should be robust against that, so even in that case it shouldn't fail!
    plugin_2 = OutputDevicePlugin()
    plugin_2.setPluginId("plugin_two")
    manager.addOutputDevicePlugin(plugin_2)
    manager.removeOutputDevicePlugin("plugin_two")

