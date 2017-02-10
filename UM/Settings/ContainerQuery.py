# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import re

from . import InstanceContainer

##  Wrapper class to perform a search for a certain set of containers.
#
#   This class is primarily intended to be used internally by
#   ContainerRegistry::findContainers. It is used to perform the actual
#   searching for containers and cache the results.
#
#   \note Instances of this class will ignore the query results when
#   comparing. This is done to simplify the caching code in ContainerRegistry.
class ContainerQuery:
    ##  Constructor
    #
    #   \param registry The ContainerRegistry instance this query operates on.
    #   \param container_type A specific container class that should be filtered for.
    #   \param ignore_case Whether or not the query should be case sensitive.
    #   \param kwargs A dict of key, value pairs that should be searched for.
    def __init__(self, registry, container_type = None, *, ignore_case = False, **kwargs):
        self._registry = registry

        self._container_type = container_type
        self._ignore_case = ignore_case
        self._kwargs = kwargs

        self._result = None

    ##  Retrieve the result of this query.
    #
    #   \return A list of containers matching this query, or None if the query was not executed.
    def getResult(self):
        return self._result

    ##  Check to see if this is a very simple query that looks up a single container by ID.
    #
    #   \return True if this query is case sensitive, has only 1 thing to search for and that thing is "id".
    def isIdOnly(self):
        return not self._ignore_case and len(self._kwargs) == 1 and "id" in self._kwargs

    ##  Execute the actual query.
    #
    #   This will search the containers of the ContainerRegistry based on the arguments provided to this
    #   class' constructor. After it is done, the result can be retrieved with getResult().
    def execute(self):
        containers = []
        for container in filter(lambda c: not self._container_type or isinstance(c, self._container_type), self._registry._containers):
            matches_container = True
            for key, value in self._kwargs.items():
                if isinstance(value, str):
                    if "*" in value:
                        matches_container = self._matchRegExp(container, key, value)
                    else:
                        matches_container = self._matchString(container, key, value)
                else:
                    matches_container = self._matchType(container, key, value)

                if not matches_container: # For the moment, a query needs to match all specified criteria
                    break

            if matches_container:
                containers.append(container)

        self._result = containers

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, ContainerQuery) and self.__key() == other.__key()

    # protected:

    # Check to see if a container matches with a regular expression
    def _matchRegExp(self, container, property_name, value):
        value = re.escape(value) #Escape for regex patterns.
        value = "^" + value.replace("\\*", ".*") + "$" #Instead of (now escaped) asterisks, match on any string. Also add anchors for a complete match.
        if self._ignore_case:
            value_pattern = re.compile(value, re.IGNORECASE)
        else:
            value_pattern = re.compile(value)

        if property_name == "id":
            return value_pattern.match(container.getId())
        elif property_name == "name":
            return value_pattern.match(container.getName())
        elif property_name == "definition":
            if isinstance(container, InstanceContainer.InstanceContainer):
                return container.getDefinition() and value_pattern.match(container.getDefinition().getId())

        return value_pattern.match(str(container.getMetaDataEntry(property_name)))

    # Check to see if a container matches with a string
    def _matchString(self, container, property_name, value):
        value = self._maybeLowercase(value)

        if property_name == "id":
            return value == self._maybeLowercase(container.getId())
        elif property_name == "name":
            return value == self._maybeLowercase(container.getName())
        elif property_name == "definition":
            if isinstance(container, InstanceContainer.InstanceContainer):
                return container.getDefinition() and value == container.getDefinition().getId()

        return value == self._maybeLowercase(str(container.getMetaDataEntry(property_name)))

    # Check to see if a container matches with a specific typed property
    def _matchType(self, container, property_name, value):
        if property_name == "id" or property_name == "name" or property_name == "definition":
            return False
        elif property_name == "read_only":
            if isinstance(container, InstanceContainer.InstanceContainer):
                return value == container.isReadOnly()
            else:
                return False

        return value == container.getMetaDataEntry(property_name)

    # Helper function to simplify ignore case handling
    def _maybeLowercase(self, value):
        if self._ignore_case:
            return value.lower()

        return value

    # Private helper function for __hash__ and __eq__
    def __key(self):
        return (type(self), self._container_type, self._ignore_case, tuple(self._kwargs.items()))
