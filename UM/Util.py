# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


def parseBool(value):
    """Convert a value to a boolean

    :param :type{bool|str|int} any value.
    :return: :type{bool}
    """

    return value in [True, "True", "true", "Yes", "yes", 1]


