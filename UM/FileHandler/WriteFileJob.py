# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Job import Job

from UM.Logger import Logger
from UM.FileHandler.FileWriter import FileWriter
from UM.Message import Message

import io
import time

from typing import Any, Optional, Union


class WriteFileJob(Job):
    """A Job subclass that performs writing.

    The writer defines what the result of this job is.
    """

    def __init__(self, writer: Optional[FileWriter], stream: Union[io.BytesIO, io.StringIO], data: Any, mode: int) -> None:
        """Creates a new job for writing.

        :param writer: The file writer to use, with the correct MIME type.
        :param stream: The output stream to write to.
        :param data: Whatever it is what we want to write.
        :param mode: Additional information to send to the writer, for example: such as whether to
        write in binary format or in ASCII format.
        """

        super().__init__()
        self._stream = stream
        self._writer = writer
        self._data = data
        self._file_name = ""
        self._mode = mode
        self._add_to_recent_files = False  # If this file should be added to the "recent files" list upon success
        self._message = None  # type: Optional[Message]
        self.progress.connect(self._onProgress)
        self.finished.connect(self._onFinished)

    def _onFinished(self, job: Job) -> None:
        if self == job and self._message is not None:
            self._message.hide()
            self._message = None

    def _onProgress(self, job: Job, amount: float) -> None:
        if self == job and self._message:
            self._message.setProgress(amount)

    def setFileName(self, name: str) -> None:
        self._file_name = name

    def getFileName(self) -> str:
        return self._file_name

    def getStream(self) -> Union[io.BytesIO, io.StringIO]:
        return self._stream

    def setMessage(self, message: Message) -> None:
        self._message = message

    def getMessage(self) -> Optional[Message]:
        return self._message

    def setAddToRecentFiles(self, value: bool) -> None:
        self._add_to_recent_files = value

    def getAddToRecentFiles(self) -> bool:
        return self._add_to_recent_files and (True if not self._writer else self._writer.getAddToRecentFiles())

    def run(self) -> None:
        Job.yieldThread()
        begin_time = time.time()
        self.setResult(None if not self._writer else self._writer.write(self._stream, self._data, self._mode))
        if not self.getResult():
            self.setError(Exception("No writer in WriteFileJob" if not self._writer else self._writer.getInformation()))
        end_time = time.time()
        Logger.log("d", "Writing file took %s seconds", end_time - begin_time)
