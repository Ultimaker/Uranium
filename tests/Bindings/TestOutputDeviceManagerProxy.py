from unittest import TestCase

from unittest.mock import MagicMock, patch

from UM.Qt.Bindings.OutputDeviceManagerProxy import OutputDeviceManagerProxy


class TestOutputDeviceManagerProxy(TestCase):
    proxy = None
    mock_application = None
    mocked_device_manager = None

    def setUp(self):
        # These objects only need to be set / created once.
        if TestOutputDeviceManagerProxy.proxy is None:
            TestOutputDeviceManagerProxy.mock_application = MagicMock()
            TestOutputDeviceManagerProxy.mocked_device_manager = MagicMock()
            self.mock_application.getOutputDeviceManager = MagicMock(return_value = self.mocked_device_manager)
            with patch("UM.Application.Application.getInstance", MagicMock(return_value=self.mock_application)):
                TestOutputDeviceManagerProxy.proxy = OutputDeviceManagerProxy()

    def tearDown(self):
        pass

    def test_startAndRefreshDiscovery(self):
        self.proxy.startDiscovery()
        assert self.mocked_device_manager.startDiscovery.call_count == 1

        self.proxy.refreshConnections()
        assert self.mocked_device_manager.refreshConnections.call_count == 1