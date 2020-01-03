# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from collections import deque
from threading import RLock
import time
import uuid
from typing import Callable, Deque, Dict, Set, Union, Optional

from PyQt5.QtCore import QObject, QUrl, Qt, QTimer
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from UM.Logger import Logger

from .TaskManager import TaskManager


__all__ = ["HttpRequestData", "HttpRequestManager"]

#
# Summary:
#
# HttpRequestManager is a wrapper for Qt's QNetworkAccessManager and make it more convenient to do the following things:
#  (1) Keep track of the HTTP requests one has issued. This is done via the HttpRequestData object. Each HttpRequestData
#      object represents an issued HTTP request.
#  (2) A request can be aborted if it hasn't been issued to QNetworkAccessManager or if it's still running by
#      QNetworkAccessManager.
#  (3) Updates on each request is done via user-specified callback functions. So, for each request, you can give
#      optional callbacks:
#       - A successful callback, invoked when the request has been finished successfully.
#       - An error callback, invoked when an error has occurred, including when a request was aborted by the user or
#         timed out.
#       - A download progress callback, invoked when there's an update on the download progress.
#       - An upload progress callback, invoked when there's an update on the upload progress.
#  (4) An optional timeout can be specified for an HTTP request. Note that this timeout is the max wait time between
#      each time the request gets a response from the server. This is handled via the download and upload progress
#      callbacks. A QTimer is used for each request to track its timeout if set. If the timer gets triggered and there
#      is indeed a timeout, the request will be aborted. All requests that are aborted due to a timeout will result in
#      invoking its error callback with an error code QNetworkReply::OperationCanceledError, but the HttpRequestData
#      will have its "is_aborted_due_to_timeout" property set to True.
#     Because of
#
# All requests are handled by QNetworkAccessManager. We consider that all the requests that are being handled by
# QNetworkAccessManager at a certain point are running concurrently.
#


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

    # Sets the start time of this request. This is called when this request is issued to the QNetworkManager.
    def setStartTime(self, start_time: float) -> None:
        self._start_time = start_time

        # Prepare timeout handling
        if self._timeout is not None:
            self._last_response_time = start_time
            self._timeout_timer.start()
            Logger.log("d", "Request [%s] timeout timer started.", self)

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
            Logger.log("d", "Request [%s] download progress time last: [%s]", self, time_last)
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
            Logger.log("d", "Request [%s] upload progress, time last: [%s]", self, time_last)
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
class HttpRequestManager(TaskManager):

    __instance = None  # type: Optional[HttpRequestManager]

    @classmethod
    def getInstance(cls, *args, **kwargs) -> Optional["HttpRequestManager"]:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self, max_concurrent_requests: int = 10, parent: Optional["QObject"] = None) -> None:
        if HttpRequestManager.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        HttpRequestManager.__instance = self

        super().__init__(parent)

        self._network_manager = QNetworkAccessManager(self)

        # All the requests that have been issued to the QNetworkManager are considered as running concurrently. This
        # number defines the max number of requests that will be issued to the QNetworkManager.
        self._max_concurrent_requests = max_concurrent_requests

        # A FIFO queue for the pending requests.
        self._request_queue = deque()  # type: Deque[HttpRequestData]

        # A set of all currently in progress requests
        self._requests_in_progress = set()  # type: Set[HttpRequestData]
        self._request_lock = RLock()
        self._process_requests_scheduled = False

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
            if request in self._requests_in_progress:
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
        # Sanity checks
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
                                       manager_timeout_callback = self._onRequestTimeout,
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
                self.callLater(0, self._processNextRequestsInQueue)
                self._process_requests_scheduled = True
                Logger.log("d", "process requests call has been scheduled")

        return request_data

    # For easier debugging, so you know when the call is triggered by the timeout timer.
    def _onRequestTimeout(self, request_data: "HttpRequestData") -> None:
        Logger.log("d", "Request [%s] timeout.", self)

        # Make typing happy
        if request_data.reply is None:
            return

        with self._request_lock:
            if request_data not in self._requests_in_progress:
                return

            request_data.reply.abort()
            request_data.is_aborted_due_to_timeout = True

    # Processes the next requests in the pending queue. This function will issue as many requests to the QNetworkManager
    # as possible but limited by the value "_max_concurrent_requests". It stops if there is no more pending requests.
    def _processNextRequestsInQueue(self) -> None:
        with self._request_lock:
            # do nothing if there's no more requests to process
            if not self._request_queue:
                self._process_requests_scheduled = False
                Logger.log("d", "No more requests to process, stop")
                return

            # do not exceed the max request limit
            if len(self._requests_in_progress) >= self._max_concurrent_requests:
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

        # Only connect download/upload progress callbacks when necessary to reduce CPU usage.
        if request_data.download_progress_callback is not None or request_data.timeout is not None:
            reply.downloadProgress.connect(request_data.onDownloadProgressCallback, type = Qt.QueuedConnection)
        if request_data.upload_progress_callback is not None or request_data.timeout is not None:
            reply.uploadProgress.connect(request_data.onUploadProgressCallback, type = Qt.QueuedConnection)

        with self._request_lock:
            self._requests_in_progress.add(request_data)
            request_data.setStartTime(now)

    def _onRequestError(self, request_data: "HttpRequestData", error: "QNetworkReply.NetworkError") -> None:
        error_string = None
        if request_data.reply is not None:
            error_string = request_data.reply.errorString()
        Logger.log("d", "%s got an error %s, %s", request_data, error, error_string)

        with self._request_lock:
            # safeguard: make sure that we have the reply in the currently in-progress requests set
            if request_data not in self._requests_in_progress:
                # TODO: ERROR, should not happen
                Logger.log("e", "%s not found in the in-progress set", request_data)
                pass
            else:
                # disconnect callback signals
                if request_data.reply is not None:
                    if request_data.download_progress_callback is not None:
                        request_data.reply.downloadProgress.disconnect(request_data.onDownloadProgressCallback)
                    if request_data.upload_progress_callback is not None:
                        request_data.reply.uploadProgress.disconnect(request_data.onUploadProgressCallback)

                    request_data.setDone()
                    self._requests_in_progress.remove(request_data)

        # schedule the error callback if there is one
        if request_data.error_callback is not None:
            Logger.log("d", "%s error callback scheduled", request_data)
            self.callLater(0, request_data.error_callback, request_data.reply, error)

        # continue to process the next request
        self._processNextRequestsInQueue()

    def _onRequestFinished(self, request_data: "HttpRequestData") -> None:
        # See https://doc.qt.io/archives/qt-5.10/qnetworkreply.html#abort
        # Calling QNetworkReply.abort() will also trigger finished(), so we need to know if a request was finished or
        # aborted. This can be done by checking if the error is QNetworkReply.OperationCanceledError. If a request was
        # aborted due to timeout, the request's HttpRequestData.is_aborted_due_to_timeout will be set to True.
        #
        # We do nothing if the request was aborted because an error callback will also be triggered by Qt.
        if request_data.reply is not None and request_data.reply.error() == QNetworkReply.OperationCanceledError:
            Logger.log("d", "%s was aborted, do nothing", request_data)
            return

        Logger.log("d", "%s finished", request_data)
        with self._request_lock:
            # safeguard: make sure that we have the reply in the currently in-progress requests set.
            if request_data not in self._requests_in_progress:
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

                request_data.setDone()
                self._requests_in_progress.remove(request_data)

        # schedule the callback if there is one
        if request_data.callback is not None:
            Logger.log("d", "%s callback scheduled", request_data)
            self.callLater(0, request_data.callback, request_data.reply)

        # continue to process the next request
        self._processNextRequestsInQueue()
