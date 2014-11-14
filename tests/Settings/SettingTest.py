import unittest
from Cura.Settings.Setting import Setting
from Cura.Settings.SettingsCategory import SettingsCategory
from Cura.Settings.MachineSettings import MachineSettings
class SettingTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self._setting = Setting('TestSetting',10,'int')
        self._machine_settings = MachineSettings()
        category = SettingsCategory('TestCategory')
        self._machine_settings.addSettingsCategory(category)


    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_GetSettingByKey(self):
        
        pass

    def test_Category(self):
        pass

    def test_ValidatorTest(self):
        pass

if __name__ == "__main__":
    unittest.main()
