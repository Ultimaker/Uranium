# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


class Float:
    """Class containing helper functions for dealing with IEEE-754 floating point numbers."""

    @staticmethod
    def fuzzyCompare(f1: float, f2: float, tolerance: float = 1e-8) -> bool:
        """Compare two floats to check if they are equal with a tolerance value.

        This method will compare two floats and check whether they are equal to
        within a certain tolerance value.

        :param f1: :type{float} The first value to compare.
        :param f2: :type{float} The second value to compare.
        :param tolerance: The amount of tolerance used to consider the two numbers "equal".

        :return: True if the two numbers are considered equal, False if not.
        """

        if f1 == f2:
            return True

        return f1 > (f2 - tolerance) and f1 < (f2 + tolerance)

    @staticmethod
    def clamp(f1: float, minimum: float, maximum: float) -> float:
        """Return the value clamped to a minimum and maximum value.

        :param f1: :type{float} The value to clamp.
        :param minimum: :type{float} The minimum value.
        :param maximum: :type{float} The maximum value.

        :return: :type{float} Minimum if f1 < minimum, maximum if f1 > maximum, else f1.
        """

        return min(max(f1, minimum), maximum)
