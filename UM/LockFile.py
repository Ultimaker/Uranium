# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import time  # For timing lock file
from typing import Any, Optional

from UM.Logger import Logger
from UM.Platform import Platform


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
            if time.time() - start_wait > self._timeout: # Timeout expired. Overwrite the lock file.
                try:
                    os.remove(self._filename)
                except Exception as e:
                    try:
                        stats = os.stat(self._filename)
                    except:
                        stats = None
                    raise RuntimeError("Failed to remove lock file with stats = {stats}. Exception: {exception}".format(stats = stats, exception = e))
            open_flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            open_mode = 0o666
            try:
                self._pidfile = os.open(self._filename, open_flags, open_mode)
                break
            except:
                pass
            time.sleep(0.1)

    ##  Creates the lock file on Windows, with exclusive use and with the delete on close flag enabled so in case
    #   the process ends, the file will be automatically removed.
    #
    #   If another thread wants to use a concurrent folder/file, but this file is still in use, then wait until the
    #   current thread releases the lock file.
    def _createLockFileWindows(self) -> None:
        from ctypes import windll

        # Define attributes and flags for the file
        GENERIC_ALL = 0x10000000
        NO_SHARE = 0
        CREATE_NEW = 1
        FILE_FLAG_DELETE_ON_CLOSE = 0x04000000
        FILE_ATTRIBUTE_NORMAL = 0x80

        self._pidfile = None
        while True:
            try:
                # Try to create the lock file with the Windows API. For more information visit:
                # https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-createfilew
                self._pidfile = windll.kernel32.CreateFileW(self._filename, GENERIC_ALL, NO_SHARE, None, CREATE_NEW,
                                                            FILE_FLAG_DELETE_ON_CLOSE | FILE_ATTRIBUTE_NORMAL, None)
                if self._pidfile is not None and self._pidfile != -1: # -1 is the INVALID_HANDLE
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

    ##  Close and delete the lock file in Windows using the Windows API. For more info visit:
    #   https://msdn.microsoft.com/en-us/9b84891d-62ca-4ddc-97b7-c4c79482abd9
    def _deleteLockFileWindows(self) -> None:
        from ctypes import windll
        try:
            windll.kernel32.CloseHandle(self._pidfile)
        except:
            pass

    ##  Attempt to grab the lock file for personal use.
    def __enter__(self) -> None:
        if Platform.isWindows():
            self._createLockFileWindows()
        else:
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
        if Platform.isWindows():
            self._deleteLockFileWindows()
        else:
            self._deleteLockFile()
