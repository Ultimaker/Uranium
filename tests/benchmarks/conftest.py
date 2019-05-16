# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest
import warnings

warn = True

@pytest.hookimpl
def pytest_ignore_collect(path, config):
    if config.pluginmanager.hasplugin("pytest-benchmark"):
        return False
    else:
        global warn
        if warn:
            warnings.warn(pytest.PytestWarning("Skipping benchmarks because pytest-benchmark plugin was not found."))
            warn = False

        return True
