# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

import threading

import subprocess
import time
import os

from UM.Signal import Signal, SignalEmitter
    
try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

## Support for removable devices on Mac OSX

class OSXRemovableDrives(threading.Thread, SignalEmitter):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.start()

    drivesChanged = Signal()

    def run(self):
        while True:
            drives = {}
            p = subprocess.Popen(["system_profiler", "SPUSBDataType", "-xml"], stdout=subprocess.PIPE)
            xml = ElementTree.fromstring(p.communicate()[0])
            p.wait()

            xml = self._parseStupidPListXML(xml)
            for dev in self._findInTree(xml, "Mass Storage Device"):
                if "removable_media" in dev and dev["removable_media"] == "yes" and "volumes" in dev and len(dev["volumes"]) > 0:
                    for vol in dev["volumes"]:
                        if "mount_point" in vol:
                            volume = vol["mount_point"]
                            drives[os.path.basename(volume)] = volume

            p = subprocess.Popen(["system_profiler", "SPCardReaderDataType", "-xml"], stdout=subprocess.PIPE)
            xml = ElementTree.fromstring(p.communicate()[0])
            p.wait()

            xml = self._parseStupidPListXML(xml)
            for entry in xml:
                if "_items" in entry:
                    for item in entry["_items"]:
                        for dev in item["_items"]:
                            if "removable_media" in dev and dev["removable_media"] == "yes" and "volumes" in dev and len(dev["volumes"]) > 0:
                                for vol in dev["volumes"]:
                                    if "mount_point" in vol:
                                        volume = vol["mount_point"]
                                        drives[os.path.basename(volume)] = volume

            self.drivesChanged.emit(drives)
            time.sleep(5)

    def ejectDrive(self, drive):
        #TODO: Check if this needs drive name or mount point
        try:
            mount = self._drives[drive]
        except KeyError:
            return

        p = subprocess.Popen(["diskutil", "eject", mount], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()

        if p.wait():
            print(output[0])
            print(output[1])
            return False
        else:
            return True

    def _parseStupidPListXML(self, e):
        if e.tag == "plist":
            return self._parseStupidPListXML(list(e)[0])
        if e.tag == "array":
            ret = []
            for c in list(e):
                ret.append(self._parseStupidPListXML(c))
            return ret
        if e.tag == "dict":
            ret = {}
            key = None
            for c in list(e):
                if c.tag == "key":
                    key = c.text
                elif key is not None:
                    ret[key] = self._parseStupidPListXML(c)
                    key = None
            return ret
        if e.tag == "true":
            return True
        if e.tag == "false":
            return False
        return e.text
    
    def _findInTree(self, t, n):
        ret = []
        if type(t) is dict:
            if "_name" in t and t["_name"] == n:
                ret.append(t)
            for k, v in t.items():
                ret += self._findInTree(v, n)
        if type(t) is list:
            for v in t:
                ret += self._findInTree(v, n)
        return ret
