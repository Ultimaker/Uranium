from numpy import AxesType, ndarray
from typing import (Any, Union)

# FIXME: This definition is incomplete and doesn't represent the full range of the norm() function.
def norm(vector: ndarray[Any], ord: Union[int,float,str,None]=None, axis: AxesType=None) -> float: ...
