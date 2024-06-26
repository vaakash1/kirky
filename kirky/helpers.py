from fractions import Fraction
from math import gcd as math_gcd


def common_denominator(fractions):
    denominators = [fraction.denominator for fraction in fractions]
    if len(denominators) > 1:
        divider = gcd(denominators[0], denominators[1])
        multiplier = denominators[1] / divider
        common_denominator = denominators[0] * multiplier
        if len(denominators) > 2:
            for denominator in denominators[2:]:
                divider = gcd(int(common_denominator), denominator)
                multiplier = denominator / divider
                common_denominator *= multiplier
        return common_denominator
    else:
        return denominators[0]

def gcd(a, b):
    return math_gcd(int(a), int(b))