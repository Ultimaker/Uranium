# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Job import Job
import time
from UM.Logger import Logger


##  A Job subclass that performs writing.
#
#   The writer defines what the result of this job is.
class WriteFileJob(Job):
    ##  Creates a new job for writing.
    #
    #   \param writer The file writer to use, with the correct MIME type.
    #   \param stream The output stream to write to.
    #   \param data Whatever it is what we want to write.
    #   \param mode Additional information to send to the writer, for example: such as whether to
    #   write in binary format or in ASCII format.
    def __init__(self, writer, stream, data, mode):
        super().__init__()
        self._stream = stream
        self._writer = writer
        self._data = data
        self._file_name = ""
        self._mode = mode
        self._message = None
        self.progress.connect(self._onProgress)
        self.finished.connect(self._onFinished)

    def _onFinished(self, job):
        if self == job and self._message is not None:
            self._message.hide()
            self._message = None

    def _onProgress(self, job, amount):
        if self == job and self._message:
            self._message.setProgress(amount)

    def setFileName(self, name):
        self._file_name = name

    def getFileName(self):
        return self._file_name

    def getStream(self):
        return self._stream

    ##  Set the message associated with this job
    def setMessage(self, message):
        self._message = message

    def getMessage(self):
        return self._message

    def run(self):
        Job.yieldThread()
        begin_time = time.time()
        self.setResult(self._writer.write(self._stream, self._data, self._mode))
        end_time = time.time()
        Logger.log("d", "Writing file took %s seconds", end_time - begin_time)