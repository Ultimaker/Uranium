# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Ray import Ray
from UM.Math.Vector import Vector

@profile
def intersects(box, ray):
    return box.intersectsRay(ray)

ray = Ray(Vector(10, 10, 10), Vector(-1, -1, -1))
box = AxisAlignedBox(10, 10, 10)

for i in range(100000):
    intersects(box, ray)
