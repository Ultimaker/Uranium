# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Application import Application
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.i18n import i18nCatalog
from .LocalFileOutputDevice import LocalFileOutputDevice

catalog = i18nCatalog("uranium")


class LocalFileOutputDevicePlugin(OutputDevicePlugin):
    """Implements an OutputDevicePlugin that provides a single instance of LocalFileOutputDevice"""

    def __init__(self):
        super().__init__()

        Application.getInstance().getPreferences().addPreference("local_file/last_used_type", "")
        Application.getInstance().getPreferences().addPreference("local_file/dialog_save_path", "")

    def start(self):
        self.getOutputDeviceManager().addOutputDevice(LocalFileOutputDevice())

    def stop(self):
        self.getOutputDeviceManager().removeOutputDevice("local_file")