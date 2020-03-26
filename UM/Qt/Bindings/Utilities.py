# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import List, TYPE_CHECKING
from urllib.parse import urlparse

from PyQt5.QtCore import pyqtSlot, QUrl, QObject
from PyQt5.QtGui import QDesktopServices

from UM.Logger import Logger

if TYPE_CHECKING:
    from PyQt5.QtQml import QQmlEngine, QJSEngine


class UrlUtil(QObject):
    """
    Helper class used to open URLs from QML.
    """
    __valid_uri_schemes = ("http", "https")  # Schemes considered valid to be used when calling the custom openUrl

    def __init__(self, parent = None):
        super().__init__(parent)

    @pyqtSlot(str, list, result = bool)
    def openUrl(self, target_url: str, allowed_schemes: List[str]) -> bool:
        """
        Opens the target_url if it has an allowed and valid scheme. This function can be called inside QML files.

        :param target_url: The URL string to be opened e.g. 'https://example.org'
        :param allowed_schemes: A list of the schemes that are allowed to be opened e.g. ['http', 'https']
        :return: True if the URL opens successfully, False if an invalid scheme is used
        """
        if self._urlHasValidScheme(target_url, allowed_schemes):
            QDesktopServices.openUrl(QUrl(target_url))
            return True
        return False

    def _urlHasValidScheme(self, url: str, input_schemes: List[str]) -> bool:
        """
        Checks if the scheme of the url is in the valid URL schemes and whether it has been allowed. If an invalid
        scheme was attempted to be allowed, the function logs a warning. If the url has a disallowed scheme, it logs an
        error.

        :param url: URL string to be checked
        :param input_schemes: A list of the schemes that are allowed to be opened e.g. ['http', 'https']
        :return: True if the URL has a scheme that is allowed and valid, False otherwise
        """
        allowed_schemes = set(self.__valid_uri_schemes) & set(input_schemes)
        if set(input_schemes) - allowed_schemes:
            Logger.log("w", "Attempted to allow invalid schemes {invalid}. Valid URL schemes that can be allowed "
                            "are {valid}.".format(
                                                invalid=set(input_schemes) - allowed_schemes,
                                                valid=self.__valid_uri_schemes)
                       )
        parse_result = urlparse(url)
        if parse_result.scheme in allowed_schemes:
            return True
        else:
            Logger.log("e", "Attempted to open URL '{uri}'. The scheme '{scheme}' is not in the allowed schemes "
                            "{allowed_schemes}.".format(
                                                        uri=url,
                                                        scheme=parse_result.scheme,
                                                        allowed_schemes=allowed_schemes)
                       )
            return False


def createUrlUtil(engine: "QQmlEngine", script_engine: "QJSEngine") -> UrlUtil:
    """
    Function used by the Qt bindings to instantiate the UrlUtil class.
    """
    return UrlUtil()
