# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.


##  Class containing helper functions for dealing with IEEE-754 floating point numbers.
#
#
class Float:
    ##  Compare two floats to check if they are equal with a tolerance value.
    #
    #   This method will compare two floats and check whether they are equal to
    #   within a certain tolerance value.
    #
    #   \param f1 \type{float} The first value to compare.
    #   \param f2 \type{float} The second value to compare.
    #   \param tolerance \type{float} The amount of tolerance used to consider the two numbers "equal".
    #
    #   \return True if the two numbers are considered equal, False if not.
    @staticmethod
    def fuzzyCompare(f1, f2, tolerance = 1e-8):
        if f1 == f2:
            return True

        return f1 > (f2 - tolerance) and f1 < (f2 + tolerance)

    ##  Return the value clamped to a minimum and maximum value.
    #
    #   \param f1 \type{float} The value to clamp.
    #   \param minimum \type{float} The minimum value.
    #   \param maximum \type{float} The maximum value.
    #
    #   \return \type{float} Minimum if f1 < minimum, maximum if f1 > maximum, else f1.
    @staticmethod
    def clamp(f1, minimum, maximum):
        return min(max(f1, minimum), maximum)
