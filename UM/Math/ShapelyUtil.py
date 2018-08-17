from typing import TYPE_CHECKING

import shapely.geometry

if TYPE_CHECKING:
    from UM.Math.Polygon import Polygon


#
# Converts a UM.Polygon into a shapely Polygon.
#
def polygon2ShapelyPolygon(polygon: "Polygon") -> shapely.geometry.Polygon:
    return shapely.geometry.Polygon([tuple(p) for p in polygon.getPoints()])
