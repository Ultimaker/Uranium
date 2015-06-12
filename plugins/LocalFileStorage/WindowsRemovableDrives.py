# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, SignalEmitter

import threading
import string

from ctypes import windll
import ctypes
import time
import os
import subprocess

## Removable drive support for windows
class WindowsRemovableDrives(threading.Thread, SignalEmitter):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.start()
        
    drivesChanged = Signal()
        
    def run(self):
        while True:
            drives = {}

            bitmask = windll.kernel32.GetLogicalDrives()
            # Check possible drive letters, from A to Z
            # Note: using ascii_uppercase because we do not want this to change with locale!
            for letter in string.ascii_uppercase:
                # Do we really want to skip A and B?
                # GetDriveTypeA explicitly wants a byte array of type ascii. It will accept a string, but this wont work
                if letter != "A" and letter != "B" and bitmask & 1 and windll.kernel32.GetDriveTypeA(bytes((letter + ":/"),"ascii")) == 2:
                    volume_name = ""
                    name_buffer = ctypes.create_unicode_buffer(1024)
                    filesystem_buffer = ctypes.create_unicode_buffer(1024)
                    if windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(letter + ":/"), name_buffer, ctypes.sizeof(name_buffer), None, None, None, filesystem_buffer, ctypes.sizeof(filesystem_buffer)) == 0:
                        volume_name = name_buffer.value
                    if volume_name == "":
                        volume_name = "Removable Drive"

                    # Certain readers will report themselves as a volume even when there is no card inserted, but will show an
                    # "No volume in drive" warning when trying to call GetDiskFreeSpace. However, they will not report a valid
                    # filesystem, so we can filter on that. In addition, this excludes other things with filesystems Windows
                    # does not support.
                    if filesystem_buffer.value == "":
                        continue

                    # Check for the free space. Some card readers show up as a drive with 0 space free when there is no card inserted.
                    freeBytes = ctypes.c_longlong(0)
                    if windll.kernel32.GetDiskFreeSpaceExA(bytes((letter + ":/"),"ascii"), ctypes.byref(freeBytes), None, None) == 0:
                        continue
                    if freeBytes.value < 1:
                        continue
                    
                    drives["%s (%s:)" % (volume_name, letter)] = letter + ":/"
                bitmask >>= 1

            self.drivesChanged.emit(drives)
            time.sleep(5)

    def ejectDrive(self, drive):
        try:
            mount = self._drives[drive]
        except KeyError:
            return

        #TODO: This really should not be calling magic external executables that are not contained in the source
        #or properly documented. Since we have WinAPI stuff here anyway, we could just use the WinAPI functions for
        #ejecting.
        #
        #See http://support2.microsoft.com/?scid=kb%3Ben-us%3B165721&x=18&y=13 for how to do it with just WinAPI
        command = [os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "EjectMedia.exe")), driveName]
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = su
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        output = p.communicate()

        if p.wait():
            print(output[0])
            print(output[1])
            return False
        else:
            return True
