# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import time  # For timing lock file
from typing import Any, Optional

from UM.Logger import Logger
from UM.Platform import Platform


class LockFile:
    """Manage a lock file for reading / writing in a directory.

    example usage::

    $ with LockFile("my_lock_file.lock"):
    $   <do something in a directory>
    """

    def __init__(self, filename: str, timeout: int = 10, wait_msg: str = "Waiting for lock file to disappear...") -> None:
        """Creates the locker instance that will hold the lock file.

        :param filename: The name and path of the lockfile to create.
        :param timeout: After this amount of seconds, the lock will break
        regardless of the state of the file system.
        :param wait_msg: A message to log when the thread is blocked by the lock.
        It is intended that you modify this to better indicate what lock file is
        blocking the thread.
        """

        self._filename = filename
        self._wait_msg = wait_msg
        self._timeout = timeout
        self._pidfile = None #type: Optional[int]

    def _createLockFile(self) -> None:
        """Creates the lock file on the file system, with exclusive use.

        If another thread wants to use a concurrent folder/file, but this file is still in use, then wait until the
        current thread releases the lock file.
        """

        start_wait = time.time()
        while True:
            if time.time() - start_wait > self._timeout:  # Timeout expired. Overwrite the lock file.
                try:
                    os.remove(self._filename)
                except FileNotFoundError:
                    pass  # In case the file is simply not found, continue as normal.
                except OSError:
                    pass  # Can happen if the file system is dismounted or permissions have been changed during the runtime, etc.
                except Exception as e:
                    stats = None
                    try:
                        stats = os.stat(self._filename)
                    except:
                        pass
                    raise RuntimeError("Failed to remove lock file with stats = {stats}. Exception: {exception}".format(stats = stats, exception = e))
            open_flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            open_mode = 0o666
            try:
                self._pidfile = os.open(self._filename, open_flags, open_mode)
                break
            except:
                pass
            time.sleep(0.1)

    def _createLockFileWindows(self) -> None:
        """Creates the lock file on Windows, with exclusive use and with the delete on close flag enabled so in case
        the process ends, the file will be automatically removed.

        If another thread wants to use a concurrent folder/file, but this file is still in use, then wait until the
        current thread releases the lock file.
        """

        from ctypes import windll  # type: ignore
        start_wait = time.time()
        # Define attributes and flags for the file
        GENERIC_READ_WRITE = 0x40000000 | 0x80000000 #Read and write rights.
        NO_SHARE = 0
        CREATE_NEW = 1 #Only create the file if it doesn't already exist.
        FILE_FLAG_DELETE_ON_CLOSE = 0x04000000 #Delete the file when we close the file handle.
        FILE_ATTRIBUTE_NORMAL = 0x80 #Default auxiliary flags.

        self._pidfile = None
        while True:
            if time.time() - start_wait > self._timeout:  # Timeout expired. Overwrite the lock file.
                self._deleteLockFileWindows()
            try:
                # Try to create the lock file with the Windows API. For more information visit:
                # https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-createfilew
                self._pidfile = windll.kernel32.CreateFileW(self._filename, GENERIC_READ_WRITE, NO_SHARE, None, CREATE_NEW,
                                                            FILE_FLAG_DELETE_ON_CLOSE | FILE_ATTRIBUTE_NORMAL, None)
                if self._pidfile is not None and self._pidfile != -1: # -1 is the INVALID_HANDLE
                    break
            except Exception:
                Logger.logException("w", "An exception occured while attempting to create the lock file.")
            time.sleep(0.1)

    def _deleteLockFile(self) -> None:
        """Close and delete the lock file from the file system once the current thread finish what it was doing."""

        try:
            if self._pidfile is None:
                Logger.log("e", "Could not determine process ID file.")
                return
            os.close(self._pidfile)
            os.remove(self._filename)
        except:
            Logger.log("e", "Could not delete lock file [%s]" % self._filename)

    def _deleteLockFileWindows(self) -> None:
        """Close and delete the lock file in Windows using the Windows API. For more info visit:
        https://msdn.microsoft.com/en-us/9b84891d-62ca-4ddc-97b7-c4c79482abd9
        """

        from ctypes import windll  # type: ignore
        try:
            windll.kernel32.CloseHandle(self._pidfile)
        except Exception:
            Logger.logException("w", "Failed to remove the lockfile [%s]", self._filename)

    def __enter__(self) -> None:
        """Attempt to grab the lock file for personal use."""

        if Platform.isWindows():
            self._createLockFileWindows()
        else:
            self._createLockFile()

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Any) -> None: #exc_tb is actually a traceback object which is not exposed in Python.
        """Release the lock file so that other processes may use it.

        :param exc_type: The type of exception that was raised during the
            ``with`` block, if any. Use ``None`` if no exception was raised.
        :param exc_val: The exception instance that was raised during the
            ``with`` block, if any. Use ``None`` if no exception was raised.
        :param exc_tb: The traceback frames at the time the exception occurred,
            if any. Use ``None`` if no exception was raised.
        """

        if Platform.isWindows():
            self._deleteLockFileWindows()
        else:
            self._deleteLockFile()
