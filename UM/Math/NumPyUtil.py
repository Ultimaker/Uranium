# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Union, List

import numpy
from copy import deepcopy


def immutableNDArray(nda: Union[List, numpy.array]) -> numpy.array:
    """Creates an immutable copy of the given narray

    If the array is already immutable then it just returns it.
    :param nda: :type{numpy.ndarray} the array to copy. May be a list
    :return: :type{numpy.ndarray} an immutable narray
    """

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
