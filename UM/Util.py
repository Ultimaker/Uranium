# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import time  # For timing lock file

from contextlib import contextmanager

from UM.Logger import Logger


##  Convert a value to a boolean
#
#   \param \type{bool|str|int} any value.
#   \return \type{bool}
def parseBool(value):
    return value in [True, "True", "true", "Yes", "yes", 1]


##  Manage a lock file for reading / writing in a directory.
#
#   example usage:
#   $ with LockFile("my_lock_file.lock").lockFile(timeout = 20):
#   $   <do something in a directory>
class LockFile(object):
    def __init__(self, filename, wait_msg="Waiting for lock file to disappear..."):
        self._filename = filename
        self._wait_msg = wait_msg

    ##  Wait for a lock file to disappear
    #   if the file is too old, it will be ignored too
    def waitLockFileDisappear(self, timeout = 10):
        now = time.time()
        # Allow max age of 10 seconds
        while os.path.exists(self._filename) and now < os.path.getmtime(self._filename) + timeout and now > os.path.getmtime(self._filename):
            Logger.log("d", self._wait_msg)
            time.sleep(1)
            now = time.time()

    def createLockFile(self):
        try:
            with open(self._filename, 'w') as lock_file:
                lock_file.write("%s" % os.getpid())
        except:
            Logger.log("e", "Could not create lock file [%s]" % self._filename)

    def deleteLockFile(self):
        try:
            if os.path.exists(self._filename):
                os.remove(self._filename)
        except:
            Logger.log("e", "Could not delete lock file [%s]" % self._filename)

    ##  Generator for lock file, you can use this function in your own context manager
    #   like so:  yield from lock_file.lockFileGenerator()
    def lockFileGenerator(self, timeout = 10):
        self.waitLockFileDisappear(timeout = timeout)
        self.createLockFile()
        yield
        self.deleteLockFile()

    ##  Contextmanager to create a lock file and remove it afterwards.
    @contextmanager
    def lockFile(self, timeout = 10):
        yield from self.lockFileGenerator(timeout = timeout)
