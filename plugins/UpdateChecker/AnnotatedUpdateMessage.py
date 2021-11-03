# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional

from UM.Message import Message


class AnnotatedUpdateMessage(Message):

    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self.download_url: Optional[str] = None
        self.change_log_url: Optional[str] = None
        self._lifetime = 60
