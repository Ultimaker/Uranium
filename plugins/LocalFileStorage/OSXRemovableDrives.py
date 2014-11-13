import threading

import subprocess
import time
import os
    
try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

## Support for removable devices on Mac OSX

class OSXRemovableDriveThread(threading.Thread):
    def __init__(self, drives):
        super(OSXRemovableDrive, self).__init__()
        self.daemon = True
        self._driveManager = drives

    def run(self):
        while True:
            drives = {}
            p = subprocess.Popen(['system_profiler', 'SPUSBDataType', '-xml'], stdout=subprocess.PIPE)
            xml = ElementTree.fromstring(p.communicate()[0])
            p.wait()

            xml = self._parseStupidPListXML(xml)
            for dev in self._findInTree(xml, 'Mass Storage Device'):
                if 'removable_media' in dev and dev['removable_media'] == 'yes' and 'volumes' in dev and len(dev['volumes']) > 0:
                    for vol in dev['volumes']:
                        if 'mount_point' in vol:
                            volume = vol['mount_point']
                            drives[os.path.basename(volume)] = volume

            p = subprocess.Popen(['system_profiler', 'SPCardReaderDataType', '-xml'], stdout=subprocess.PIPE)
            xml = ElementTree.fromstring(p.communicate()[0])
            p.wait()

            xml = self._parseStupidPListXML(xml)
            for entry in xml:
                if '_items' in entry:
                    for item in entry['_items']:
                        for dev in item['_items']:
                            if 'removable_media' in dev and dev['removable_media'] == 'yes' and 'volumes' in dev and len(dev['volumes']) > 0:
                                for vol in dev['volumes']:
                                    if 'mount_point' in vol:
                                        volume = vol['mount_point']
                                        drives[os.path.basename(volume)] = volume

            self._driveManager.setDrives(drives)
            time.sleep(5)

    def _parseStupidPListXML(self, e):
        if e.tag == 'plist':
            return self._parseStupidPListXML(list(e)[0])
        if e.tag == 'array':
            ret = []
            for c in list(e):
                ret.append(self._parseStupidPListXML(c))
            return ret
        if e.tag == 'dict':
            ret = {}
            key = None
            for c in list(e):
                if c.tag == 'key':
                    key = c.text
                elif key is not None:
                    ret[key] = self._parseStupidPListXML(c)
                    key = None
            return ret
        if e.tag == 'true':
            return True
        if e.tag == 'false':
            return False
        return e.text
    
    def _findInTree(self, t, n):
        ret = []
        if type(t) is dict:
            if '_name' in t and t['_name'] == n:
                ret.append(t)
            for k, v in t.items():
                ret += self._findInTree(v, n)
        if type(t) is list:
            for v in t:
                ret += self._findInTree(v, n)
        return ret

class OSXRemovableDrives(object):
    def __init__(self):
        super(OSXRemovableDrives, self).__init__()
        self._thread = OSXRemovableDriveThread(self)
        self._thread.start()
        self._drives = {}

    def setDrives(self, drives):
        self._drives = drives

    def getDrives(self):
        return self._drives

    def hasDrives(self):
        return len(self._drives) > 0

    def ejectDrive(self, drive):
        #TODO: Check if this needs drive name or mount point
        try:
            mount = self._drives[drive]
        except KeyError:
            return

        p = subprocess.Popen(["diskutil", "eject", mount], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()

        if p.wait():
            print output[0]
            print output[1]
            return False
        else:
            return True
