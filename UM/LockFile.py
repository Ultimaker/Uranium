# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import time  # For timing lock file

from UM.Logger import Logger


##  Manage a lock file for reading / writing in a directory.
#   \param filename the filename to use as lock file
#   \param timeout in seconds; if the file is too old by this amount, then it gets ignored
#   \param wait_msg the message to log when waiting for the lock file to disappear
#
#   example usage:
#   $ with LockFile("my_lock_file.lock"):
#   $   <do something in a directory>
class LockFile(object):
    def __init__(self, filename, timeout = 10, wait_msg = "Waiting for lock file to disappear..."):
        self._filename = filename
        self._wait_msg = wait_msg
        self._timeout = timeout

    def _waitLockFileDisappear(self):
        now = time.time()
        while os.path.exists(self._filename) and now < os.path.getmtime(self._filename) + self._timeout and now > os.path.getmtime(self._filename):
            Logger.log("d", self._wait_msg)
            time.sleep(1)
            now = time.time()

    def _createLockFile(self):
        try:
            with open(self._filename, 'w') as lock_file:
                lock_file.write("%s" % os.getpid())
        except:
            Logger.log("e", "Could not create lock file [%s]" % self._filename)

    def _deleteLockFile(self):
        try:
            if os.path.exists(self._filename):
                os.remove(self._filename)
        except:
            Logger.log("e", "Could not delete lock file [%s]" % self._filename)

    def __enter__(self):
        self._waitLockFileDisappear()
        self._createLockFile()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._deleteLockFile()
