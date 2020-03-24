# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional, List, Union
from urllib.parse import urlparse

from PyQt5.QtCore import pyqtSlot, QUrl, QObject
from PyQt5.QtGui import QDesktopServices

from UM.Logger import Logger


class UrlUtil(QObject):
    """
    Helper class used to open URLs from QML.
    """
    valid_uri_schemes = ["http", "https"]

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(str, list)
    def openUrl(self, target_url: str, schemes: List[str]) -> None:
        """
        Checks whether the target_url has an allowed scheme and, if it does, it opens the URL. If the target_url has a
        disallowed or invalid scheme, then it logs an error. This function can be called inside QML files.

        :param target_url: The URL string to be opened e.g. 'https://example.org'
        :param schemes: A list of the schemes that are allowed to be opened e.g. ['http', 'https']
        :return: None
        """
        allowed_schemes = set()
        for s in schemes:
            if s in self.valid_uri_schemes:
                allowed_schemes.add(s)
        parse_result = urlparse(target_url)
        if parse_result.scheme in allowed_schemes:
            QDesktopServices.openUrl(QUrl(target_url))
        else:
            Logger.log("e", "Attempted to open URL '{uri}'. The scheme '{scheme}' is not in the allowed schemes '"
                            "{allowed_schemes}'.".format(
                                                            uri = target_url,
                                                            scheme = parse_result.scheme,
                                                            allowed_schemes = allowed_schemes))


def createUrlUtil(engine: "QQmlEngine", script_engine: "QJSEngine") -> UrlUtil:
    """
    Function used by the Qt bindings to instantiate the UrlUtil class.
    """
    return UrlUtil()
