# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

warn = True

@pytest.hookimpl
def pytest_ignore_collect(path, config):
    if config.pluginmanager.hasplugin("pytest-benchmark"):
        return False
    else:
        global warn
        if warn:
            config.warn("", "Skipping benchmarks because pytest-benchmark plugin was not found.", "tests/benchmarks/conftest.py")
            warn = False

        return True
