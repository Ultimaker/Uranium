from typing import TYPE_CHECKING

import shapely.geometry

if TYPE_CHECKING:
    from UM.Math.Polygon import Polygon


#
# Converts a UM.Polygon into a shapely Polygon.
#
def polygon2ShapelyPolygon(polygon: "Polygon") -> shapely.geometry.Polygon:
    xmin = min(p[0] for p in polygon.getPoints())
    xmax = max(p[0] for p in polygon.getPoints())
    ymin = min(p[1] for p in polygon.getPoints())
    ymax = max(p[1] for p in polygon.getPoints())

    return shapely.geometry.box(xmin, ymin, xmax, ymax)
    #return shapely.geometry.Polygon([tuple(p) for p in polygon.getPoints()])
