from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from UM.Preferences import Preferences


class SettingPreferenceVisibilityHandler(QObject):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)
        self._visible = set()
        self._visibility_string = ""

        Preferences.getInstance().preferenceChanged.connect(self._onPreferencesChanged)
        self._onPreferencesChanged("general/visible_settings")

    visibilityChanged = pyqtSignal()

    def _onPreferencesChanged(self, name):
        if name != "general/visible_settings":
            return
        new_visible = set()
        self._visibility_string = Preferences.getInstance().getValue("general/visible_settings")
        for key in self._visibility_string.split(";"):
            new_visible.add(key.strip())

        self._visible = new_visible
        self.visibilityChanged.emit()

    def setVisible(self, visible):
        self._visible = visible
        preference = ";".join(self._visible)
        Preferences.getInstance().setValue("general/visible_settings", preference)

    def getVisible(self):
        return self._visible

