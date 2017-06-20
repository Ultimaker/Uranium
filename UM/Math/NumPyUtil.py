# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import numpy
from copy import deepcopy

##  Creates an immutable copy of the given narray
#
#   If the array is already immutable then it just returns it.
#   \param nda \type{numpy.ndarray} the array to copy. May be a list
#   \return \type{numpy.ndarray} an immutable narray
def immutableNDArray(nda):
    if nda is None:
        return None

    if type(nda) is list:
        nda = numpy.array(nda, numpy.float32)
        nda.flags.writeable = False

    if not nda.flags.writeable:
        return nda
    copy = deepcopy(nda)
    copy.flags.writeable = False
    return copy
