# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from collections import deque
from threading import RLock
import time
import uuid
from typing import Callable, Deque, Dict, Set, Union, Optional

from PyQt5.QtCore import QObject, QUrl, Qt, QTimer
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from UM.Logger import Logger


__all__ = ["HttpRequestData", "HttpRequestManager"]


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
class HttpRequestData:
    def __init__(self, request_id: str,
                 http_method: str, request: "QNetworkRequest",
                 data: Optional[Union[bytes, bytearray]] = None,
                 callback: Optional[Callable[["QNetworkReply"], None]] = None,
                 error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
                 download_progress_callback: Optional[Callable[[int, int], None]] = None,
                 upload_progress_callback: Optional[Callable[[int, int], None]] = None,
                 timeout: Optional[float] = None,
                 reply: Optional["QNetworkReply"] = None) -> None:
        self._request_id = request_id
        self.http_method = http_method.lower()
        self.request = request
        self.data = data
        self.callback = callback
        self.error_callback = error_callback
        self.download_progress_callback = download_progress_callback
        self.upload_progress_callback = upload_progress_callback
        self._timeout = timeout
        self.reply = reply

        # The timestamp when this request was initially issued to the QNetworkManager. This field to used to track and
        # manage timeouts (if set) for the requests.
        self._start_time = None  # type: Optional[float]
        self._timeout_time = None  # type: Optional[float]  # For convenience, = start_time + timeout
        self.is_aborted_due_to_timeout = False

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def timeout(self) -> Optional[float]:
        return self._timeout

    @property
    def timeout_time(self) -> Optional[float]:
        return self._timeout_time

    # Sets the start time of this request. This is called when this request is issued to the QNetworkManager.
    def setStartTime(self, start_time: float) -> None:
        self._start_time = start_time
        if self._timeout is not None:
            self._timeout_time = self._start_time + self._timeout

    # Checks with the given timestamp (in seconds) to see if this request has exceeded its timeout.
    # If no timeout is specified for this request, this check will return False.
    def hasExceededTimeout(self, now: float) -> bool:
        if self._timeout_time is None:
            return False
        return now > self._timeout_time

    def getTimeToTimeout(self, now: float) -> Optional[float]:
        if self._timeout_time is None:
            return None
        return self._timeout_time - now

    # Since Qt 5.12, pyqtSignal().connect() will return a Connection instance that represents a connection. This
    # Connection instance can later be used to disconnect for cleanup purpose. We are using Qt 5.10 and this feature
    # is not available yet, and I'm not sure if disconnecting a lambda can potentially cause issues. For this reason,
    # I'm using the following facade callback functions to handle the lambda function cases.
    def onCallback(self, reply: "QNetworkReply") -> None:
        if self.callback is not None:
            self.callback(reply)

    def onErrorCallback(self, reply: "QNetworkReply", error: "QNetworkReply.NetworkError") -> None:
        if self.error_callback is not None:
            self.error_callback(reply, error)

    def onDownloadProgressCallback(self, bytes_received: int, bytes_total: int) -> None:
        if self.download_progress_callback is not None:
            self.download_progress_callback(bytes_received, bytes_total)

    def onUploadProgressCallback(self, bytes_sent: int, bytes_total: int) -> None:
        if self.upload_progress_callback is not None:
            self.upload_progress_callback(bytes_sent, bytes_total)

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


#
# A dedicated manager that processes and schedules HTTP requests. It provides public APIs for issuing HTTP requests
# and the results, successful or not, will be communicated back via callback functions. For each request, 2 callback
# functions can be optionally specified:
#
#  - callback: This function will be invoked when a request finishes. (bound to QNetworkReply.finished signal)
#        Its signature should be "def callback(QNetworkReply) -> None" or other compatible form.
#
#  - error_callback: This function will be invoked when a request fails. (bound to QNetworkReply.error signal)
#        Its signature should be "def callback(QNetworkReply, QNetworkReply.NetworkError) -> None" or other compatible
#        form.
#
#  - download_progress_callback: This function will be invoked whenever the download progress changed. (bound to
#       QNetworkReply.downloadProgress signal)
#       Its signature should be "def callback(bytesReceived: int, bytesTotal: int) -> None" or other compatible form.
#
#  - upload_progress_callback: This function will be invoked whenever the upload progress changed. (bound to
#       QNetworkReply.downloadProgress signal)
#       Its signature should be "def callback(bytesSent: int, bytesTotal: int) -> None" or other compatible form.
#
#  - timeout (EXPERIMENTAL): The timeout is seconds for a request. This is the timeout since the request was first
#       issued to the QNetworkManager. NOTE that this timeout is NOT the timeout between each response from the other
#       party, but the timeout for the complete request. So, if you have a very slow network which takes 2 hours to
#       download a 1MB file, and for this request you set a timeout of 10 minutes, the request will be aborted after
#       10 minutes if it's not finished.
#
class HttpRequestManager(QObject):

    __instance = None  # type: Optional[HttpRequestManager]

    @classmethod
    def getInstance(cls, *args, **kwargs) -> Optional["HttpRequestManager"]:
        return cls.__instance

    def __init__(self, max_concurrent_requests: int = 10, parent: Optional["QObject"] = None) -> None:
        if HttpRequestManager.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        HttpRequestManager.__instance = self

        super().__init__(parent)

        from cura.CuraApplication import CuraApplication
        self._application = CuraApplication.getInstance()

        self._network_manager = QNetworkAccessManager(self)

        # Max number of concurrent requests that can be issued
        self._max_concurrent_requests = max_concurrent_requests

        # A FIFO queue for the pending requests.
        self._request_queue = deque()  # type: Deque[HttpRequestData]

        # A set of all currently in progress requests
        self._current_requests = set()  # type: Set[HttpRequestData]
        self._request_lock = RLock()
        self._process_requests_scheduled = False

        # Timer for managing timeouts.
        self._timeout_timer = QTimer(parent = self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._triggerTimeoutCheck)

    # Public API for creating an HTTP GET request.
    # Returns an HttpRequestData instance that represents this request.
    def get(self, url: str,
            headers_dict: Optional[Dict[str, str]] = None,
            callback: Optional[Callable[["QNetworkReply"], None]] = None,
            error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
            download_progress_callback: Optional[Callable[[int, int], None]] = None,
            upload_progress_callback: Optional[Callable[[int, int], None]] = None,
            timeout: Optional[float] = None) -> "HttpRequestData":
        return self._createRequest("get", url, headers_dict = headers_dict,
                                   callback = callback, error_callback = error_callback,
                                   download_progress_callback = download_progress_callback,
                                   upload_progress_callback = upload_progress_callback,
                                   timeout = timeout)

    # Public API for creating an HTTP PUT request.
    # Returns an HttpRequestData instance that represents this request.
    def put(self, url: str,
            headers_dict: Optional[Dict[str, str]] = None,
            data: Optional[Union[bytes, bytearray]] = None,
            callback: Optional[Callable[["QNetworkReply"], None]] = None,
            error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
            download_progress_callback: Optional[Callable[[int, int], None]] = None,
            upload_progress_callback: Optional[Callable[[int, int], None]] = None,
            timeout: Optional[float] = None) -> "HttpRequestData":
        return self._createRequest("put", url, headers_dict = headers_dict, data = data,
                                   callback = callback, error_callback = error_callback,
                                   download_progress_callback = download_progress_callback,
                                   upload_progress_callback = upload_progress_callback,
                                   timeout = timeout)

    # Public API for creating an HTTP POST request. Returns a unique request ID for this request.
    # Returns an HttpRequestData instance that represents this request.
    def post(self, url: str,
             headers_dict: Optional[Dict[str, str]] = None,
             data: Optional[Union[bytes, bytearray]] = None,
             callback: Optional[Callable[["QNetworkReply"], None]] = None,
             error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
             download_progress_callback: Optional[Callable[[int, int], None]] = None,
             upload_progress_callback: Optional[Callable[[int, int], None]] = None,
             timeout: Optional[float] = None) -> "HttpRequestData":
        return self._createRequest("post", url, headers_dict = headers_dict, data = data,
                                   callback = callback, error_callback = error_callback,
                                   download_progress_callback = download_progress_callback,
                                   upload_progress_callback = upload_progress_callback,
                                   timeout = timeout)

    # Public API for aborting a given HttpRequestData. If the request is not pending or in progress, nothing
    # will be done.
    def abortRequest(self, request: "HttpRequestData") -> None:
        with self._request_lock:
            # If the request is currently pending, just remove it from the pending queue.
            if request in self._request_queue:
                self._request_queue.remove(request)

            # If the request is currently in progress, abort it.
            if request in self._current_requests:
                if request.reply is not None and request.reply.isRunning():
                    request.reply.abort()
                    Logger.log("d", "%s aborted", request)

    # This function creates a HttpRequestData with the given data and puts it into the pending request queue.
    # If no request processing call has been scheduled, it will schedule it too.
    # Returns an HttpRequestData instance that represents this request.
    def _createRequest(self, http_method: str, url: str,
                       headers_dict: Optional[Dict[str, str]] = None,
                       data: Optional[Union[bytes, bytearray]] = None,
                       callback: Optional[Callable[["QNetworkReply"], None]] = None,
                       error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
                       download_progress_callback: Optional[Callable[[int, int], None]] = None,
                       upload_progress_callback: Optional[Callable[[int, int], None]] = None,
                       timeout: Optional[float] = None) -> "HttpRequestData":
        assert(timeout is None or timeout > 0)
        if timeout is not None and timeout <= 0:
            raise ValueError("Timeout must be a positive number if provided, but [%s] was given" % timeout)

        request = QNetworkRequest(QUrl(url))

        # Make sure that Qt handles redirects
        if hasattr(QNetworkRequest, "FollowRedirectsAttribute"):
            # Patch for Qt 5.6-5.8
            request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        if hasattr(QNetworkRequest, "RedirectPolicyAttribute"):
            # Patch for Qt 5.9+
            request.setAttribute(QNetworkRequest.RedirectPolicyAttribute, True)

        # Set headers
        if headers_dict is not None:
            for key, value in headers_dict.items():
                request.setRawHeader(key.encode("utf-8"), value.encode("utf-8"))

        # Generate a unique request ID
        request_id = uuid.uuid4().hex

        # Create the request data
        request_data = HttpRequestData(request_id,
                                       http_method = http_method,
                                       request = request,
                                       data = data,
                                       callback = callback,
                                       error_callback = error_callback,
                                       download_progress_callback = download_progress_callback,
                                       upload_progress_callback = upload_progress_callback,
                                       timeout = timeout)

        with self._request_lock:
            Logger.log("d", "%s has been queued", request_data)
            self._request_queue.append(request_data)

            # Schedule a call to process pending requests in the queue
            if not self._process_requests_scheduled:
                self._application.callLater(self._processRequestsInQueue)
                self._process_requests_scheduled = True
                Logger.log("d", "process requests call has been scheduled")

        return request_data

    # For easier debugging, so you know when the call is triggered by the timeout timer.
    def _triggerTimeoutCheck(self) -> None:
        Logger.log("d", "Timeout checkpoint triggered.")
        self._checkRequetsForTimeouts()

    def _checkRequetsForTimeouts(self) -> None:
        has_timeout_timer_rescheduled = False
        with self._request_lock:
            now = time.time()
            # Sort all currently in progress requests by their remaining times to timeout.
            #  - Abort the requests that have exceeded the timeout limit.
            #  - Schedule the timeout Timer to the next most recent timeout as a checkpoint.
            requests_with_timeout = filter(lambda r: r.timeout is not None, self._current_requests)
            sorted_requests = sorted(requests_with_timeout, key = lambda r: r.getTimeToTimeout(now))
            for request in sorted_requests:
                if request.hasExceededTimeout(now):
                    # Abort the requests that have exceeded the timeout limit.
                    if request.reply is not None and request.reply.isRunning():
                        request.reply.abort()
                        request.is_aborted_due_to_timeout = True
                        Logger.log("d", "%s aborted due to timeout [%s sec]", request, request.timeout)
                else:
                    # Schedule the timeout Timer to the next most recent timeout as a checkpoint.
                    seconds_to_timeout = request.getTimeToTimeout(now)
                    if seconds_to_timeout is not None:  # Make type checking happy
                        next_check_time = seconds_to_timeout + 0.5  # add a little margin
                        self._timeout_timer.stop()
                        self._timeout_timer.setInterval(next_check_time * 1000)
                        self._timeout_timer.start()
                        has_timeout_timer_rescheduled = True
                        Logger.log("d", "Timeout timer scheduled in [%s] sec for request", request)
                        break

        if not has_timeout_timer_rescheduled:
            self._timeout_timer.stop()

        Logger.log("d", "Timeout check done.")
        # We don't need to reschedule _processRequest() because abort() will trigger finished() which will
        # eventually try to schedule _processRequest().

    # Processes the next request in the pending queue. Stops if there is no more pending requests. It also stops if
    # the maximum number of concurrent requests has been reached.
    def _processRequestsInQueue(self) -> None:
        with self._request_lock:
            # do nothing if there's no more requests to process
            if not self._request_queue:
                self._process_requests_scheduled = False
                Logger.log("d", "No more requests to process, stop")
                return

            # do not exceed the max request limit
            if len(self._current_requests) >= self._max_concurrent_requests:
                self._process_requests_scheduled = False
                Logger.log("d", "The in-progress requests has reached the limit %s, stop",
                           self._max_concurrent_requests)
                return

            # fetch the next request and process
            next_request_data = self._request_queue.popleft()
        self._processRequest(next_request_data)

    # Processes the given HttpRequestData by issuing the request using QNetworkAccessManager and moves the
    # request into the currently in-progress list.
    def _processRequest(self, request_data: "HttpRequestData") -> None:
        now = time.time()
        Logger.log("d", "Start processing %s", request_data)

        # get the right http_method function and prepare arguments.
        method = getattr(self._network_manager, request_data.http_method)
        args = [request_data.request]
        if request_data.data is not None:
            args.append(request_data.data)

        # issue the request and add the reply into the currently in-progress requests set
        reply = method(*args)
        request_data.reply = reply

        # connect callback signals
        reply.error.connect(lambda err, rd = request_data: self._onRequestError(rd, err), type = Qt.QueuedConnection)
        reply.finished.connect(lambda rd = request_data: self._onRequestFinished(rd), type = Qt.QueuedConnection)
        if request_data.download_progress_callback is not None:
            reply.downloadProgress.connect(request_data.onDownloadProgressCallback, type = Qt.QueuedConnection)
        if request_data.upload_progress_callback is not None:
            reply.uploadProgress.connect(request_data.onUploadProgressCallback, type = Qt.QueuedConnection)

        with self._request_lock:
            self._current_requests.add(request_data)
            request_data.setStartTime(now)
            self._checkRequetsForTimeouts()

    def _onRequestError(self, request_data: "HttpRequestData", error: "QNetworkReply.NetworkError") -> None:
        error_string = None
        if request_data.reply is not None:
            error_string = request_data.reply.errorString()
        Logger.log("d", "%s got an error %s, %s", request_data, error, error_string)
        with self._request_lock:
            # safeguard: make sure that we have the reply in the currently in-progress requests set
            if request_data not in self._current_requests:
                # TODO: ERROR, should not happen
                Logger.log("e", "%s not found in the in-progress set", request_data)
                pass

            # disconnect callback signals
            if request_data.reply is not None:
                if request_data.download_progress_callback is not None:
                    request_data.reply.downloadProgress.disconnect(request_data.onDownloadProgressCallback)
                if request_data.upload_progress_callback is not None:
                    request_data.reply.uploadProgress.disconnect(request_data.onUploadProgressCallback)

            self._current_requests.remove(request_data)

        # schedule the error callback if there is one
        if request_data.error_callback is not None:
            Logger.log("d", "%s error callback scheduled", request_data)
            self._application.callLater(request_data.error_callback, request_data.reply, error)

        # continue to process the next request
        self._processRequestsInQueue()
        self._checkRequetsForTimeouts()  # TODO: optimize this

    def _onRequestFinished(self, request_data: "HttpRequestData") -> None:
        # See https://doc.qt.io/archives/qt-5.10/qnetworkreply.html#abort
        # Calling QNetworkReply.abort() will also trigger finished(), so we need to know if a request was finished or
        # aborted. This can be done by checking if the error is QNetworkReply.OperationCanceledError.
        #
        #  - Do nothing if the request was aborted by the user.
        #  - Call the timeout callback if the request was aborted due to timeout.
        if request_data.reply is not None and request_data.reply.error() == QNetworkReply.OperationCanceledError:
            Logger.log("d", "%s was aborted, do nothing", request_data)
            return

        Logger.log("d", "%s finished", request_data)
        with self._request_lock:
            # safeguard: ake sure that we have the reply in the currently in-progress requests set.
            if request_data not in self._current_requests:
                # This can happen if a request has been aborted. The finished() signal will still be triggered at the
                # end. In this case, do nothing with this request.
                Logger.log("e", "%s not found in the in-progress set", request_data)
            else:
                # disconnect callback signals
                if request_data.reply is not None:
                    if request_data.download_progress_callback is not None:
                        request_data.reply.downloadProgress.disconnect(request_data.onDownloadProgressCallback)
                    if request_data.upload_progress_callback is not None:
                        request_data.reply.uploadProgress.disconnect(request_data.onUploadProgressCallback)

                self._current_requests.remove(request_data)

        # schedule the callback if there is one
        if request_data.callback is not None:
            Logger.log("d", "%s callback scheduled", request_data)
            self._application.callLater(request_data.callback, request_data.reply)

        # continue to process the next request
        self._processRequestsInQueue()
        self._checkRequetsForTimeouts()  # TODO: optimize this
