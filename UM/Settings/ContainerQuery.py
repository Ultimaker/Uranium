# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import re
from typing import Optional

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
    def __init__(self, registry, *, ignore_case = False, **kwargs):
        self._registry = registry

        self._ignore_case = ignore_case
        self._kwargs = kwargs

        self._result = None

    ##  Get the class of the containers that this query should find, if any.
    #
    #   If the query doesn't filter on container type, `None` is returned.
    def getContainerType(self) -> Optional[type]:
        return self._kwargs.get("container_type")

    ##  Retrieve the result of this query.
    #
    #   \return A list of containers matching this query, or None if the query was not executed.
    def getResult(self):
        return self._result

    ##  Check to see if this is a very simple query that looks up a single container by ID.
    #
    #   \return True if this query is case sensitive, has only 1 thing to search for and that thing is "id".
    def isIdOnly(self):
        return len(self._kwargs) == 1 and not self._ignore_case and "id" in self._kwargs

    ##  Check to see if any of the kwargs is a Dict, which is not hashable for query caching.
    #
    #   \return True if this query is hashable.
    def isHashable(self):
        for kwarg in self._kwargs.values():
            if isinstance(kwarg, dict):
                return False
        return True

    ##  Execute the actual query.
    #
    #   This will search the container metadata of the ContainerRegistry based
    #   on the arguments provided to this class' constructor. After it is done,
    #   the result can be retrieved with getResult().
    def execute(self, candidates = None):
        if candidates is None:
            candidates = list(self._registry.metadata.values())

        #Filter on all the key-word arguments.
        for key, value in self._kwargs.items():
            if isinstance(value, str):
                if ("*" or "|") in value:
                    key_filter = lambda candidate, key = key, value = value: self._matchRegExp(candidate, key, value)
                else:
                    key_filter = lambda candidate, key = key, value = value: self._matchString(candidate, key, value)
            else:
                key_filter = lambda candidate, key = key, value = value: self._matchType(candidate, key, value)
            candidates = filter(key_filter, candidates)

        #Execute all filters.
        self._result = list(candidates)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, ContainerQuery) and self.__key() == other.__key()

    ##  Human-readable string representation for debugging.
    def __str__(self):
        return str(self._kwargs)

    # protected:

    # Check to see if a container matches with a regular expression
    def _matchRegExp(self, metadata, property_name, value):
        if property_name not in metadata:
            return False
        value = re.escape(value) #Escape for regex patterns.
        value = "^" + value.replace("\\*", ".*").replace("\\(", "(").replace("\\)", ")").replace("\\|", "|") + "$" #Instead of (now escaped) asterisks, match on any string. Also add anchors for a complete match.
        if self._ignore_case:
            value_pattern = re.compile(value, re.IGNORECASE)
        else:
            value_pattern = re.compile(value)

        return value_pattern.match(str(metadata[property_name]))

    # Check to see if a container matches with a string
    def _matchString(self, metadata, property_name, value):
        if property_name not in metadata:
            return False
        value = self._maybeLowercase(value)
        return value == self._maybeLowercase(str(metadata[property_name]))

    # Check to see if a container matches with a specific typed property
    def _matchType(self, metadata, property_name, value):
        if property_name == "container_type":
            return issubclass(metadata.get(property_name), value) #Also allow subclasses.
        return value == metadata.get(property_name) #If the metadata entry doesn't exist, match on None.

    # Helper function to simplify ignore case handling
    def _maybeLowercase(self, value):
        if self._ignore_case:
            return value.lower()

        return value

    # Private helper function for __hash__ and __eq__
    def __key(self):
        return (type(self), self._ignore_case, tuple(self._kwargs.items()))
