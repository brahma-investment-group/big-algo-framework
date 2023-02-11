import math

def truncate(number, decimals=0):
    """ Returns a value truncated to a specific number of decimal places.
        Used to limit the number of digits when submitting orders etc.
        TD is specific about format of digits and IB may have restrictions on limit price digits."""
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor