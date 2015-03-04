from UM.Signal import Signal, SignalEmitter

import threading
import glob
import time
import os
import subprocess

##  Support for removable devices on Linux.
#
#   TODO: This code uses the most basic interfaces for handling this.
#         We should instead use UDisks2 to handle mount/unmount and hotplugging events.

class LinuxRemovableDrives(threading.Thread, SignalEmitter):
    def __init__(self):
        super(LinuxRemovableDrives, self).__init__()
        self.setDaemon(True)
        self.start()

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

            self.drivesChanged.emit(drives)
            time.sleep(1)

    drivesChanged = Signal()

    def ejectDrive(self, drive):
        p = subprocess.Popen(["umount", drive], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()

        if p.wait():
            print(output[0])
            print(output[1])
            return False
        else:
            return True
