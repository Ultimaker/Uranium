# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from collections import deque


class PropertyEvaluationContext:
    """Context for evaluating a property value

    It contains:
    1. a stack of containers during the evaluation in the function call stack fashion
    2. a context dictionary which contains all the current context
    """


    def __init__(self, source_stack = None):
        self.stack_of_containers = deque()
        if source_stack is not None:
            self.stack_of_containers.append(source_stack)
        self.context = {}

    def rootStack(self):
        if self.stack_of_containers:
            return self.stack_of_containers[0]

    def pushContainer(self, container):
        self.stack_of_containers.append(container)

    def popContainer(self) -> None:
        return self.stack_of_containers.pop()
