# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

#pylint: disable=bad-whitespace

class ColorGenerator():
    """Very simple class filled with a bunch of colours that are chosen thusly that they are easily distinguishable
    for humans.
    """

    def __init__(self):
        self._rgb_color_list = [
            [   0, 255,   0], [   0,   0, 255], [ 255,   0,   0],
            [   1, 255, 254], [ 255, 166, 254], [ 255, 219, 102],
            [   0, 100,   1], [   1,   0, 103], [ 149,   0,  58],
            [   0, 125, 181], [ 255,   0, 246], [ 255, 238, 232],
            [ 119,  77,   0], [ 144, 251, 146], [   0, 118, 255],
            [ 213, 255,   0], [ 255, 147, 126], [ 106, 130, 108],
            [ 255,   2, 157], [ 254, 137,   0], [ 122,  71, 130],
            [ 126,  45, 210], [ 133, 169,   0], [ 255,   0,  86],
            [ 164,  36,   0], [   0, 174, 126], [ 104,  61,  59],
            [ 189, 198, 255], [  38,  52,   0], [ 189, 211, 147],
            [   0, 185,  23], [ 158,   0, 142], [   0,  21,  68],
            [ 194, 140, 159], [ 255, 116, 163], [   1, 208, 255],
            [   0,  71,  84], [ 229, 111, 254], [ 120, 130,  49],
            [  14,  76, 161], [ 145, 208, 203], [ 190, 153, 112],
            [ 150, 138, 232], [ 187, 136,   0], [  67,   0,  44],
            [ 222, 255, 116], [   0, 255, 198], [ 255, 229,   2],
            [  98,  14,   0], [   0, 143, 156], [ 152, 255,  82],
            [ 117,  68, 177], [ 181,   0, 255], [   0, 255, 120],
            [ 255, 110,  65], [   0,  95,  57], [ 107, 104, 130],
            [  95, 173,  78], [ 167,  87,  64], [ 165, 255, 210],
            [ 255, 177, 103], [   0, 155, 255], [ 232,  94, 190],
            [  50,  50,  50]
        ]
        self._color_list = [
            [  21./360., 1., 1.0 ], [  36./360., 1., 1.0], [  56./360., 1. , 1.  ],
            [ 117./360., 1., 0.8 ], [ 126./360., 1., 0.6], [ 179./360., 1. , 0.75],
            [ 235./360., 1., 0.54], [ 272./360., 1., 0.5], [ 287./360., 1.0, 0.8 ],
            [        0., 1., 0.8 ], [  12./360., 1., 1.0]
        ]

    def getColor(self, index):
        """Get a colour, based on index from the list

        :type index: int
        :returns: list with 3 integers
        """

        while index >= len(self._color_list):
            index -= len(self._color_list)
        return self._color_list[index]

    def getDistinctColor(self, index):
        while index >= len(self._rgb_color_list):
            index -= len(self._rgb_color_list)
        return self._rgb_color_list[index]
