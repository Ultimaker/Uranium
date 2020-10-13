# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import json
import time
import uuid
from collections import deque
from threading import RLock
from typing import Callable, cast, Dict, Set, Union, Optional, Any

from PyQt5.QtCore import QObject, QUrl, Qt, pyqtSignal, pyqtProperty
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from UM.Logger import Logger
from UM.TaskManagement.HttpRequestData import HttpRequestData
from UM.TaskManagement.HttpRequestScope import HttpRequestScope
from UM.TaskManagement.TaskManager import TaskManager


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

    internetReachableChanged = pyqtSignal(bool)

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "HttpRequestManager":
        if cls.__instance is None:
            cls.__instance = cls(*args, **kwargs)
        return cls.__instance

    def __init__(self, max_concurrent_requests: int = 4, parent: Optional["QObject"] = None,
                 enable_request_benchmarking: bool = False) -> None:
        if HttpRequestManager.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        HttpRequestManager.__instance = self

        super().__init__(parent)

        self._network_manager = QNetworkAccessManager(self)
        self._account_manager = None
        self._is_internet_reachable = True

        # All the requests that have been issued to the QNetworkManager are considered as running concurrently. This
        # number defines the max number of requests that will be issued to the QNetworkManager.
        self._max_concurrent_requests = max_concurrent_requests

        # A FIFO queue for the pending requests.
        self._request_queue = deque()  # type: deque

        # A set of all currently in progress requests
        self._requests_in_progress = set()  # type: Set[HttpRequestData]
        self._request_lock = RLock()
        self._process_requests_scheduled = False

        # Debug options
        #
        # Enabling benchmarking will make the manager to time how much time it takes for a request from start to finish
        # and log them.
        self._enable_request_benchmarking = enable_request_benchmarking

    @pyqtProperty(bool, notify = internetReachableChanged)
    def isInternetReachable(self) -> bool:
        return self._is_internet_reachable

    # Public API for creating an HTTP GET request.
    # Returns an HttpRequestData instance that represents this request.
    def get(self, url: str,
            headers_dict: Optional[Dict[str, str]] = None,
            callback: Optional[Callable[["QNetworkReply"], None]] = None,
            error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
            download_progress_callback: Optional[Callable[[int, int], None]] = None,
            upload_progress_callback: Optional[Callable[[int, int], None]] = None,
            timeout: Optional[float] = None,
            scope: Optional[HttpRequestScope] = None) -> "HttpRequestData":
        return self._createRequest("get", url, headers_dict = headers_dict,
                                   callback = callback, error_callback = error_callback,
                                   download_progress_callback = download_progress_callback,
                                   upload_progress_callback = upload_progress_callback,
                                   timeout = timeout,
                                   scope = scope)

    # Public API for creating an HTTP PUT request.
    # Returns an HttpRequestData instance that represents this request.
    def put(self, url: str,
            headers_dict: Optional[Dict[str, str]] = None,
            data: Optional[Union[bytes, bytearray]] = None,
            callback: Optional[Callable[["QNetworkReply"], None]] = None,
            error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
            download_progress_callback: Optional[Callable[[int, int], None]] = None,
            upload_progress_callback: Optional[Callable[[int, int], None]] = None,
            timeout: Optional[float] = None,
            scope: Optional[HttpRequestScope] = None) -> "HttpRequestData":
        return self._createRequest("put", url, headers_dict = headers_dict, data = data,
                                   callback = callback, error_callback = error_callback,
                                   download_progress_callback = download_progress_callback,
                                   upload_progress_callback = upload_progress_callback,
                                   timeout = timeout,
                                   scope = scope)

    # Public API for creating an HTTP POST request. Returns a unique request ID for this request.
    # Returns an HttpRequestData instance that represents this request.
    def post(self, url: str,
             headers_dict: Optional[Dict[str, str]] = None,
             data: Optional[Union[bytes, bytearray]] = None,
             callback: Optional[Callable[["QNetworkReply"], None]] = None,
             error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
             download_progress_callback: Optional[Callable[[int, int], None]] = None,
             upload_progress_callback: Optional[Callable[[int, int], None]] = None,
             timeout: Optional[float] = None,
             scope: Optional[HttpRequestScope] = None) -> "HttpRequestData":
        return self._createRequest("post", url, headers_dict = headers_dict, data = data,
                                   callback = callback, error_callback = error_callback,
                                   download_progress_callback = download_progress_callback,
                                   upload_progress_callback = upload_progress_callback,
                                   timeout = timeout,
                                   scope = scope)

    # Public API for creating an HTTP DELETE request.
    # Returns an HttpRequestData instance that represents this request.
    def delete(self, url: str,
               headers_dict: Optional[Dict[str, str]] = None,
               callback: Optional[Callable[["QNetworkReply"], None]] = None,
               error_callback: Optional[Callable[["QNetworkReply", "QNetworkReply.NetworkError"], None]] = None,
               download_progress_callback: Optional[Callable[[int, int], None]] = None,
               upload_progress_callback: Optional[Callable[[int, int], None]] = None,
               timeout: Optional[float] = None,
               scope: Optional[HttpRequestScope] = None) -> "HttpRequestData":
        return self._createRequest("deleteResource", url, headers_dict=headers_dict,
                                   callback=callback, error_callback=error_callback,
                                   download_progress_callback=download_progress_callback,
                                   upload_progress_callback=upload_progress_callback,
                                   timeout=timeout,
                                   scope=scope)

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

    @staticmethod
    def readJSON(reply: QNetworkReply) -> Any:
        """ Read a Json response into a Python object (list, dict, str depending on json type)

        :return: Python object representing the Json or None in case of error
        """
        try:
            return json.loads(HttpRequestManager.readText(reply))
        except json.decoder.JSONDecodeError:
            Logger.log("w", "Received invalid JSON: " + str(reply.url()))
            return None

    @staticmethod
    def readText(reply: QNetworkReply) -> str:
        """Decode raw reply bytes as utf-8"""
        return bytes(reply.readAll()).decode("utf-8")

    @staticmethod
    def replyIndicatesSuccess(reply: QNetworkReply, error: Optional["QNetworkReply.NetworkError"] = None) -> bool:
        """Returns whether reply status code indicates success and error is None"""
        return error is None and 200 <= reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) < 300

    @staticmethod
    def safeHttpStatus(reply: Optional[QNetworkReply]):
        """Returns the status code or -1 if there isn't any"""
        if reply is None:
            return -1

        return reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or -1

    @staticmethod
    def qt_network_error_name(error: QNetworkReply.NetworkError):
        """String representation of a NetworkError, eg 'ProtocolInvalidOperationError'"""

        for k, v in QNetworkReply.__dict__.items():
            if v == error:
                return k
        return "Unknown Qt Network error"

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
                       timeout: Optional[float] = None,
                       scope: Optional[HttpRequestScope] = None ) -> "HttpRequestData":
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

        if scope is not None:
            scope.requestHook(request)

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
            self._request_queue.append(request_data)

            # Schedule a call to process pending requests in the queue
            if not self._process_requests_scheduled:
                self.callLater(0, self._processNextRequestsInQueue)
                self._process_requests_scheduled = True

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
        # Process all requests until the max concurrent number is hit or there's no more requests to process.
        while True:
            with self._request_lock:
                # Do nothing if there's no more requests to process
                if not self._request_queue:
                    self._process_requests_scheduled = False
                    return

                # Do not exceed the max request limit
                if len(self._requests_in_progress) >= self._max_concurrent_requests:
                    self._process_requests_scheduled = False
                    return

                # Fetch the next request and process
                next_request_data = self._request_queue.popleft()
            self._processRequest(cast(HttpRequestData, next_request_data))

    # Processes the given HttpRequestData by issuing the request using QNetworkAccessManager and moves the
    # request into the currently in-progress list.
    def _processRequest(self, request_data: "HttpRequestData") -> None:
        now = time.time()

        # Get the right http_method function and prepare arguments.
        method = getattr(self._network_manager, request_data.http_method)
        args = [request_data.request]
        if request_data.data is not None:
            args.append(request_data.data)

        # Issue the request and add the reply into the currently in-progress requests set
        reply = method(*args)
        request_data.reply = reply

        # Connect callback signals
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

        if error == QNetworkReply.UnknownNetworkError or QNetworkReply.HostNotFoundError:
            self._setInternetReachable(False)
            # manager seems not always able to recover from a total loss of network access, so re-create it
            self._network_manager = QNetworkAccessManager(self)

        Logger.log("d", "%s got an error %s, %s", request_data, error, error_string)

        with self._request_lock:
            # Safeguard: make sure that we have the reply in the currently in-progress requests set
            if request_data not in self._requests_in_progress:
                # TODO: ERROR, should not happen
                Logger.log("e", "%s not found in the in-progress set", request_data)
                pass
            else:
                # Disconnect callback signals
                if request_data.reply is not None:
                    if request_data.download_progress_callback is not None:
                        request_data.reply.downloadProgress.disconnect(request_data.onDownloadProgressCallback)
                    if request_data.upload_progress_callback is not None:
                        request_data.reply.uploadProgress.disconnect(request_data.onUploadProgressCallback)

                    request_data.setDone()
                    self._requests_in_progress.remove(request_data)

        # Schedule the error callback if there is one
        if request_data.error_callback is not None:
            self.callLater(0, request_data.error_callback, request_data.reply, error)

        # Continue to process the next request
        self._processNextRequestsInQueue()

    def _onRequestFinished(self, request_data: "HttpRequestData") -> None:
        # See https://doc.qt.io/archives/qt-5.10/qnetworkreply.html#abort
        # Calling QNetworkReply.abort() will also trigger finished(), so we need to know if a request was finished or
        # aborted. This can be done by checking if the error is QNetworkReply.OperationCanceledError. If a request was
        # aborted due to timeout, the request's HttpRequestData.is_aborted_due_to_timeout will be set to True.
        #
        # We do nothing if the request was aborted or and error was detected because an error callback will also
        # be triggered by Qt.
        reply = request_data.reply
        if reply is not None:
            reply_error = reply.error()  # error() must only be called once
            if reply_error != QNetworkReply.NoError:
                if reply_error == QNetworkReply.OperationCanceledError:
                    Logger.log("d", "%s was aborted, do nothing", request_data)

                # stop processing for any kind of error
                return

        # No error? Internet is reachable
        self._setInternetReachable(True)

        if self._enable_request_benchmarking:
            time_spent = None  # type: Optional[float]
            if request_data.start_time is not None:
                time_spent = time.time() - request_data.start_time
            Logger.log("d", "Request [%s] finished, took %s seconds, pending for %s seconds",
                       request_data, time_spent, request_data.pending_time)

        with self._request_lock:
            # Safeguard: make sure that we have the reply in the currently in-progress requests set.
            if request_data not in self._requests_in_progress:
                # This can happen if a request has been aborted. The finished() signal will still be triggered at the
                # end. In this case, do nothing with this request.
                Logger.log("e", "%s not found in the in-progress set", request_data)
            else:
                # Disconnect callback signals
                if reply is not None:
                    # Even after the request was successfully finished, an error may still be emitted if
                    # the network connection is lost seconds later. Bug in Qt? Fixes CURA-7349
                    reply.error.disconnect()

                    if request_data.download_progress_callback is not None:
                        reply.downloadProgress.disconnect(request_data.onDownloadProgressCallback)
                    if request_data.upload_progress_callback is not None:
                        reply.uploadProgress.disconnect(request_data.onUploadProgressCallback)

                request_data.setDone()
                self._requests_in_progress.remove(request_data)

        # Schedule the callback if there is one
        if request_data.callback is not None:
            self.callLater(0, request_data.callback, reply)

        # Continue to process the next request
        self._processNextRequestsInQueue()

    def _setInternetReachable(self, reachable: bool):
        if reachable != self._is_internet_reachable:
            self._is_internet_reachable = reachable
            self.internetReachableChanged.emit(reachable)
