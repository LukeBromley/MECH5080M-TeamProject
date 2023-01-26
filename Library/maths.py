from math import sqrt
from typing import Union


class Vector:
    def __init__(self, i: float, j: float, k: float):
        self.i = i
        self.j = j
        self.k = k


class VisualPoint:
    def __init__(self, x: int, y: int, colour: tuple) -> None:
        """

        :param x: x coordinate of plotted point
        :param y: y coordinate of plotted point
        :param colour: colour of plotted point
        """
        self.x = x
        self.y = y
        self.colour = colour


def calculate_vector_magnitude(A: Vector):
    return sqrt(A.i**2 + A.j**2 + A.k**2)


def calculate_cross_product(A: Vector, B: Vector):
    return Vector(0, 0, A.i * B.j - A.j * B.i)


def clamp(n: Union[int, float], minn: Union[int, float], maxn: Union[int, float]) -> Union[int, float]:
    """

    Limit a value, n, between minimum and maximum
    :param n: value to be limited
    :param minn: min that n can be
    :param maxn: max that n can be
    :return: limited value
    """
    return max(min(maxn, n), minn)
