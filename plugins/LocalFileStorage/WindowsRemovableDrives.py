import threading
import string

from ctypes import windll
import ctypes
import time
import os
import subprocess

## Removable drive support for windows

class WindowsRemovableDriveThread(threading.Thread):
    def __init__(self, drives):
        super().__init__()
        self.daemon = True
        self._driveManager = drives
        
    def run(self):
        while True:
            drives = {}
            
            bitmask = windll.kernel32.GetLogicalDrives()
            # Check possible drive letters, from A to Z
            # Note: using ascii_uppercase because we do not want this to change with locale!
            for letter in string.ascii_uppercase:
                # Do we really want to skip A and B?
                if letter != 'A' and letter != 'B' and bitmask & 1 and windll.kernel32.GetDriveTypeA(letter + ':/') == 2:
                    volume_name = ''
                    name_buffer = ctypes.create_unicode_buffer(1024)
                    if windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(letter + ':/'), name_buffer, ctypes.sizeof(name_buffer), None, None, None, None, 0) == 0:
                        volume_name = name_buffer.value
                    if volume_name == '':
                        volume_name = 'Removable Drive'

                    # Check for the free space. Some card readers show up as a drive with 0 space free when there is no card inserted.
                    freeBytes = ctypes.c_longlong(0)
                    if windll.kernel32.GetDiskFreeSpaceExA(letter + ':/', ctypes.byref(freeBytes), None, None) == 0:
                        continue
                    if freeBytes.value < 1:
                        continue
                    
                    drives['%s (%s:)' % (volume_name, letter)] = letter + ':/'
                bitmask >>= 1
                
            self._driveManager.setDrives(drives)
            time.sleep(5)


class WindowsRemovableDrives(object):
    def __init__(self):
        super(WindowsRemovableDrives, self).__init__()
        self._thread = WindowsRemovableDriveThread(self)
        self._thread.start()
        self._drives = {}

    def setDrives(self, drives):
        self._drives = drives

    def hasDrives(self):
        return len(self._drives) > 0

    def getDrives(self):
        return self._drives

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
        command = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'EjectMedia.exe')), driveName]
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        output = p.communicate()

        if p.wait():
            print(output[0])
            print(output[1])
            return False
        else:
            return True
