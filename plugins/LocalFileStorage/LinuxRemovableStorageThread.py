import threading

import glob
import time
import os
    
class LinuxRemovableStorageThread(threading.Thread):
    def __init__(self, app):
        super(LinuxRemovableStorageThread, self).__init__()
        self.daemon = True
        self._app = app
        
    def run(self):
        while True:
            hasDrive = False
            for volume in glob.glob('/media/*'):
                if os.path.ismount(volume):
                    hasDrive = True
                elif volume == '/media/'+os.getenv('USER'):
                    for volume in glob.glob('/media/'+os.getenv('USER')+'/*'):
                        if os.path.ismount(volume):
                            hasDrive = True
            else:
                for volume in glob.glob('/run/media/' + os.getenv('USER') + '/*'):
                    if os.path.ismount(volume):
                        hasDrive = True
            
            if hasDrive:
                print "Found removable device"
                self._app.getStorageDevice("local").setStorageProperty("removableDevice", True)
            else:
                print "No removable devices"
                self._app.getStorageDevice("local").setStorageProperty("removableDevice", False)
                
            time.sleep(5)