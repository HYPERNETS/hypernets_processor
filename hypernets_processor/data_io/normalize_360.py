# function to normalize angles between two limits
# adapted from https://gist.github.com/phn/1111712
def normalizedeg(num, lower=0.0, upper=360.0, b=False):
    """Normalize number to range [lower, upper) or [lower, upper].
    Parameters
    ----------
    num : float
        The number to be normalized.
    lower : float
        Lower limit of range. Default is 0.0.
    upper : float
        Upper limit of range. Default is 360.0.
    b : bool
        Type of normalization. See notes.
    Returns
    -------
    n : float
        A number in the range [lower, upper) or [lower, upper].
    Raises
    ------
    ValueError
      If lower >= upper.
    Notes
    -----
    If the keyword `b == False`, the default, then the normalization
    is done in the following way. Consider the numbers to be arranged
    in a circle, with the lower and upper marks sitting on top of each
    other. Moving past one limit, takes the number into the beginning
    of the other end. For example, if range is [0 - 360), then 361
    becomes 1. Negative numbers move from higher to lower
    numbers. So, -1 normalized to [0 - 360) becomes 359.
    If the keyword `b == True` then the given number is considered to
    "bounce" between the two limits. So, -91 normalized to [-90, 90],
    becomes -89, instead of 89. In this case the range is [lower,
    upper]. This code is based on the function `fmt_delta` of `TPM`.
    Range must be symmetric about 0 or lower == 0.
    """
    from math import floor, ceil
    # abs(num + upper) and abs(num - lower) are needed, instead of
    # abs(num), since the lower and upper limits need not be 0. We need
    # to add half size of the range, so that the final result is lower +
    # <value> or upper - <value>, respectively.
    res = num
    if not b:
        if lower >= upper:
            raise ValueError("Invalid lower and upper limits: (%s, %s)" %
                             (lower, upper))

        res = num
        if num > upper or num == lower:
            num = lower + abs(num + upper) % (abs(lower) + abs(upper))
        if num < lower or num == upper:
            num = upper - abs(num - lower) % (abs(lower) + abs(upper))

        res = lower if res == upper else num
    else:
        total_length = abs(lower) + abs(upper)
        if num < -total_length:
            num += ceil(num / (-2 * total_length)) * 2 * total_length
        if num > total_length:
            num -= floor(num / (2 * total_length)) * 2 * total_length
        if num > upper:
            num = total_length - num
        if num < lower:
            num = -total_length - num

        res = num * 1.0  # Make all numbers float, to be consistent

    return res