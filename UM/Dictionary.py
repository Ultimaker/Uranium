# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Dict, Any

"""Helper functions for dealing with Python dictionaries."""


def findKey(dictionary: Dict[Any, Any], search_value: Any) -> Any:
    """Find the key corresponding to a certain value

    :param dictionary: :type{dict} The dictionary to search for the value
    :param search_value: The value to search for.

    :return: The key matching to value. Note that if the dictionary contains multiple instances of value it is undefined which exact key is returned.

    :exception ValueError: is raised when the value is not found in the dictionary.
    """

    for key, value in dictionary.items():
        if value == search_value:
            return key

    raise ValueError("Value {0} not found in dictionary".format(search_value))
