import time
from unittest import mock

from PyQt5.Qt import QCoreApplication, QNetworkReply

from UM.TaskManagement.HttpRequestManager import HttpRequestManager


#
# Test a GET request and it should succeed.
#
def test_getSuccessful() -> None:
    app = QCoreApplication([])
    http_request_manager = HttpRequestManager.getInstance()

    cbo = mock.Mock()

    def callback(*args, **kwargs):
        cbo.callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    request_data = http_request_manager.get(url = "http://localhost:8080/success", callback = callback)
    # Make sure that if something goes wrong, we quit after 10 seconds
    http_request_manager.callLater(10.0, app.quit)

    app.exec()
    http_request_manager.cleanup()  # Remove all unscheduled events

    cbo.callback.assert_called_once_with(request_data.reply)


#
# Test a GET request and it should fail with a 404 Page Not Found.
#
def test_getFail404() -> None:
    app = QCoreApplication([])
    http_request_manager = HttpRequestManager.getInstance()

    cbo = mock.Mock()

    def callback(*args, **kwargs):
        cbo.callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    def error_callback(*args, **kwargs):
        cbo.error_callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    request_data = http_request_manager.get(url = "http://localhost:8080/do_not_exist",
                                            callback = callback,
                                            error_callback = error_callback)
    # Make sure that if something goes wrong, we quit after 10 seconds
    http_request_manager.callLater(10.0, app.quit)

    app.exec()
    http_request_manager.cleanup()  # Remove all unscheduled events

    cbo.error_callback.assert_called_once_with(request_data.reply, QNetworkReply.ContentNotFoundError)
    cbo.callback.assert_not_called()


#
# Test a GET request and it should time out.
#
def test_getTimeout() -> None:
    app = QCoreApplication([])
    http_request_manager = HttpRequestManager.getInstance()

    cbo = mock.Mock()

    def error_callback(*args, **kwargs):
        cbo.error_callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    request_data = http_request_manager.get(url = "http://localhost:8080/timeout",
                                            error_callback = error_callback, timeout = 1)
    # Make sure that if something goes wrong, we quit after 10 seconds
    http_request_manager.callLater(10.0, app.quit)

    app.exec()
    http_request_manager.cleanup()  # Remove all unscheduled events

    cbo.error_callback.assert_called_once_with(request_data.reply, QNetworkReply.OperationCanceledError)
    assert request_data.is_aborted_due_to_timeout


#
# Test a GET request that requires Basic Auth to access. This test provides correct auth data and expects an HTTP
# 200 as a result.
#
def test_getBasicAuthSuccess() -> None:
    app = QCoreApplication([])
    http_request_manager = HttpRequestManager.getInstance()

    cbo = mock.Mock()

    def callback(*args, **kwargs):
        cbo.callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    def error_callback(*args, **kwargs):
        cbo.callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    request_data = http_request_manager.get(url="http://localhost:8080/auth",
                                            headers_dict = {"Authorization": "Basic dXNlcjp1c2Vy"},
                                            callback = callback,
                                            error_callback=error_callback)
    # Make sure that if something goes wrong, we quit after 10 seconds
    http_request_manager.callLater(10.0, app.quit)

    app.exec()
    http_request_manager.cleanup()  # Remove all unscheduled events

    cbo.callback.assert_called_once_with(request_data.reply)
    cbo.error_callback.assert_not_called()

#
# Test a GET request that requires Basic Auth to access. This test doesn't provide auth data and expects an HTTP
# 401 as a result.
#
def test_getBasicAuthFail() -> None:
    app = QCoreApplication([])
    http_request_manager = HttpRequestManager.getInstance()

    cbo = mock.Mock()

    def callback(*args, **kwargs):
        cbo.callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    def error_callback(*args, **kwargs):
        cbo.error_callback(*args, **kwargs)
        # quit now so we don't need to wait
        http_request_manager.callLater(0, app.quit)

    request_data = http_request_manager.get(url="http://localhost:8080/auth",
                                            callback=callback,
                                            error_callback = error_callback)
    # Make sure that if something goes wrong, we quit after 10 seconds
    http_request_manager.callLater(10.0, app.quit)

    app.exec()
    http_request_manager.cleanup()  # Remove all unscheduled events

    cbo.error_callback.assert_called_once_with(request_data.reply, request_data.reply.error())
    cbo.callback.assert_not_called()
