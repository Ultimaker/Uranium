# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import time  # For timing lock file
from typing import Any, Optional

from UM.Logger import Logger


##  Manage a lock file for reading / writing in a directory.
#   \param filename the filename to use as lock file
#   \param timeout in seconds; if the file is too old by this amount, then it gets ignored
#   \param wait_msg the message to log when waiting for the lock file to disappear
#
#   example usage:
#   $ with LockFile("my_lock_file.lock"):
#   $   <do something in a directory>
class LockFile:
    ##  Creates the locker instance that will hold the lock file.
    #
    #   \param filename The name and path of the lockfile to create.
    #   \param timeout After this amount of seconds, the lock will break
    #   regardless of the state of the file system.
    #   \param wait_msg A message to log when the thread is blocked by the lock.
    #   It is intended that you modify this to better indicate what lock file is
    #   blocking the thread.
    def __init__(self, filename: str, timeout: int = 10, wait_msg: str = "Waiting for lock file to disappear...") -> None:
        self._filename = filename
        self._wait_msg = wait_msg
        self._timeout = timeout
        self._pidfile = None #type: Optional[int]

    ##  Creates the lock file on the file system, with exclusive use.
    #
    #   If another thread wants to use a concurrent folder/file, but this file is still in use, then wait until the
    #   current thread releases the lock file.
    def _createLockFile(self) -> None:
        start_wait = time.time()
        while True:
            if time.time() - start_wait > self._timeout: #Timeout expired. Overwrite the lock file.
                try:
                    os.remove(self._filename)
                except:
                    pass
            open_flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            open_mode = 0o644
            try:
                self._pidfile = os.open(self._filename, open_flags, open_mode)
                break
            except:
                pass
            time.sleep(0.1)

    ##  Close and delete the lock file from the file system once the current thread finish what it was doing.
    def _deleteLockFile(self) -> None:
        try:
            if self._pidfile is None:
                Logger.log("e", "Could not determine process ID file.")
                return
            os.close(self._pidfile)
            os.remove(self._filename)
        except:
            Logger.log("e", "Could not delete lock file [%s]" % self._filename)

    ##  Attempt to grab the lock file for personal use.
    def __enter__(self) -> None:
        self._createLockFile()

    ##  Release the lock file so that other processes may use it.
    #
    #   \param exc_type The type of exception that was raised during the
    #   ``with`` block, if any. Use ``None`` if no exception was raised.
    #   \param exc_val The exception instance that was raised during the
    #   ``with`` block, if any. Use ``None`` if no exception was raised.
    #   \param exc_tb The traceback frames at the time the exception occurred,
    #   if any. Use ``None`` if no exception was raised.
    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Any) -> None: #exc_tb is actually a traceback object which is not exposed in Python.
        self._deleteLockFile()
