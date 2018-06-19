# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List

from UM.i18n import i18nCatalog


i18n_catalog = i18nCatalog("uranium")


class FileHandler:

    def __init__(self) -> None:
        super().__init__()
        self._supported_extensions = []  # type: List[str]

    @property
    def supported_extensions(self) -> List[str]:
        return self._supported_extensions

    def initialize(self) -> None:
        pass
