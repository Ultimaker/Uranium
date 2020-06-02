# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Union


class Color:
    """An RGBA color value.

    This class represents an RGBA color value, in the range of 0.0 to 1.0.
    """

    def __init__(self, r: Union[int, float] = 0, g: Union[int, float] = 0, b: Union[int, float] = 0, a: Union[int, float] = 0) -> None:
        self._r = r if type(r) is float else r / 255    # type: float
        self._g = g if type(g) is float else g / 255    # type: float
        self._b = b if type(b) is float else b / 255    # type: float
        self._a = a if type(a) is float else a / 255    # type: float

    @property
    def r(self):
        return self._r

    def setR(self, value):
        self.setValues(value, self._g, self._b, self._a)

    @property
    def g(self):
        return self._g

    def setG(self, value):
        self.setValues(self._r, value, self._b, self._a)

    @property
    def b(self):
        return self._b

    def setB(self, value):
        self.setValues(self._r, self._g, value, self._a)

    @property
    def a(self):
        return self._a

    def setA(self, value):
        self.setValues(self._r, self._g, self._b, value)

    def setValues(self, r, g, b, a):
        self._r = r if type(r) is float else r / 255
        self._g = g if type(g) is float else g / 255
        self._b = b if type(b) is float else b / 255
        self._a = a if type(a) is float else a / 255

    def get32BitValue(self):
        return(
            (int(self._a * 255.) << 24) |
            (int(self._r * 255.) << 16) |
            (int(self._g * 255.) << 8) |
            int(self._b * 255.)
        )

    def __eq__(self, other):
        return self._r == other._r and self._g == other._g and self._b == other._b and self._a == other._a

    def __hash__(self):
        return (self._r, self._g, self._b, self._a).__hash__()

    def __repr__(self):
        return "Color(r = {0}, g = {1}, b = {2}, a = {3})".format(self._r, self._g, self._b, self._a)

    @staticmethod
    def fromARGB(value):
        """Returns a new Color constructed from a 32-bit integer in ARGB order.

        :param value: A 32-bit integer representing a color in ARGB order.
        :return: A Color constructed from the components of value.
        """

        return Color(
            (value & 0x00ff0000) >> 16,
            (value & 0x0000ff00) >> 8,
            (value & 0x000000ff) >> 0,
            (value & 0xff000000) >> 24
        )

    @staticmethod
    def fromARGBLowBits(value):
        return Color(
            (value & 0x000f0000) >> 16,
            (value & 0x00000f00) >> 8,
            (value & 0x0000000f) >> 0,
            (value & 0x0f000000) >> 24
        )

    @staticmethod
    def fromARGBHighBits(value):
        return Color(
            (value & 0x00f00000) >> 16,
            (value & 0x0000f000) >> 8,
            (value & 0x000000f0) >> 0,
            (value & 0xf0000000) >> 24
        )

    @staticmethod
    def dropLowBits(color):
        return Color.fromARGBHighBits(color.get32BitValue())

    @staticmethod
    def dropHightBits(color):
        return Color.fromARGBLowBits(color.get32BitValue())

    @staticmethod
    def fromHexString(value):
        """Returns a new Color constructed from a 7- or 9-character string "#RRGGBB" or "#AARRGGBB" format.

        :param value: A 7- or 9-character string representing a color in "#RRGGBB" or "#AARRGGBB" format.
        :return: A Color constructed from the components of value.
        """

        if len(value) == 9:
            return Color(
                int(value[3:5], 16) / 255,
                int(value[5:7], 16) / 255,
                int(value[7:9], 16) / 255,
                int(value[1:3], 16) / 255
            )
        else:
            return Color(
                int(value[1:3], 16) / 255,
                int(value[3:5], 16) / 255,
                int(value[5:7], 16) / 255,
                1.0
            )