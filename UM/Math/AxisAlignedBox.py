from UM.Math.Vector import Vector

class AxisAlignedBox:
    def __init__(self, *args, **kwargs):
        super().__init__()

        self._rightTopFront = Vector()
        self._leftBottomBack = Vector()

        if len(args) == 3:
            self.setLeft(-args[0] / 2)
            self.setRight(args[0] / 2)

            self.setTop(args[1] / 2)
            self.setBottom(-args[1] / 2)

            self.setFront(args[2] / 2)
            self.setBack(-args[2] / 2)

        if 'rightTopFront' in kwargs:
            self._rightTopFront = kwargs['rightTopFront']

        if 'leftBottomBack' in kwargs:
            self._leftBottomBack = kwargs['leftBottomBack']

    @property
    def width(self):
        return self._rightTopFront.x - self._leftBottomBack.x

    @property
    def height(self):
        return self._rightTopFront.y - self._leftBottomBack.y

    @property
    def depth(self):
        return self._rightTopFront.z - self._leftBottomBack.z

    @property
    def center(self):
        return (self._rightTopFront - self._leftBottomBack) / 2.0

    @property
    def left(self):
        return self._leftBottomBack.x

    @property
    def right(self):
        return self._rightTopFront.x

    @property
    def top(self):
        return self._rightTopFront.y

    @property
    def bottom(self):
        return self._leftBottomBack.y

    @property
    def front(self):
        return self._rightTopFront.z

    @property
    def back(self):
        return self._leftBottomBack.z

    @property
    def rightTopFront(self):
        return self._rightTopFront

    @property
    def leftBottomBack(self):
        return self._leftBottomBack

    def transform(self, matrix):
        self._rightTopFront = self._rightTopFront.transformed(matrix)
        self._leftBottomBack = self._leftBottomBack.transformed(matrix)

    #def __add__(self, other):
        #b = AxisAlignedBox()
        #b += self
        #b += other
        #return b

    #def __iadd__(self, other):
        #self._dimensions += other._dimensions
        #self._center = self._dimensions / 2.0
        #return self

    #def __sub__(self, other):
        #b = AxisAlignedBox()
        #b += self
        #b -= other
        #return b

    #def __isub__(self, other):
        #self._dimensions -= other._dimensions
        #self._center = self._dimensions / 2.0
        #return self

    def __repr__(self):
        return "AxisAlignedBox(rightTopFront = {0}, leftBottomBack = {1})".format(self._rightTopFront, self._leftBottomBack)
