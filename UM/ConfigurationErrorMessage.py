# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import itertools
import sys #For the exit() function.
from typing import Iterable, Union

from UM.i18n import i18nCatalog
from UM.Message import Message
from UM.Resources import Resources
import UM.Settings.ContainerRegistry

i18n_catalog = i18nCatalog("uranium")


##  This is a specialised message that shows errors in the configuration.
#
#   This class coalesces all errors in the configuration. Whenever there are new
#   errors the message gets updated (and shown if it was hidden).
class ConfigurationErrorMessage(Message):
    ##  This class is a singleton. You can't make it static since it needs to
    #   inherit from UM.Message.Message.
    _instance = None

    ##  Creates an instance of this object.
    #
    #   This initializer forces the Singleton pattern by checking if there is an
    #   instance first and giving an error if there is already an instance.
    def __init__(self, *args, **kwargs):
        assert self._instance is None and "Don't call the constructor of this Singleton! Use getInstance() instead."

        super().__init__(*args, **kwargs)
        self._faulty_containers = set()

        self.addAction("reset", name = i18n_catalog.i18nc("@action:button", "Reset"), icon = None, description = "Reset your configuration to factory defaults.")
        self.actionTriggered.connect(self._actionTriggered)

    ##  Show more containers which we know are faulty.
    def addFaultyContainers(self, faulty_containers: Union[Iterable, str], *args):
        initial_length = len(self._faulty_containers)
        if isinstance(faulty_containers, str):
            faulty_containers = [faulty_containers]
        for container in itertools.chain(faulty_containers, args):
            self._faulty_containers.add(container)
            UM.Settings.ContainerRegistry.ContainerRegistry.getInstance().removeContainer(container)

        if initial_length != len(self._faulty_containers):
            self.setText(i18n_catalog.i18nc("@info:status", "Your configuration seems to be corrupt. Something seems to be wrong with the following profiles:\n- {profiles}\nWould you like to reset to factory defaults?").format(profiles = "\n- ".join(self._faulty_containers)))
            self.show()

    ##  Creates an instance of this class if one doesn't exist yet.
    #
    #   If an instance does exist, this gets that instance.
    @classmethod
    def getInstance(cls) -> "ConfigurationErrorMessage":
        if cls._instance is None:
            cls._instance = ConfigurationErrorMessage(
                i18n_catalog.i18nc("@info:status", "Your configuration seems to be corrupt."),
                lifetime = 0,
                title = i18n_catalog.i18nc("@info:title", "Configuration errors")
            )
        return cls._instance

    def _actionTriggered(self, _, action_id):
        if action_id == "reset":
            Resources.factoryReset()
            sys.exit(1)