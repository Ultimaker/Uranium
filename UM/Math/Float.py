
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
