# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import tempfile
import os
import os.path
import sys

if sys.platform != "win32":
    import fcntl

    def lockFile(file):
        fcntl.flock(file, fcntl.LOCK_EX)
else:
    def lockFile(file):
        pass

##  A class to handle atomic writes to a file.
#
#   This class can be used to perform atomic writes to a file. Atomic writes ensure
#   that the file contents are always correct and that concurrent writes do not
#   end up writing to the same file at the same time.
class SaveFile:
    def __init__(self, path, mode, *args, **kwargs):
        self._path = path
        self._mode = mode
        self._open_args = args
        self._open_kwargs = kwargs

        self._temp_file = None

    def __enter__(self):
        # First, try to acquire a file lock on the file we want to write to.
        f = open(self._path, self._mode, *self._open_args, **self._open_kwargs)
        while True:
            # Try to acquire a lock. This will block if the file was already locked by a different process.
            lockFile(f)

            # Once the lock is released it is possible the other instance already replaced the file we opened.
            # So try to open it again and check if we have the same file.
            # If we do, that means the file did not get replaced in the mean time and we properly acquired a lock on the right file.
            fnew = open(self._path, self._mode, *self._open_args, **self._open_kwargs)
            if os.path.sameopenfile(f.fileno(), fnew.fileno()):
                fnew.close()
                break
            else:
                # Otherwise, retry the entire procedure.
                f.close()
                f = fnew

        # Remember the locked file.
        self._file = f
        # Create a temporary file that we can write to.
        self._temp_file = tempfile.NamedTemporaryFile(self._mode, dir = os.path.dirname(self._path), delete = False)
        return self._temp_file

    def __exit__(self, exc_type, exc_value, traceback):
        self._temp_file.close()

        # Close the actual file to release the file lock.
        # Note that this introduces a possible race condition where another process can lock the file
        # before this process can replace it.
        self._file.close()

        # Replace the existing file with the temporary file.
        # This operation is guaranteed to be atomic on Unix systems and should be atomic on Windows as well.
        # This way we can ensure we either have the old file or the new file.
        os.replace(self._temp_file.name, self._path)
