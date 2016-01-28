# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

from UM.Settings.MachineManager import MachineManager

@pytest.fixture()
def machine_manager():
    return MachineManager("test")
