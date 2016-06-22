# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  Helper functions for dealing with Python dictionaries.

##  Find the key corresponding to a certain value
#
#   \param dictionary \type{dict} The dictionary to search for the value
#   \param search_value The value to search for.
#
#   \return The key matching to value. Note that if the dictionary contains multiple instances of value it is undefined which exact key is returned.
#
#   \exception ValueError is raised when the value is not found in the dictionary.
def findKey(dictionary, search_value):
    for key, value in dictionary.items():
        if value == search_value:
            return key

    raise ValueError("Value {0} not found in dictionary".format(search_value))
