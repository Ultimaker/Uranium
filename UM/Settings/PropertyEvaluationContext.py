# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from collections import deque


##  Context for evaluating a property value
#   It contains:
#     1. a stack of containers during the evaluation in the function call stack fashion
#     2. a context dictionary which contains all the current context
#
class PropertyEvaluationContext:

    def __init__(self, source_stack = None):
        self._stack_of_containers = deque()
        if source_stack is not None:
            self._stack_of_containers.append(source_stack)
        self._context = {}

    @property
    def root_stack(self):
        if self._stack_of_containers:
            return self._stack_of_containers[0]

    @property
    def stack_of_containers(self):
        return self._stack_of_containers

    def pushContainer(self, container):
        self._stack_of_containers.append(container)

    def popContainer(self):
        return self._stack_of_containers.pop()

    @property
    def context(self):
        return self._context
