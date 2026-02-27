"""Small integer math helpers for analysis formulas."""

from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction


def gcd(a: int, b: int) -> int:
    """Greatest common divisor using Euclid's algorithm."""
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Least common multiple with zero-safe behavior."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def lcm_many(values: Iterable[int]) -> int:
    """Least common multiple over a sequence of positive integers.

    Returns 0 for empty input.
    """
    result = 0
    for value in values:
        if result == 0:
            result = value
        else:
            result = lcm(result, value)
    return result


def ceil_fraction(value: Fraction) -> int:
    """Ceiling for exact rational values represented as `Fraction`."""
    return -(-value.numerator // value.denominator)


def fraction_to_str(value: Fraction) -> str:
    """Render a fraction exactly, using `a/b` or `a` if denominator is 1."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"
