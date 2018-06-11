# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import unittest
import os.path
import tempfile

from multiprocessing import Pool

from UM.SaveFile import SaveFile

write_count = 0

def write_dual(path):
    with SaveFile(path, "w") as f:
        f.write("test file")

class TestSaveFile(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()
        self._temp_dir = None

    def test_singleWrite(self):
        path = os.path.join(self._temp_dir.name, "single_write")
        with SaveFile(path, "w") as f:
            f.write("test file")

        with open(path, encoding = "utf-8") as f:
            self.assertEqual(f.readline(), "test file")

    def test_multiWrite(self):
        path = os.path.join(self._temp_dir.name, "dual_write")

        # Start two processes that try to write to the same file
        with Pool(processes = 2) as p:
            p.apply_async(write_dual, [path])
            p.apply(write_dual, [path])

        # Once done, there should be just one file
        self.assertEqual(len(os.listdir(self._temp_dir.name)), 1)

        # And file contents should be correct.
        with open(path, encoding = "utf-8") as f:
            data = f.read()
            self.assertEqual(len(data), 9)
            self.assertEqual(data, "test file")

if __name__ == "__main__":
    unittest.main()
