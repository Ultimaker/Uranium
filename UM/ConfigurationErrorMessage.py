# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import itertools
import sys
from typing import Iterable, Union, Optional

from PyQt5.QtWidgets import QMessageBox

from UM.i18n import i18nCatalog
from UM.Message import Message
from UM.Resources import Resources

i18n_catalog = i18nCatalog("uranium")


class ConfigurationErrorMessage(Message):
    """This is a specialised message that shows errors in the configuration.

    This class coalesces all errors in the configuration. Whenever there are new
    errors the message gets updated (and shown if it was hidden).
    """

    def __init__(self, application, *args, **kwargs):
        if ConfigurationErrorMessage.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        ConfigurationErrorMessage.__instance = self

        super().__init__(*args, **kwargs)
        self._application = application
        self._faulty_containers = set()

        self.addAction("reset", name = i18n_catalog.i18nc("@action:button", "Reset"), icon = None, description = "Reset your configuration to factory defaults.")
        self.actionTriggered.connect(self._actionTriggered)

    # Show more containers which we know are faulty.
    def addFaultyContainers(self, faulty_containers: Union[Iterable, str], *args):
        initial_length = len(self._faulty_containers)
        if isinstance(faulty_containers, str):
            faulty_containers = [faulty_containers]
        for container in itertools.chain(faulty_containers, args):
            self._faulty_containers.add(container)

        if initial_length != len(self._faulty_containers):
            self.setText(i18n_catalog.i18nc("@info:status", "Your configuration seems to be corrupt. Something seems to be wrong with the following profiles:\n- {profiles}\n Would you like to reset to factory defaults? Reset will remove all your current printers and profiles.").format(profiles = "\n- ".join(self._faulty_containers)))
            self.show()

    def _actionTriggered(self, _, action_id):
        if action_id == "reset":
            result = QMessageBox.question(None, i18n_catalog.i18nc("@title:window", "Reset to factory"),
                                          i18n_catalog.i18nc("@label",
                                                        "Reset will remove all your current printers and profiles! Are you sure you want to reset?"))
            if result == QMessageBox.Yes:
                Resources.factoryReset()
                sys.exit(1)

    __instance = None   # type: ConfigurationErrorMessage

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "ConfigurationErrorMessage":
        return cls.__instance
