import platform
from typing import Dict

from PyQt5.QtNetwork import QNetworkRequest

from UM.Application import Application


## Modifies a request in some way. This concept is sometimes called a request interceptor. Could be used to add
# authorization headers or set user agents, for example
class HttpRequestScope:
    ## Invoked after request-specific headers are set and before HttpRequestData is created
    def request_hook(self, request: QNetworkRequest):
        pass

    def add_headers(self, request: QNetworkRequest, header_dict: Dict):
        for key, value in header_dict.items():
            request.setRawHeader(key.encode("utf-8"), value.encode("utf-8"))


## Adds a User-Agent header
class DefaultUserAgentScope(HttpRequestScope):
    def __init__(self, application: Application) -> None:
        self.header_dict = {
            "User-Agent": "%s/%s (%s %s)" % (application.getApplicationName(),
                                             application.getVersion(),
                                             platform.system(),
                                             platform.machine())
        }

    def request_hook(self, request: QNetworkRequest):
        super().request_hook(request)
        self.add_headers(request, self.header_dict)
