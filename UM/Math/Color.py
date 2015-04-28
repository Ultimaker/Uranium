

##  An RGBA color value.
#
#   This class represents an RGBA color value, in the range of 0.0 to 1.0.
class Color:
    def __init__(self, r = 0, g = 0, b = 0, a = 0):
        self._r = r if type(r) is float else r / 255
        self._g = g if type(g) is float else g / 255
        self._b = b if type(b) is float else b / 255
        self._a = a if type(a) is float else a / 255

    @property
    def r(self):
        return self._r

    @property
    def g(self):
        return self._g

    @property
    def b(self):
        return self._b

    @property
    def a(self):
        return self._a

    def setValues(self, r, g, b, a):
        self._r = r if type(r) is float else r / 255
        self._g = g if type(g) is float else g / 255
        self._b = b if type(b) is float else b / 255
        self._a = a if type(a) is float else a / 255

    def __eq__(self, other):
        return self._r == other._r and self._g == other._g and self._b == other._b and self._a == other._a

    def __hash__(self):
        return (self._r, self._g, self._b, self._a).__hash__()

    def __repr__(self):
        return "Color(r = {0}, g = {1}, b = {2}, a = {3})".format(self._r, self._g, self._b, self._a)

    ##  Returns a new Color constructed from a 32-bit integer in ARGB order.
    #
    #   \param value A 32-bit integer representing a color in ARGB order.
    #   \return A Color constructed from the components of value.
    @staticmethod
    def fromARGB(value):
        return Color(
            (value & 0x00ff0000) >> 16,
            (value & 0x0000ff00) >> 8,
            (value & 0x000000ff) >> 0,
            (value & 0xff000000) >> 24
        )
