# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import collections  # To cache queries.
import re
from typing import Any, cast, Dict, List, Optional, Tuple, Type, TYPE_CHECKING
import functools

if TYPE_CHECKING:
    from UM.Settings.ContainerRegistry import ContainerRegistry

##  Wrapper class to perform a search for a certain set of containers.
#
#   This class is primarily intended to be used internally by
#   ContainerRegistry::findContainers. It is used to perform the actual
#   searching for containers and cache the results.
#
#   \note Instances of this class will ignore the query results when
#   comparing. This is done to simplify the caching code in ContainerRegistry.
class ContainerQuery:
    cache = {}  # type: Dict[Tuple[Any, ...], ContainerQuery]  # To speed things up, we're keeping a cache of the container queries we've executed before.

    # If a field is provided in the format "[t1|t2|t3|...]", try to find if any of the given tokens is present in the
    # value. Use regex to do matching because certain fields such as name can be filled by a user and it can be string
    # like "[my_printer][something]".
    OPTIONS_REGEX = re.compile("^\\[[a-zA-Z0-9-_\\+\\. ]+(\\|[a-zA-Z0-9-_\\+\\. ]+)*\\]$")

    ##  Constructor
    #
    #   \param registry The ContainerRegistry instance this query operates on.
    #   \param container_type A specific container class that should be filtered for.
    #   \param ignore_case Whether or not the query should be case sensitive.
    #   \param kwargs A dict of key, value pairs that should be searched for.
    def __init__(self, registry: "ContainerRegistry", *, ignore_case = False, **kwargs: Any) -> None:
        self._registry = registry

        self._ignore_case = ignore_case
        self._kwargs = kwargs

        self._result = None  # type: Optional[List[Dict[str, Any]]]

    ##  Get the class of the containers that this query should find, if any.
    #
    #   If the query doesn't filter on container type, `None` is returned.
    def getContainerType(self) -> Optional[type]:
        return self._kwargs.get("container_type")

    ##  Retrieve the result of this query.
    #
    #   \return A list of containers matching this query, or None if the query was not executed.
    def getResult(self) -> Optional[List[Dict[str, Any]]]:
        return self._result

    ##  Check to see if this is a very simple query that looks up a single container by ID.
    #
    #   \return True if this query is case sensitive, has only 1 thing to search for and that thing is "id".
    def isIdOnly(self) -> bool:
        return len(self._kwargs) == 1 and not self._ignore_case and "id" in self._kwargs

    ##  Execute the actual query.
    #
    #   This will search the container metadata of the ContainerRegistry based
    #   on the arguments provided to this class' constructor. After it is done,
    #   the result can be retrieved with getResult().
    def execute(self, candidates: Optional[List[Any]] = None) -> None:
        key_so_far = (self._ignore_case, )  # type: Tuple[Any, ...]
        if candidates is None:
            filtered_candidates = list(self._registry.metadata.values())
        else:
            filtered_candidates = candidates

        # Filter on all the key-word arguments.
        for key, value in self._kwargs.items():
            key_so_far += (key, value)
            if candidates is None and key_so_far in self.cache:
                filtered_candidates = cast(List[Dict[str, Any]], self.cache[key_so_far].getResult())
                continue

            if isinstance(value, type):
                key_filter = functools.partial(self._matchType, property_name = key, value = value)
            elif isinstance(value, str):
                if ContainerQuery.OPTIONS_REGEX.fullmatch(value) is not None:
                    # With [token1|token2|token3|...], we try to find if any of the given tokens is present in the value.
                    key_filter = functools.partial(self._matchRegMultipleTokens, property_name = key, value = value)
                elif ("*" or "|") in value:
                    key_filter = functools.partial(self._matchRegExp, property_name = key, value = value)
                else:
                    key_filter = functools.partial(self._matchString, property_name = key, value = value)
            else:
                key_filter = functools.partial(self._matchDirect, property_name = key, value = value)
            filtered_candidates = list(filter(key_filter, filtered_candidates))  # Execute this filter.

            if candidates is None:  # Only cache if we didn't pre-filter candidates.
                cached_arguments = dict(zip(key_so_far[1::2], key_so_far[2::2]))
                self.cache[key_so_far] = ContainerQuery(self._registry, ignore_case = self._ignore_case, **cached_arguments)  # Cache this query for the next time.
                self.cache[key_so_far]._result = filtered_candidates

        # Execute all filters.
        self._result = filtered_candidates

    ##  Human-readable string representation for debugging.
    def __str__(self):
        return str(self._kwargs)

    # protected:

    def _matchDirect(self, metadata: Dict[str, Any], property_name: str, value: str):
        if property_name not in metadata:
            return False

        return value == metadata[property_name]

    # Check to see if a container matches with a regular expression
    def _matchRegExp(self, metadata: Dict[str, Any], property_name: str, value: str):
        if property_name not in metadata:
            return False
        value = re.escape(value)  # Escape for regex patterns.
        value = "^" + value.replace("\\*", ".*").replace("\\(", "(").replace("\\)", ")").replace("\\|", "|") + "$" #Instead of (now escaped) asterisks, match on any string. Also add anchors for a complete match.
        if self._ignore_case:
            value_pattern = re.compile(value, re.IGNORECASE)
        else:
            value_pattern = re.compile(value)

        return value_pattern.match(str(metadata[property_name]))

    def _matchRegMultipleTokens(self, metadata: Dict[str, Any], property_name: str, value: str):
        if property_name not in metadata:
            return False

        # Use pattern /^(token1|token2|token3|...)$/ to look for any match of the given tokens
        value = "^" + value.replace("[", "(").replace("]", ")") + "$" #Match on any string and add anchors for a complete match.
        if self._ignore_case:
            value_pattern = re.compile(value, re.IGNORECASE)
        else:
            value_pattern = re.compile(value)

        return value_pattern.match(str(metadata[property_name]))

    # Check to see if a container matches with a string
    def _matchString(self, metadata: Dict[str, Any], property_name: str, value: str) -> bool:
        if property_name not in metadata:
            return False
        if self._ignore_case:
            return value.lower() == str(metadata[property_name]).lower()
        else:
            return value == str(metadata[property_name])

    # Check to see if a container matches with a specific typed property
    def _matchType(self, metadata: Dict[str, Any], property_name: str, value: Type):
        if property_name == "container_type":
            if "container_type" in metadata:
                try:
                    return issubclass(metadata["container_type"], value)  # Also allow subclasses.
                except TypeError:
                    # Since the type error that we got is extremely not helpful, we re-raise it with more info.
                    raise TypeError("The value {value} of the property {property} is not a type but a {type}: {metadata}"
                                    .format(value = value, property = property_name, type = type(value), metadata = metadata))
            else:
                return False

        if property_name not in metadata:
            return False

        return value == metadata[property_name]

    __slots__ = ("_ignore_case", "_kwargs", "_result", "_registry")

