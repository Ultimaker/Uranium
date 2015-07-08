# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.OutputDevice.OutputDevice import OutputDevice
from UM.Message import Message

from . import RemovableDrivePlugin

import glob
import os
import subprocess

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

##  Support for removable devices on Linux.
#
#   TODO: This code uses the most basic interfaces for handling this.
#         We should instead use UDisks2 to handle mount/unmount and hotplugging events.

class LinuxRemovableDrivePlugin(RemovableDrivePlugin.RemovableDrivePlugin):
    def checkRemovableDrives(self):
        drives = {}
        for volume in glob.glob("/media/*"):
            if os.path.ismount(volume):
                drives[volume] = os.path.basename(volume)
            elif volume == "/media/"+os.getenv("USER"):
                for volume in glob.glob("/media/"+os.getenv("USER")+"/*"):
                    if os.path.ismount(volume):
                        drives[volume] = os.path.basename(volume)

        for volume in glob.glob("/run/media/" + os.getenv("USER") + "/*"):
            if os.path.ismount(volume):
                drives[volume] = os.path.basename(volume)

        return drives

    def createOutputDevice(self, key, value):
        return LinuxRemovableDriveOutputDevice(key, value)

class LinuxRemovableDriveOutputDevice(OutputDevice):
    def __init__(self, device_id, device_name):
        super().__init__(device_id)

        self.setName(device_name)
        self.setShortDescription(catalog.i18nc("", "Save to Removable Drive"))
        self.setDescription(catalog.i18nc("", "Save to Removable Drive {0}").format(device_name))
        self.setIconName("save_sd")
        self.setSupportedMimeTypes(["text/x-gcode"])
        self.setPriority(1)

    def requestWrite(self, node):
        pass

    def eject(self):
        p = subprocess.Popen(["umount", self.getId()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()

        return_code = p.wait()
        if return_code != 0:
            message = Message("Failed to eject {0}. Maybe it is still in use?".format(self.getName()))
            message.show()
            return False
        else:
            message = Message("Ejected {0}. You can now safely remove the card.".format(self.getName()))
            message.show()
            return True
