# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Optional


##  Convert a value to a boolean
#
#   \param \type{bool|str|int} any value.
#   \return \type{bool}
def parseBool(value) -> Any:
    return value in [True, "True", "true", "Yes", "yes", 1]


def findKeyInDict(dictionary: dict, search_value: Any) -> Optional[Any]:
    result = None
    for key, value in dictionary.items():
        if value == search_value:
            result = key
            break
    return result
