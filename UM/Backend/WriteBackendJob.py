# Copyright (c) 2015 Ruben Dulek, Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Message import Message

import os.path

##  A Job subclass that writes backend output.
#
#   The result of this job is True if the write was successful or False when it
#   wasn't successful.
class WriteBackendJob(Job):
    ##  Creates a new WriteBackendJob.
    #
    #   No file name is initialised. This must be set using setFileName.
    #
    #   \param writer The output writer to write with.
    #   \param stream The stream to write to with the output writer.
    def __init__(self, writer, stream):
        super().__init__()
        self._stream = stream
        self._writer = writer
        self._file_name = ""

    def setFileName(self, name):
        self._file_name = name

    def getFileName(self):
        return self._file_name

    def getStream(self):
        return self._stream

    def run(self):
        Job.yieldThread()
        self.setResult(self._writer.write(self._stream))
