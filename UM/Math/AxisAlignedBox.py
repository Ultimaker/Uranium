from UM.Math.Vector import Vector
from UM.Math.Float import Float

import numpy

## Axis alligned bounding box. 
class AxisAlignedBox:
    class IntersectionResult:
        NoIntersection = 1
        PartialIntersection = 2
        FullIntersection = 3

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._min = Vector()
        self._max = Vector()

        if len(args) == 3:
            self.setLeft(-args[0] / 2)
            self.setRight(args[0] / 2)

            self.setTop(args[1] / 2)
            self.setBottom(-args[1] / 2)

            self.setBack(-args[2] / 2)
            self.setFront(args[2] / 2)

        if "minimum" in kwargs:
            self._min = kwargs["minimum"]

        if "maximum" in kwargs:
            self._max = kwargs["maximum"]

        self._ensureMinMax()

    def __add__(self, other):
        b = AxisAlignedBox()
        b += self
        b += other
        return b

    def __iadd__(self, other):
        if not other.isValid():
            return self

        newMin = Vector()
        newMin.setX(min(self._min.x, other.left))
        newMin.setY(min(self._min.y, other.bottom))
        newMin.setZ(min(self._min.z, other.back))

        newMax = Vector()
        newMax.setX(max(self._max.x, other.right))
        newMax.setY(max(self._max.y, other.top))
        newMax.setZ(max(self._max.z, other.front))

        self._min = newMin
        self._max = newMax

        return self

    #def __sub__(self, other):
        #b = AxisAlignedBox()
        #b += self
        #b -= other
        #return b

    #def __isub__(self, other):
        #self._dimensions -= other._dimensions
        #self._center = self._dimensions / 2.0
        #return self

    @property
    def width(self):
        return self._max.x - self._min.x

    @property
    def height(self):
        return self._max.y - self._min.y

    @property
    def depth(self):
        return self._max.z - self._min.z

    @property
    def center(self):
        return self._min + ((self._max - self._min) / 2.0)

    @property
    def left(self):
        return self._min.x

    def setLeft(self, value):
        self._min.setX(value)
        self._ensureMinMax()

    @property
    def right(self):
        return self._max.x

    def setRight(self, value):
        self._max.setX(value)
        self._ensureMinMax()

    @property
    def bottom(self):
        return self._min.y

    def setBottom(self, value):
        self._min.setY(value)
        self._ensureMinMax()

    @property
    def top(self):
        return self._max.y

    def setTop(self, value):
        self._max.setY(value)
        self._ensureMinMax()

    @property
    def back(self):
        return self._min.z

    def setBack(self, value):
        self._min.setZ(value)
        self._ensureMinMax()

    @property
    def front(self):
        return self._max.z

    def setFront(self, value):
        self._max.setZ(value)
        self._ensureMinMax()

    @property
    def minimum(self):
        return self._min

    def setMinimum(self, m):
        self._min = m
        self._ensureMinMax()

    @property
    def maximum(self):
        return self._max

    def setMaximum(self, m):
        self._max = m
        self._ensureMinMax()

    ##  Check if the bounding box is valid.
    #   Uses fuzzycompare to validate.
    #   \sa Float::fuzzyCompare()
    def isValid(self):
        return not(Float.fuzzyCompare(self._min.x, self._max.x) or
                   Float.fuzzyCompare(self._min.y, self._max.y) or
                   Float.fuzzyCompare(self._min.z, self._max.z))

    ##  Intersect the bounding box with a ray 
    #   \param ray \type{Ray}
    #   \sa Ray
    def intersectsRay(self, ray):
        inv = ray.inverseDirection

        t = numpy.empty((2,3), dtype=numpy.float32)
        t[0, 0] = inv.x * (self._min.x - ray.origin.x)
        t[0, 1] = inv.y * (self._min.y - ray.origin.y)
        t[0, 2] = inv.z * (self._min.z - ray.origin.z)
        t[1, 0] = inv.x * (self._max.x - ray.origin.x)
        t[1, 1] = inv.y * (self._max.y - ray.origin.y)
        t[1, 2] = inv.z * (self._max.z - ray.origin.z)

        tmin = numpy.min(t, axis=0)
        tmax = numpy.max(t, axis=0)

        largest_min = numpy.max(tmin)
        smallest_max = numpy.min(tmax)

        if smallest_max > largest_min:
            return (largest_min, smallest_max)
        else:
            return False

    ##  Check to see if this box intersects another box.
    #
    #   \param box \type{AxisAlignedBox} The box to check for intersection.
    #   \return \type{IntersectionResult} NoIntersection when no intersection occurs, PartialIntersection when partially intersected, FullIntersection when box is fully contained inside this box.
    def intersectsBox(self, box):
        if self._min.x > box._max.x or box._min.x > self._max.x:
            return self.IntersectionResult.NoIntersection

        if self._min.y > box._max.y or box._min.y > self._max.y:
            return self.IntersectionResult.NoIntersection

        if self._min.z > box._max.z or box._min.z > self._max.z:
            return self.IntersectionResult.NoIntersection

        if box._min >= self._min and box._max <= self._max:
            return self.IntersectionResult.FullIntersection

        return self.IntersectionResult.PartialIntersection

    ##  private:

    #   Ensure min contains the minimum values and max contains the maximum values
    def _ensureMinMax(self):
        if self._max.x < self._min.x:
            x = self._min.x
            self._min.setX(self._max.x)
            self._max.setX(x)

        if self._max.y < self._min.y:
            y = self._min.y
            self._min.setY(self._max.y)
            self._max.setY(y)

        if self._max.z < self._min.z:
            z = self._min.z
            self._min.setZ(self._max.z)
            self._max.setZ(z)

    def __repr__(self):
        return "AxisAlignedBox(min = {0}, max = {1})".format(self._min, self._max)
