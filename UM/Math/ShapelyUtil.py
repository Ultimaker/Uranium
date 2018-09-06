# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import TYPE_CHECKING

import shapely.geometry

if TYPE_CHECKING:
    from UM.Math.Polygon import Polygon


#
# Converts a UM.Polygon into a shapely Polygon.
#
def polygon2ShapelyPolygon(polygon: "Polygon") -> shapely.geometry.Polygon:
    return shapely.geometry.Polygon([tuple(p) for p in polygon.getPoints()])
