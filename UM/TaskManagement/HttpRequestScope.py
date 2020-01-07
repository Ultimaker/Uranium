import platform
from typing import Dict

from PyQt5.QtNetwork import QNetworkRequest

from UM.Application import Application

from cura.API import CuraAPI, Account


# Modifies a request in some way. Could be used to add authorization headers, or set user agents, for example
class HttpRequestScope:
    ## Invoked after request-specific headers are set and before HttpRequestData is created
    def request_hook(self, request: QNetworkRequest):
        pass

    def add_headers(self, request: QNetworkRequest, header_dict: Dict):
        for key, value in header_dict.items():
            request.setRawHeader(key.encode("utf-8"), value.encode("utf-8"))


class DefaultUserAgentScope(HttpRequestScope):
    def __init__(self, application: Application):
        self.header_dict = {
            "User-Agent": "%s/%s (%s %s)" % (application.getApplicationName(),
                                             application.getVersion(),
                                             platform.system(),
                                             platform.machine())
        }

    def request_hook(self, request: QNetworkRequest):
        super().request_hook(request)
        self.add_headers(request, self.header_dict)


# Adds the default User Agent and an API-token
class UltimakerCloudScope(DefaultUserAgentScope):
    def __init__(self, application: Application):
        super().__init__(application)
        api = CuraAPI()
        self._account = api.account  # type: Account

    def request_hook(self, request: QNetworkRequest):
        super().request_hook(request)
        token = self._account.accessToken
        header_dict = {
            "Authorization": "Bearer {}".format(token)
        }
        self.add_headers(request, header_dict)

