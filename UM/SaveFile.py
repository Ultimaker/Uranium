# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import tempfile
import os
import os.path
import sys
from typing import Union, IO
fsync = os.fsync
if sys.platform != "win32":
    import fcntl
    def lockFile(file):
        try:
            fcntl.flock(file, fcntl.LOCK_EX)
        except OSError:  # Some file systems don't support file locks.
            pass

    if hasattr(fcntl, 'F_FULLFSYNC'):
        def fsync(fd):
            # https://lists.apple.com/archives/darwin-dev/2005/Feb/msg00072.html
            # https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man2/fsync.2.html
            fcntl.fcntl(fd, fcntl.F_FULLFSYNC)

else:  # On Windows, flock doesn't exist so we disable it at risk of corruption when using multiple application instances.
    def lockFile(file): #pylint: disable=unused-argument
        pass


class SaveFile:
    """A class to handle atomic writes to a file.

    This class can be used to perform atomic writes to a file. Atomic writes ensure
    that the file contents are always correct and that concurrent writes do not
    end up writing to the same file at the same time.
    """

    # How many time so re-try saving this file when getting unknown exceptions.
    __max_retries = 10

    # Create a new SaveFile.
    #
    # \param path The path to write to.
    # \param mode The file mode to use. See open() for details.
    # \param encoding The encoding to use while writing the file. Defaults to UTF-8.
    # \param kwargs Keyword arguments passed on to open().
    def __init__(self, path: Union[str, IO[str]], mode: str, encoding: str = "utf-8", **kwargs) -> None:
        self._path = path
        self._mode = mode
        self._encoding = encoding
        self._open_kwargs = kwargs
        self._file = None
        self._temp_file = None

    def __enter__(self):
        # Create a temporary file that we can write to.
        self._temp_file = tempfile.NamedTemporaryFile(self._mode, dir = os.path.dirname(self._path), encoding = self._encoding, delete = False, **self._open_kwargs) #pylint: disable=bad-whitespace
        return self._temp_file

    def __exit__(self, exc_type, exc_value, traceback):
        self._temp_file.flush()
        fsync(self._temp_file.fileno())
        self._temp_file.close()

        self.__max_retries = 10
        while not self._file:
            # First, try to open the file we want to write to.
            try:
                self._file = open(self._path, self._mode, encoding = self._encoding, **self._open_kwargs)
            except PermissionError:
                self._file = None #Always retry.
            except Exception as e:
                if self.__max_retries <= 0:
                    raise e
                self.__max_retries -= 1

        while True:
            # Try to acquire a lock. This will block if the file was already locked by a different process.
            lockFile(self._file)

            # Once the lock is released it is possible the other instance already replaced the file we opened.
            # So try to open it again and check if we have the same file.
            # If we do, that means the file did not get replaced in the mean time and we properly acquired a lock on the right file.
            try:
                file_new = open(self._path, self._mode, encoding = self._encoding, **self._open_kwargs)
            except PermissionError:
                # This primarily happens on Windows where trying to open an opened file will raise a PermissionError.
                # We want to block on those, to simulate blocking writes.
                continue
            except Exception as e:
                #In other cases with unknown exceptions, don't try again indefinitely.
                if self.__max_retries <= 0:
                    raise e
                self.__max_retries -= 1
                continue

            if not self._file.closed and os.path.sameopenfile(self._file.fileno(), file_new.fileno()):
                file_new.close()

                # Close the actual file to release the file lock.
                # Note that this introduces a slight race condition where another process can lock the file
                # before this process can replace it.
                self._file.close()

                # Replace the existing file with the temporary file.
                # This operation is guaranteed to be atomic on Unix systems and should be atomic on Windows as well.
                # This way we can ensure we either have the old file or the new file.
                # Note that due to the above mentioned race condition, on Windows a PermissionError can be raised.
                # If that happens, the replace operation failed and we should try again.
                try:
                    os.replace(self._temp_file.name, self._path)
                except PermissionError:
                    continue
                except Exception as e:
                    if self.__max_retries <= 0:
                        raise e
                    self.__max_retries -= 1

                break
            else:
                # Otherwise, retry the entire procedure.
                self._file.close()
                self._file = file_new
