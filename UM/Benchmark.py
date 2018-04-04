# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time
from UM.Logger import Logger
from UM.Application import Application

##  Static class used for benchmarking purposes. This class is only meant to be used as a static class.
class Benchmark:

    _start_time = None

    def __init__(self):
        raise Exception("This class is static only")

    @classmethod
    def start(cls, reference_text):
        Logger.log("d", "[BENCHMARK STARTS] %s", reference_text)
        Application.getInstance().callLater(cls._finished)
        cls._start_time = time.time()

    @classmethod
    def _finished(cls):
        Logger.log("d", "[BENCHMARK ENDS] Total time: %s", time.time() - cls._start_time)
