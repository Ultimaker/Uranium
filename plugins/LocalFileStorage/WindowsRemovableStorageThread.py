import threading
import string

from ctypes import windll
import ctypes
import time

# Thread that checks to see if a removable storage device was inserted.
class WindowsRemoveableStorageThread(threading.Thread):
    def __init__(self, app):
        super(WindowsRemoveableStorageThread, self).__init__()
        self.daemon = True
        self._app = app
        
    def run(self):
        while True:
            hasDrive = False
            
            bitmask = windll.kernel32.GetLogicalDrives()
            
            # Check possible drive letters, from A to Z
            # Note: using ascii_uppercase because we do not want this to change with locale!
            for letter in string.ascii_uppercase:
                if letter != 'A' and letter != 'B' and bitmask & 1 and windll.kernel32.GetDriveTypeA(letter + ':/') == 2:
                    volume_name = ''
                    name_buffer = ctypes.create_unicode_buffer(1024)
                    if windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(letter + ':/'), name_buffer, ctypes.sizeof(name_buffer), None, None, None, None, 0) == 0:
                        volume_name = name_buffer.value
                    if volume_name == '':
                        volume_name = 'NO NAME'

                    # Check for the free space. Some card readers show up as a drive with 0 space free when there is no card inserted.
                    freeBytes = ctypes.c_longlong(0)
                    if windll.kernel32.GetDiskFreeSpaceExA(letter + ':/', ctypes.byref(freeBytes), None, None) == 0:
                        continue
                    if freeBytes.value < 1:
                        continue
                    
                    hasDrive = True
                bitmask >>= 1
                
            if hasDrive:
                self._app.getStorageDevice("local").setStorageProperty("removableDevice", True)
            else:
                self._app.getStorageDevice("local").setStorageProperty("removableDevice", False)
                
            time.sleep(5)