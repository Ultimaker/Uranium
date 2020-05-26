from typing import Callable, Optional, Union, TYPE_CHECKING
from PyQt5.QtCore import QObject, QTimer

from UM.Logger import Logger

import time

if TYPE_CHECKING:
    from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply


#
# This is an internal data class which holds all data regarding a network request.
#  - request_id: A unique ID that's generated for each request.
#  - http_method: The HTTP method to use for this request, e.g. GET, PUT, POST, etc.
#  - request: The QNetworkRequest object that's created for this request
#  - data (optional): The data in binary form that needs to be sent.
#  - callback (optional): The callback function that will be triggered when the request is finished.
#  - error_callback (optional): The callback function for handling errors.
#  - download_progress_callback (optional): The callback function for handling download progress.
#  - upload_progress_callback (optional): The callback function for handling upload progress.
#  - timeout (optional): The timeout in seconds for this request. Must be a positive number if present.
#  - reply: The QNetworkReply for this request. It will only present after this request gets processed.
#
class HttpRequestData(QObject):

    # Add some tolerance for scheduling the QTimer to check for timeouts, because the QTimer may trigger the event a
    # little earlier. For example, with a 5000ms interval, the timer event can be triggered after 4752ms, so a request
    # may never timeout if we don't add some tolerance.
    # 4752ms (actual) and 5000ms (expected) has about 6% difference, so here I use 15% to be safer.
    TIMEOUT_CHECK_TOLERANCE = 0.15

    def __init__(self, request_id: str,
                 http_method: str, request: "QNetworkRequest",
                 manager_timeout_callback: Callable[["HttpRequestData"], None],
                 data: Optional[Union[bytes, bytearray]] = None,
                 callback: Optional[Callable[["QNetworkReply"], None]] = None,
                 error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
                 download_progress_callback: Optional[Callable[[int, int], None]] = None,
                 upload_progress_callback: Optional[Callable[[int, int], None]] = None,
                 timeout: Optional[float] = None,
                 reply: Optional["QNetworkReply"] = None,
                 parent: Optional["QObject"] = None) -> None:
        super().__init__(parent = parent)

        # Sanity checks
        if timeout is not None and timeout <= 0:
            raise ValueError("Timeout must be a positive value, but got [%s] instead." % timeout)

        self._request_id = request_id
        self.http_method = http_method
        self.request = request
        self.data = data
        self.callback = callback
        self.error_callback = error_callback
        self.download_progress_callback = download_progress_callback
        self.upload_progress_callback = upload_progress_callback
        self._timeout = timeout
        self.reply = reply

        # For benchmarking. For calculating the time a request spent pending.
        self._create_time = time.time()

        # The timestamp when this request was initially issued to the QNetworkManager. This field to used to track and
        # manage timeouts (if set) for the requests.
        self._start_time = None  # type: Optional[float]
        self.is_aborted_due_to_timeout = False

        self._last_response_time = float(0)
        self._timeout_timer = QTimer(parent = self)
        if self._timeout is not None:
            self._timeout_timer.setSingleShot(True)
            timeout_check_interval = self._timeout * 1000 * (1 + self.TIMEOUT_CHECK_TOLERANCE)
            self._timeout_timer.setInterval(timeout_check_interval)
            self._timeout_timer.timeout.connect(self._onTimeoutTimerTriggered)

        self._manager_timeout_callback = manager_timeout_callback

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def timeout(self) -> Optional[float]:
        return self._timeout

    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    # For benchmarking. Time in seconds that this request stayed in the pending queue.
    @property
    def pending_time(self) -> Optional[float]:
        if self._start_time is None:
            return None
        return self._start_time - self._create_time

    # Sets the start time of this request. This is called when this request is issued to the QNetworkManager.
    def setStartTime(self, start_time: float) -> None:
        self._start_time = start_time

        # Prepare timeout handling
        if self._timeout is not None:
            self._last_response_time = start_time
            self._timeout_timer.start()

    # Do some cleanup, such as stopping the timeout timer.
    def setDone(self) -> None:
        if self._timeout is not None:
            self._timeout_timer.stop()
            self._timeout_timer.timeout.disconnect(self._onTimeoutTimerTriggered)

    # Since Qt 5.12, pyqtSignal().connect() will return a Connection instance that represents a connection. This
    # Connection instance can later be used to disconnect for cleanup purpose. We are using Qt 5.10 and this feature
    # is not available yet, and I'm not sure if disconnecting a lambda can potentially cause issues. For this reason,
    # I'm using the following facade callback functions to handle the lambda function cases.

    def onDownloadProgressCallback(self, bytes_received: int, bytes_total: int) -> None:
        # Update info for timeout handling
        if self._timeout is not None:
            now = time.time()
            time_last = now - self._last_response_time
            self._last_response_time = time.time()
            # We've got a response, restart the timeout timer
            self._timeout_timer.start()

        if self.download_progress_callback is not None:
            self.download_progress_callback(bytes_received, bytes_total)

    def onUploadProgressCallback(self, bytes_sent: int, bytes_total: int) -> None:
        # Update info for timeout handling
        if self._timeout is not None:
            now = time.time()
            time_last = now - self._last_response_time
            self._last_response_time = time.time()
            # We've got a response, restart the timeout timer
            self._timeout_timer.start()

        if self.upload_progress_callback is not None:
            self.upload_progress_callback(bytes_sent, bytes_total)

    def _onTimeoutTimerTriggered(self) -> None:
        # Make typing happy
        if self._timeout is None:
            return
        if self.reply is None:
            return

        now = time.time()
        time_last = now - self._last_response_time
        if self.reply.isRunning() and time_last >= self._timeout:
            self._manager_timeout_callback(self)
        else:
            self._timeout_timer.start()

    def __str__(self) -> str:
        data = "no-data"
        if self.data:
            data = str(self.data[:10])
            if len(self.data) > 10:
                data += "..."

        return "request[{id}][{method}][{url}][timeout={timeout}][{data}]".format(id = self._request_id[:8],
                                                                                  method = self.http_method,
                                                                                  url = self.request.url(),
                                                                                  timeout = self._timeout,
                                                                                  data = data)
