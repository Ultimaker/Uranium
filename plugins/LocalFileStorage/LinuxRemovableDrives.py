import threading

import glob
import time
import os
import subprocess

##  Support for removable devices on Linux.
#
#   TODO: This code uses the most basic interfaces for handling this.
#         We should instead use UDisks2 to handle mount/unmount and hotplugging events.


class LinuxRemovableDrivesThread(threading.Thread):
    def __init__(self, drives):
        super(LinuxRemovableDrivesThread, self).__init__()
        self.daemon = True
        self._driveManager = drives
        
    def run(self):
        while True:
            drives = {}
            for volume in glob.glob('/media/*'):
                if os.path.ismount(volume):
                    drives[os.path.basename(volume)] = volume
                elif volume == '/media/'+os.getenv('USER'):
                    for volume in glob.glob('/media/'+os.getenv('USER')+'/*'):
                        if os.path.ismount(volume):
                            drives[os.path.basename(volume)] =  volume

            for volume in glob.glob('/run/media/' + os.getenv('USER') + '/*'):
                if os.path.ismount(volume):
                    drives[os.path.basename(volume)] = volume

            self._driveManager.setDrives(drives)
            time.sleep(5)

class LinuxRemovableDrives(object):
    def __init__(self):
        super(LinuxRemovableDrives, self).__init__()
        self._thread = LinuxRemovableDrivesThread(self)
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

        p = subprocess.Popen(["umount", mount], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()

        if p.wait():
            print(output[0])
            print(output[1])
            return False
        else:
            return True
