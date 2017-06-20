# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.


##  Convert a value to a boolean
#
#   \param \type{bool|str|int} any value.
#   \return \type{bool}
def parseBool(value):
    return value in [True, "True", "true", "Yes", "yes", 1]


